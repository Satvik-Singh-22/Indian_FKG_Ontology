"""
Ingredient deduplication using rapidfuzz tiered normalization.

Tiers:
  - Tier 1 (≥ 92% similarity): auto-merge silently
  - Tier 2 (80–92%): write to CSV for human review
  - < 80%: keep as separate ingredients

Usage:
    # Step 1: generate review CSV + apply auto-merges
    python -m pipeline.dedup_ingredients

    # Step 2: edit pipeline/output/dedup_review.csv (set 'action' column)
    # Step 3: apply reviewed merges
    python -m pipeline.dedup_ingredients --apply-review
"""

import argparse
import csv
import json
from pathlib import Path
from collections import defaultdict

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SKOS

from rapidfuzz import fuzz, process

from pipeline.config import FKG, HEALS, HEALS_ING, OUTPUT_TTL, STATE_DIR


# ── Thresholds ────────────────────────────────────────────────────────
AUTO_MERGE_THRESHOLD = 96   # Tier 1: auto-merge (raised from 92 to avoid false positives)
REVIEW_THRESHOLD     = 80   # Tier 2: generate CSV review

REVIEW_CSV = Path(OUTPUT_TTL).parent / "dedup_review.csv"
MERGE_LOG  = Path(OUTPUT_TTL).parent / "dedup_merge_log.json"


def _extract_ingredients(g: Graph) -> dict[str, str]:
    """Extract {label: uri_str} for all ingredients in the graph."""
    ingredients = {}
    for subj in g.subjects(RDF.type, HEALS_ING.Ingredient):
        for label in g.objects(subj, RDFS.label):
            ingredients[str(label)] = str(subj)
    return ingredients


def _pick_canonical(names: list[str]) -> str:
    """Pick the most descriptive name (longest) as canonical."""
    return max(names, key=len)


def _build_clusters(ingredients: dict[str, str],
                    threshold: int) -> list[list[str]]:
    """
    Build transitive clusters of ingredient labels above `threshold`.
    Returns a list of clusters, where each cluster is a list of labels.
    """
    labels = list(ingredients.keys())
    parent = {l: l for l in labels}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Compare all pairs using rapidfuzz
    for i, label_a in enumerate(labels):
        # Use process.extract for efficient batch comparison
        matches = process.extract(
            label_a,
            labels[i+1:],
            scorer=fuzz.ratio,
            score_cutoff=threshold,
            limit=None,
        )
        for match_label, score, _ in matches:
            union(label_a, match_label)

    # Group into clusters
    clusters_dict = defaultdict(list)
    for label in labels:
        clusters_dict[find(label)].append(label)

    # Only return clusters with >1 member
    return [c for c in clusters_dict.values() if len(c) > 1]


def _apply_merges(g: Graph, merges: list[tuple[str, list[str]]],
                  ingredients: dict[str, str]) -> int:
    """
    Apply merges to the graph.

    For each (canonical_label, [old_labels]) pair:
    1. Find all recipes linked to old ingredient URIs
    2. Re-link them to the canonical ingredient URI
    3. Add skos:altLabel on canonical for each old label
    4. Remove orphaned old ingredient nodes

    Returns the number of merges applied.
    """
    g.bind("skos", SKOS)
    merge_count = 0

    for canonical_label, old_labels in merges:
        canonical_uri = HEALS_ING[_slugify(canonical_label)]

        # Ensure canonical exists
        g.add((canonical_uri, RDF.type, HEALS_ING.Ingredient))
        g.add((canonical_uri, RDFS.label, Literal(canonical_label)))

        for old_label in old_labels:
            if old_label == canonical_label:
                continue

            old_uri_str = ingredients.get(old_label)
            if not old_uri_str:
                continue

            from rdflib import URIRef
            old_uri = URIRef(old_uri_str)

            # Move all hasIngredient links from old → canonical
            for recipe in g.subjects(FKG.hasIngredient, old_uri):
                g.remove((recipe, FKG.hasIngredient, old_uri))
                g.add((recipe, FKG.hasIngredient, canonical_uri))

            # Add altLabel on canonical
            g.add((canonical_uri, SKOS.altLabel, Literal(old_label)))

            # Remove old ingredient node (type + label + any other triples)
            for p, o in list(g.predicate_objects(old_uri)):
                g.remove((old_uri, p, o))
            for s, p in list(g.subject_predicates(old_uri)):
                g.remove((s, p, old_uri))

            merge_count += 1
            print(f"    ✓ Merged \"{old_label}\" → \"{canonical_label}\"")

    return merge_count


def _slugify(text: str) -> str:
    """PascalCase slugify for URI creation."""
    import re
    text = str(text).strip()
    text = re.sub(r"[^\w\s-]", "", text)
    words = re.split(r"[\s\-_]+", text)
    return "".join(w.capitalize() for w in words if w)


