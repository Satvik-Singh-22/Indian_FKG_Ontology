"""
Main pipeline orchestrator.
Ties together dataset loading, LLM parsing, ingredient resolution,
ontology building, and state persistence.

Usage:
    python -m pipeline.run_pipeline
"""

import sys
from pathlib import Path

from pipeline.config import (
    DATASET_NUMBER, START_INDEX, END_INDEX,
    INTERACTIVE_REVIEW, OUTPUT_TTL, print_config,
)
from pipeline.dataset_loader import load_dataset
from pipeline.llm_parser import batch_parse_recipes
from pipeline.ingredient_resolver import resolve_ingredients
from pipeline.ontology_builder import (
    init_graph, load_graph, recipe_exists,
    add_recipe_to_graph, save_graph, print_stats,
)
from pipeline.state_manager import (
    load_processed_recipes, save_processed_recipes,
    is_recipe_processed, mark_recipe_processed,
    load_known_ingredients, save_known_ingredients,
    load_skipped_ingredients, save_skipped_ingredients,
    log_run, print_run_history,
)


def main():
    print("\n🍛 Indian Food Knowledge Graph Pipeline")
    print("=" * 50)
    print_config()

    # ── 1. Load persistent state ──────────────────────────────────────
    print("\n📂 Loading state…")
    processed = load_processed_recipes()
    known_ingredients = load_known_ingredients()
    skipped_ingredients = load_skipped_ingredients()
    print_run_history()

    print(f"  Known ingredients : {len(known_ingredients)}")
    print(f"  Skipped ingredients: {len(skipped_ingredients)}")

    # ── 2. Initialize or load ontology graph ──────────────────────────
    print("\n📊 Initializing ontology…")
    output_path = Path(OUTPUT_TTL)
    if output_path.exists():
        g = load_graph(output_path)
    else:
        g = init_graph()

    # ── 3. Load dataset rows ──────────────────────────────────────────
    recipes = load_dataset(DATASET_NUMBER, START_INDEX, END_INDEX)
    if not recipes:
        print("\n⚠️  No recipes to process. Check your index range.")
        return

    # ── 4. Filter already-processed recipes ───────────────────────────
    to_process = []
    for recipe in recipes:
        row_idx = recipe["dataset_row_index"]
        if is_recipe_processed(processed, DATASET_NUMBER, row_idx):
            continue
        if recipe_exists(g, recipe["name"]):
            print(f"  ⏭  Already in ontology: {recipe['name']}")
            mark_recipe_processed(processed, DATASET_NUMBER, row_idx)
            continue
        to_process.append(recipe)

    print(f"\n  Recipes to process: {len(to_process)} "
          f"(skipped {len(recipes) - len(to_process)} already done)")

    if not to_process:
        print("\n✅ All recipes in this range are already processed.")
        save_processed_recipes(processed)
        return

    # ── 5. LLM ingredient extraction ─────────────────────────────────
    print("\n🤖 Extracting ingredients via LLM…")
    all_parsed = batch_parse_recipes(to_process)

    # ── 6. Process each recipe ────────────────────────────────────────
    print("\n🔧 Resolving ingredients & building ontology…")
    recipes_added = 0
    ingredients_before = len(known_ingredients)

    for i, recipe in enumerate(to_process):
        raw_ingredients = all_parsed[i]
        if not raw_ingredients:
            print(f"  ⚠️  No ingredients parsed for: {recipe['name']}")

        print(f"\n  [{i+1}/{len(to_process)}] {recipe['name']} "
              f"({len(raw_ingredients)} ingredients)")

        # Resolve ingredients (interactive if enabled)
        resolved = resolve_ingredients(
            raw_ingredients,
            known_ingredients,
            skipped_ingredients,
            interactive=INTERACTIVE_REVIEW,
        )

        # Add to graph
        add_recipe_to_graph(g, recipe, resolved)
        mark_recipe_processed(processed, DATASET_NUMBER,
                              recipe["dataset_row_index"])
        recipes_added += 1

    new_ingredients = len(known_ingredients) - ingredients_before

    # ── 7. Save everything ────────────────────────────────────────────
    print("\n💾 Saving state and ontology…")
    save_graph(g, OUTPUT_TTL)
    save_processed_recipes(processed)
    save_known_ingredients(known_ingredients)
    save_skipped_ingredients(skipped_ingredients)
    log_run(DATASET_NUMBER, START_INDEX, END_INDEX,
            recipes_added, new_ingredients, len(skipped_ingredients))

    # ── 8. Summary ────────────────────────────────────────────────────
    print("\n✅ Run complete!")
    print(f"  Recipes added this run  : {recipes_added}")
    print(f"  New ingredients added   : {new_ingredients}")
    print(f"  Total known ingredients : {len(known_ingredients)}")
    print_stats(g)


if __name__ == "__main__":
    main()
