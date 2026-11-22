#!/usr/bin/env python3
"""
One-time fix: Re-classify diet types for all recipes in the existing TTL
based on their ingredient lists.

Recipes that already have a diet type from the source dataset (DS2) are
left untouched. Recipes where diet was defaulted to "Vegetarian" because
the source had no diet column (DS1) are reclassified using ingredient-based
inference.

Usage:
    python scripts/fix_diet_types.py [--dry-run]
"""

import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rdflib import Graph, Literal
from rdflib.namespace import RDF, RDFS

from pipeline.config import FKG, HEALS, HEALS_ING, OUTPUT_TTL
from pipeline.schema import slugify, infer_diet_from_ingredients


def fix_diet_types(dry_run: bool = False):
    """Fix diet types for all recipes in the knowledge graph."""
    print(f"Loading graph from {OUTPUT_TTL} ...")
    g = Graph()
    g.bind("fkg", FKG)
    g.bind("heals", HEALS)
    g.bind("heals-ing", HEALS_ING)
    g.parse(str(OUTPUT_TTL), format="turtle")
    print(f"  Loaded {len(g)} triples.")

    # Iterate over all recipes
    recipes = list(g.subjects(RDF.type, HEALS.Recipe))
    print(f"  Found {len(recipes)} recipes.\n")

    stats = {"unchanged": 0, "vegetarian_to_nonveg": 0, "vegetarian_to_eggetarian": 0}
    changes = []

    for recipe_uri in recipes:
        # Get current diet
        current_diets = list(g.objects(recipe_uri, FKG.hasDietType))
        label = str(list(g.objects(recipe_uri, RDFS.label))[0])

        # Get ingredient names for this recipe
        ingredient_uris = list(g.objects(recipe_uri, FKG.hasIngredient))
        ingredient_names = []
        for ing_uri in ingredient_uris:
            ing_labels = list(g.objects(ing_uri, RDFS.label))
            if ing_labels:
                ingredient_names.append(str(ing_labels[0]))

        # Infer diet from ingredients
        inferred = infer_diet_from_ingredients(ingredient_names)

        # Current diet slug (from URI fragment)
        current_slug = str(current_diets[0]).split("#")[-1] if current_diets else "Unknown"

        if inferred != current_slug:
            changes.append((label, current_slug, inferred, ingredient_names))
            if inferred == "NonVegetarian":
                stats["vegetarian_to_nonveg"] += 1
            elif inferred == "Eggetarian":
                stats["vegetarian_to_eggetarian"] += 1

            if not dry_run:
                # Remove old diet type triple
                for old_diet in current_diets:
                    g.remove((recipe_uri, FKG.hasDietType, old_diet))

                # Add new diet type
                new_diet_uri = FKG[inferred]
                g.add((new_diet_uri, RDF.type, FKG.DietType))
                g.add((new_diet_uri, RDFS.label, Literal(inferred)))
                g.add((recipe_uri, FKG.hasDietType, new_diet_uri))
        else:
            stats["unchanged"] += 1

    # Print summary
    print("=" * 70)
    print("  DIET TYPE RECLASSIFICATION SUMMARY")
    print("=" * 70)
    print(f"  Unchanged (correct):         {stats['unchanged']}")
    print(f"  Vegetarian → NonVegetarian:  {stats['vegetarian_to_nonveg']}")
    print(f"  Vegetarian → Eggetarian:     {stats['vegetarian_to_eggetarian']}")
    print(f"  Total changes:               {len(changes)}")
    print()

    # Print changed recipes
    if changes:
        from pipeline.schema import (
            _NON_VEG_KEYWORDS, _EGG_KEYWORDS, _FALSE_POSITIVE_EXCLUSIONS,
        )
        print("  Changed recipes:")
        print("  " + "-" * 66)
        for label, old, new, ings in sorted(changes, key=lambda x: x[2]):
            # Find the trigger ingredient
            triggers = []
            for ing in ings:
                ing_low = ing.lower()
                is_excluded = any(
                    exc.replace(" ", "") in ing_low.replace(" ", "")
                    for exc in _FALSE_POSITIVE_EXCLUSIONS
                )
                if is_excluded:
                    continue
                if new == "NonVegetarian":
                    for kw in _NON_VEG_KEYWORDS:
                        if kw in ing_low:
                            triggers.append(ing)
                            break
                elif new == "Eggetarian":
                    for kw in _EGG_KEYWORDS:
                        if kw in ing_low:
                            triggers.append(ing)
                            break
            trigger_str = ", ".join(triggers[:3])
            print(f"    {old:12s} → {new:16s}  {label[:40]:40s}  [{trigger_str}]")
        print()

    if dry_run:
        print("  ⚠️  DRY RUN — no changes written to disk.")
    else:
        # Save updated graph
        g.serialize(str(OUTPUT_TTL), format="turtle")
        print(f"  💾 Saved updated graph → {OUTPUT_TTL}")
        print(f"     New triple count: {len(g)}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    fix_diet_types(dry_run=dry_run)