def run_dedup():
    """Main dedup routine: auto-merge Tier 1, generate CSV for Tier 2."""
    print("\n🔍 Ingredient Deduplication (rapidfuzz)")
    print("=" * 60)

    # Load graph
    print("  Loading KG…")
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("skos", SKOS)
    g.parse(str(OUTPUT_TTL), format="turtle")
    print(f"  Loaded {len(g)} triples")

    ingredients = _extract_ingredients(g)
    print(f"  Found {len(ingredients)} unique ingredients")

    # ── Tier 1: Auto-merge (≥ 92%) ───────────────────────────────────
    print(f"\n  Tier 1: Auto-merge (similarity ≥ {AUTO_MERGE_THRESHOLD}%)…")
    auto_clusters = _build_clusters(ingredients, AUTO_MERGE_THRESHOLD)
    print(f"  Found {len(auto_clusters)} auto-merge clusters")

    auto_merges = []
    for cluster in auto_clusters:
        canonical = _pick_canonical(cluster)
        old = [l for l in cluster if l != canonical]
        auto_merges.append((canonical, old))
        print(f"    Cluster: {canonical} ← {old}")

    if auto_merges:
        count = _apply_merges(g, auto_merges, ingredients)
        print(f"\n  Applied {count} auto-merges")
    else:
        print("  No auto-merges needed")

    # Refresh ingredients after merges
    ingredients = _extract_ingredients(g)

    # ── Tier 2: Review (80–92%) ──────────────────────────────────────
    print(f"\n  Tier 2: Review candidates ({REVIEW_THRESHOLD}–{AUTO_MERGE_THRESHOLD}%)…")
    review_clusters = _build_clusters(ingredients, REVIEW_THRESHOLD)
    print(f"  Found {len(review_clusters)} review clusters")

    if review_clusters:
        # Write to CSV
        with open(REVIEW_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "cluster_id", "ingredient_label", "suggested_canonical",
                "similarity", "action"
            ])
            for cid, cluster in enumerate(review_clusters):
                canonical = _pick_canonical(cluster)
                for label in cluster:
                    if label == canonical:
                        sim = 100.0
                    else:
                        sim = fuzz.ratio(label.lower(), canonical.lower())
                    # action: 'merge', 'keep', or leave blank
                    action = "" if label == canonical else "merge"
                    writer.writerow([cid, label, canonical, f"{sim:.1f}", action])

        print(f"  Wrote review CSV → {REVIEW_CSV}")
        print(f"  Edit the 'action' column: 'merge' to merge, 'keep' to keep separate")
        print(f"  Then run: python -m pipeline.dedup_ingredients --apply-review")
    else:
        print("  No review candidates found")

    # Save graph (with auto-merges applied)
    g.serialize(str(OUTPUT_TTL), format="turtle")
    print(f"\n  💾 Saved KG → {OUTPUT_TTL}")

    # Save merge log
    log = {
        "auto_merges": [
            {"canonical": c, "merged": old} for c, old in auto_merges
        ],
        "review_clusters": len(review_clusters),
    }
    with open(MERGE_LOG, "w") as f:
        json.dump(log, f, indent=2)
    print(f"  📝 Merge log → {MERGE_LOG}")

    # Update known_ingredients.json
    _update_known_ingredients(auto_merges)

    # Stats
    new_ingredients = _extract_ingredients(g)
    print(f"\n  Ingredients before: {len(ingredients) + sum(len(old) for _, old in auto_merges)}")
    print(f"  Ingredients after:  {len(new_ingredients)}")
    print(f"  Reduced by:         {len(ingredients) + sum(len(old) for _, old in auto_merges) - len(new_ingredients)}")


def apply_review():
    """Apply reviewed merges from the CSV."""
    print("\n🔧 Applying reviewed merges from CSV")
    print("=" * 60)

    if not REVIEW_CSV.exists():
        print(f"  ❌ Review CSV not found: {REVIEW_CSV}")
        print(f"  Run 'python -m pipeline.dedup_ingredients' first")
        return

    # Load graph
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("skos", SKOS)
    g.parse(str(OUTPUT_TTL), format="turtle")

    ingredients = _extract_ingredients(g)

    # Parse CSV
    merges_by_cluster = defaultdict(lambda: {"canonical": None, "merge": []})
    with open(REVIEW_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row["cluster_id"]
            label = row["ingredient_label"]
            canonical = row["suggested_canonical"]
            action = row["action"].strip().lower()

            if label == canonical:
                merges_by_cluster[cid]["canonical"] = canonical
            elif action == "merge":
                merges_by_cluster[cid]["canonical"] = canonical
                merges_by_cluster[cid]["merge"].append(label)

    merges = [
        (data["canonical"], data["merge"])
        for data in merges_by_cluster.values()
        if data["canonical"] and data["merge"]
    ]

    if not merges:
        print("  No merges to apply (all marked 'keep' or CSV unchanged)")
        return

    print(f"  {len(merges)} clusters to merge:")
    count = _apply_merges(g, merges, ingredients)

    g.serialize(str(OUTPUT_TTL), format="turtle")
    print(f"\n  💾 Saved KG → {OUTPUT_TTL}")
    print(f"  Applied {count} review merges")

    _update_known_ingredients(merges)


def _update_known_ingredients(merges: list[tuple[str, list[str]]]):
    """Update known_ingredients.json with merge mappings."""
    ki_path = STATE_DIR / "known_ingredients.json"
    if not ki_path.exists():
        return

    with open(ki_path) as f:
        known = json.load(f)

    for canonical, old_labels in merges:
        for old in old_labels:
            known[old.lower()] = canonical

    with open(ki_path, "w") as f:
        json.dump(known, f, indent=2)
    print(f"  📝 Updated known_ingredients.json")


def main():
    parser = argparse.ArgumentParser(description="Ingredient deduplication")
    parser.add_argument("--apply-review", action="store_true",
                        help="Apply reviewed merges from CSV")
    args = parser.parse_args()

    if args.apply_review:
        apply_review()
    else:
        run_dedup()


if __name__ == "__main__":
    main()
