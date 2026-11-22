"""
Ingredient resolver with rapidfuzz tiered matching and interactive human review.
Deduplicates ingredients against a known set, prompting the user when
similar names are found.

Tiers (using rapidfuzz.fuzz.ratio):
  - ≥ 92%: auto-merge into existing canonical name
  - 80–92%: prompt user for interactive review
  - < 80%: add as new ingredient
"""

from rapidfuzz import fuzz, process
from pipeline.schema import slugify

# ── Thresholds ────────────────────────────────────────────────────────
AUTO_MERGE_CUTOFF = 96   # Tier 1: auto-merge without asking
REVIEW_CUTOFF     = 80   # Tier 2: show interactive prompt


def resolve_ingredients(raw_list: list[str],
                        known_ingredients: dict[str, str],
                        skipped_ingredients: set[str],
                        interactive: bool = True) -> list[str]:
    """
    Resolve a list of LLM-extracted ingredient names against known ingredients.

    For each ingredient:
      1. Exact match (case-insensitive) → use existing canonical name
      2. rapidfuzz ≥ 92% → auto-merge into best match
      3. rapidfuzz 80–92% + interactive → prompt user
      4. Otherwise → auto-add as new

    Args:
        raw_list: ingredient names from LLM
        known_ingredients: dict of {lowercase_name: canonical_name}
        skipped_ingredients: set of lowercase names the user has previously skipped
        interactive: whether to prompt for human review

    Returns:
        List of resolved canonical ingredient names (may be shorter than input
        if user skips some).

    Side effects:
        Mutates known_ingredients and skipped_ingredients in place when new
        ingredients are added or skipped.
    """
    resolved = []

    for raw_name in raw_list:
        raw_name = raw_name.strip()
        if not raw_name:
            continue

        key = raw_name.lower()

        # 1. Exact match → use existing
        if key in known_ingredients:
            resolved.append(known_ingredients[key])
            continue

        # 2. Previously skipped → skip silently
        if key in skipped_ingredients:
            continue

        # 3. Fuzzy match against known ingredients using rapidfuzz
        known_keys = list(known_ingredients.keys())
        if not known_keys:
            known_ingredients[key] = raw_name
            resolved.append(raw_name)
            continue

        matches = process.extract(
            key,
            known_keys,
            scorer=fuzz.ratio,
            score_cutoff=REVIEW_CUTOFF,
            limit=10,
        )

        if matches:
            best_key, best_score, _ = matches[0]

            # Tier 1: auto-merge (≥ 92%)
            if best_score >= AUTO_MERGE_CUTOFF:
                canonical = known_ingredients[best_key]
                known_ingredients[key] = canonical
                resolved.append(canonical)
                continue

        # Deduplicate by canonical name (multiple keys can map to same canonical)
        seen_canonical = set()
        unique_matches = []
        for match_key, score, _ in matches:
            canonical = known_ingredients[match_key]
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                unique_matches.append((canonical, score))
        unique_matches = unique_matches[:5]  # Limit to 5 options

        if unique_matches and interactive:
            # Tier 2: interactive review (80–92%)
            candidates = [name for name, score in unique_matches]
            scores = {name: score for name, score in unique_matches}
            result = _interactive_review(raw_name, candidates, scores)
            if result is None:
                # User chose to skip
                skipped_ingredients.add(key)
                continue
            elif result == raw_name:
                # User chose to add as new (unchanged)
                known_ingredients[key] = raw_name
                resolved.append(raw_name)
            elif result.startswith("__RENAME__:"):
                # User chose to rename
                new_canonical = result[len("__RENAME__:"):]
                known_ingredients[key] = new_canonical
                known_ingredients[new_canonical.lower()] = new_canonical
                resolved.append(new_canonical)
            else:
                # User chose to merge into existing
                known_ingredients[key] = result
                resolved.append(result)
        else:
            # Auto-add as new (no close matches, or non-interactive)
            known_ingredients[key] = raw_name
            resolved.append(raw_name)

    return resolved


def _interactive_review(new_name: str,
                        candidates: list[str],
                        scores: dict[str, float] | None = None) -> str | None:
    """
    Display an interactive prompt for ingredient deduplication.

    Args:
        new_name: the new ingredient name from LLM
        candidates: list of unique canonical names that are similar
        scores: optional dict of {canonical_name: similarity_score}

    Returns:
        - canonical name to merge into (existing)
        - new_name if user wants to add as new
        - "__RENAME__:<name>" if user wants to rename
        - None if user wants to skip
    """
    print()
    print("─" * 60)
    print(f"  🆕 New ingredient: \"{new_name}\"")
    print(f"  Similar existing ingredients:")
    for i, canonical in enumerate(candidates, 1):
        score_str = f" ({scores[canonical]:.0f}%)" if scores and canonical in scores else ""
        print(f"    [{i}] {canonical}{score_str}")
    print(f"    [a] Add \"{new_name}\" as new ingredient")
    print(f"    [r] Rename — enter a custom name")
    print(f"    [s] Skip this ingredient")
    print("─" * 60)

    while True:
        choice = input("  Your choice: ").strip().lower()

        if choice == "a":
            return new_name
        elif choice == "s":
            return None
        elif choice == "r":
            custom = input("  Enter new name: ").strip()
            if custom:
                print(f"  ✓ Renamed \"{new_name}\" → \"{custom}\"")
                return f"__RENAME__:{custom}"
            else:
                print("  Name cannot be empty. Try again.")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                canonical = candidates[idx]
                print(f"  ✓ Merging \"{new_name}\" → \"{canonical}\"")
                return canonical
            else:
                print(f"  Invalid number. Choose 1–{len(candidates)}, 'a', 'r', or 's'.")
        else:
            print(f"  Invalid choice. Enter 1–{len(candidates)}, 'a', 'r', or 's'.")

