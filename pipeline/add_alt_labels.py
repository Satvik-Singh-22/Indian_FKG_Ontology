"""
Add skos:altLabel triples to the Food Knowledge Graph.

Sources:
  1. Transliteration map (pipeline.transliteration_map)
  2. Dedup merge log (old names become altLabels on canonical ingredient)

Usage:
    python -m pipeline.add_alt_labels
"""

import json
from pathlib import Path

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, SKOS

from pipeline.config import FKG, HEALS, HEALS_ING, OUTPUT_TTL
from pipeline.transliteration_map import TRANSLITERATION_MAP
from pipeline.schema import slugify


MERGE_LOG = Path(OUTPUT_TTL).parent / "dedup_merge_log.json"


def _find_ingredient_uri(g: Graph, canonical_label: str) -> URIRef | None:
    """Find an ingredient URI by its rdfs:label."""
    for subj in g.subjects(RDF.type, HEALS_ING.Ingredient):
        for label in g.objects(subj, RDFS.label):
            if str(label) == canonical_label:
                return subj
    return None


def add_transliteration_labels(g: Graph) -> int:
    """Add skos:altLabel triples from the transliteration map."""
    added = 0
    missing = []

    for alt_name, canonical_label, lang_tag in TRANSLITERATION_MAP:
        uri = _find_ingredient_uri(g, canonical_label)
        if uri is None:
            # Try slugified URI lookup as fallback
            uri_candidate = HEALS_ING[slugify(canonical_label)]
            if (uri_candidate, RDF.type, HEALS_ING.Ingredient) in g:
                uri = uri_candidate
            else:
                missing.append((alt_name, canonical_label))
                continue

        # Create language-tagged literal
        alt_literal = Literal(alt_name, lang=lang_tag)

        # Only add if not already present
        if (uri, SKOS.altLabel, alt_literal) not in g:
            g.add((uri, SKOS.altLabel, alt_literal))
            added += 1

    if missing:
        print(f"\n  ⚠️  {len(missing)} transliteration entries couldn't find their canonical ingredient:")
        for alt, canonical in missing[:10]:
            print(f"      \"{alt}\" → \"{canonical}\" (not found in KG)")
        if len(missing) > 10:
            print(f"      … and {len(missing) - 10} more")

    return added


def add_dedup_merge_labels(g: Graph) -> int:
    """Add skos:altLabel triples from dedup merge log (old names → canonical)."""
    if not MERGE_LOG.exists():
        print("  No dedup merge log found, skipping")
        return 0

    with open(MERGE_LOG) as f:
        log = json.load(f)

    added = 0
    for entry in log.get("auto_merges", []):
        canonical_label = entry["canonical"]
        uri = _find_ingredient_uri(g, canonical_label)
        if uri is None:
            continue

        for old_label in entry.get("merged", []):
            alt_literal = Literal(old_label)  # no lang tag — these are English variants
            if (uri, SKOS.altLabel, alt_literal) not in g:
                g.add((uri, SKOS.altLabel, alt_literal))
                added += 1

    return added


def main():
    print("\n🏷️  Adding skos:altLabel triples")
    print("=" * 60)

    # Load graph
    print("  Loading KG…")
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.bind("skos", SKOS)
    g.parse(str(OUTPUT_TTL), format="turtle")

    initial_triples = len(g)
    print(f"  Loaded {initial_triples} triples")

    # Count existing altLabels
    existing_alt = sum(1 for _ in g.triples((None, SKOS.altLabel, None)))
    print(f"  Existing skos:altLabel triples: {existing_alt}")

    # 1. Add transliteration labels
    print("\n  📝 Adding transliteration altLabels…")
    trans_count = add_transliteration_labels(g)
    print(f"  Added {trans_count} transliteration altLabels")

    # 2. Add dedup merge labels
    print("\n  📝 Adding dedup merge altLabels…")
    dedup_count = add_dedup_merge_labels(g)
    print(f"  Added {dedup_count} dedup altLabels")

    # Save
    g.serialize(str(OUTPUT_TTL), format="turtle")
    final_triples = len(g)

    print(f"\n  💾 Saved KG → {OUTPUT_TTL}")
    print(f"\n  Summary:")
    print(f"    Triples before     : {initial_triples}")
    print(f"    Triples after      : {final_triples}")
    print(f"    New altLabels added : {trans_count + dedup_count}")
    print(f"    Total altLabels    : {existing_alt + trans_count + dedup_count}")

    # Show some examples
    print("\n  Sample altLabel triples:")
    count = 0
    for s, p, o in g.triples((None, SKOS.altLabel, None)):
        if count >= 10:
            break
        label = list(g.objects(s, RDFS.label))
        label_str = str(label[0]) if label else str(s)
        lang = o.language if hasattr(o, 'language') and o.language else "none"
        print(f"    {label_str} — altLabel: \"{o}\" @{lang}")
        count += 1


if __name__ == "__main__":
    main()
