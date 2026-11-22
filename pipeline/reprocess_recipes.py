"""
Reprocess specific recipes or all empty recipes in the ontology graph.
Ties together dataset loading, LLM parsing, ingredient resolution,
ontology rebuilding, and state persistence.

Usage:
    python -m pipeline.reprocess_recipes --empty
    python -m pipeline.reprocess_recipes --indices 700 708 710 ...
    python -m pipeline.reprocess_recipes --non-interactive
"""

import sys
import argparse
import time
from pathlib import Path
import pandas as pd
from rdflib import RDF, RDFS

import json
import re
from pipeline.config import (
    DATASET_NUMBER, INTERACTIVE_REVIEW, OUTPUT_TTL,
    RATE_LIMIT_DELAY, GROQ_MODEL, FKG, HEALS, print_config,
)
from pipeline.dataset_loader import load_dataset, DS1_PATH, DS2_PATH, _safe_str
from pipeline.llm_parser import (
    parse_ingredients_single, client, SYSTEM_PROMPT, _strip_markdown_fences
)
from pipeline.ingredient_resolver import resolve_ingredients
from pipeline.ontology_builder import (
    load_graph, init_graph, add_recipe_to_graph,
    remove_recipe_from_graph, save_graph, print_stats,
)
from pipeline.state_manager import (
    load_processed_recipes, save_processed_recipes,
    mark_recipe_processed, unmark_recipe_processed,
    load_known_ingredients, save_known_ingredients,
    load_skipped_ingredients, save_skipped_ingredients,
    log_run,
)
from pipeline.schema import slugify


def extract_ingredients_robust(raw_text: str, name: str) -> list[str]:
    """Parse ingredients with automatic handling and waiting on rate limits."""
    if not raw_text or pd.isna(raw_text):
        return []

    user_msg = f"Recipe: {name}\nRaw ingredients:\n{str(raw_text).strip()}"

    for attempt in range(10):
        try:
            resp = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": user_msg},
                ],
                max_tokens=512,
                temperature=0,
            )
            content = _strip_markdown_fences(resp.choices[0].message.content.strip())
            parsed = json.loads(content)
            if isinstance(parsed, list):
                return [str(i).strip() for i in parsed if str(i).strip()]
            return []
        except json.JSONDecodeError:
            fallback = re.findall(r'"([^"]+)"', content)
            if fallback:
                return fallback
            return []
        except Exception as e:
            err_str = str(e)
            match = re.search(r"try again in (?:(\d+)m)?([\d\.]+)s", err_str)
            if match:
                mins = int(match.group(1)) if match.group(1) else 0
                secs = float(match.group(2))
                wait_time = mins * 60 + secs + 2.0
                print(f"  ⏳ Rate limit reached. Waiting {wait_time:.1f}s before retry…")
                time.sleep(wait_time)
            else:
                print(f"  [WARN] Groq error for '{name}': {e}")
                time.sleep(RATE_LIMIT_DELAY * 2)

    return []


def get_empty_recipe_indices(g, dataset_path=DS1_PATH) -> list[int]:
    """Find row indices of all recipes in the graph that have 0 ingredients."""
    df = pd.read_csv(dataset_path)
    df.columns = df.columns.str.strip()
    name_to_idx = {
        str(row["TranslatedRecipeName"]).strip().lower(): i
        for i, row in df.iterrows()
        if pd.notna(row.get("TranslatedRecipeName"))
    }

    empty_indices = []
    for r in g.subjects(RDF.type, HEALS.Recipe):
        ings = list(g.objects(r, FKG.hasIngredient))
        if len(ings) == 0:
            labels = list(g.objects(r, RDFS.label))
            lbl = str(labels[0]).strip().lower() if labels else ""
            if lbl in name_to_idx:
                empty_indices.append(name_to_idx[lbl])

    return sorted(set(empty_indices))


def load_recipe_by_index(dataset_number: int, idx: int) -> dict | None:
    """Load a single recipe by its dataset row index."""
    path = DS1_PATH if dataset_number == 1 else DS2_PATH
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    if idx < 0 or idx >= len(df):
        return None

    row = df.iloc[idx]
    if dataset_number == 1:
        name = _safe_str(row.get("TranslatedRecipeName"))
        if not name:
            return None
        return {
            "name":             name,
            "raw_ingredients":  _safe_str(row.get("TranslatedIngredients")) or "",
            "cuisine":          _safe_str(row.get("Cuisine")),
            "diet":             None,
            "course":           None,
            "prep_time":        None,
            "cook_time":        None,
            "total_time":       row.get("TotalTimeInMins"),
            "servings":         None,
            "instructions":     _safe_str(row.get("TranslatedInstructions")),
            "description":      None,
            "url":              _safe_str(row.get("URL")),
            "image_url":        _safe_str(row.get("image-url")),
            "dataset_number":   1,
            "dataset_row_index": idx,
        }
    else:
        name = _safe_str(row.get("recipe_name"))
        if not name:
            return None
        return {
            "name":             name,
            "raw_ingredients":  _safe_str(row.get("ingredients")) or "",
            "cuisine":          _safe_str(row.get("cuisine")),
            "diet":             _safe_str(row.get("diet")),
            "course":           _safe_str(row.get("course")),
            "prep_time":        row.get("prep_time"),
            "cook_time":        row.get("cook_time"),
            "total_time":       None,
            "servings":         row.get("servings"),
            "instructions":     _safe_str(row.get("instructions")),
            "description":      _safe_str(row.get("description")),
            "url":              _safe_str(row.get("url")),
            "image_url":        None,
            "dataset_number":   2,
            "dataset_row_index": idx,
        }


def reprocess(target_indices: list[int], interactive: bool = True):
    print("\n🔄 Indian Food Knowledge Graph Recipe Reprocessor")
    print("=" * 60)

    processed = load_processed_recipes()
    known_ingredients = load_known_ingredients()
    skipped_ingredients = load_skipped_ingredients()

    output_path = Path(OUTPUT_TTL)
    if not output_path.exists():
        print(f"❌ Ontology file {OUTPUT_TTL} does not exist.")
        return

    g = load_graph(output_path)
    initial_triples = len(g)

    # Resolve recipes to reprocess
    to_redo = []
    for idx in target_indices:
        r = load_recipe_by_index(DATASET_NUMBER, idx)
        if r:
            to_redo.append(r)
        else:
            print(f"⚠️ Could not load row {idx} from dataset {DATASET_NUMBER}")

    print(f"\nTarget recipes to reprocess: {len(to_redo)}")
    if not to_redo:
        print("Nothing to reprocess.")
        return

    recipes_reprocessed = 0
    ingredients_before = len(known_ingredients)

    for i, recipe in enumerate(to_redo):
        idx = recipe["dataset_row_index"]
        name = recipe["name"]
        print(f"\n[{i+1}/{len(to_redo)}] Reprocessing Row {idx}: {name}")

        # Parse ingredients
        raw_text = recipe.get("raw_ingredients", "")
        raw_ingredients = extract_ingredients_robust(raw_text, name)

        if not raw_ingredients:
            print(f"  ⚠️ Warning: Still 0 ingredients parsed for {name}. Keeping existing state.")
            continue

        print(f"  ✓ Extracted {len(raw_ingredients)} ingredients")

        # Resolve ingredients
        resolved = resolve_ingredients(
            raw_ingredients,
            known_ingredients,
            skipped_ingredients,
            interactive=interactive,
        )

        # Cleanly remove previous triples from graph
        remove_recipe_from_graph(g, name)

        # Add updated recipe
        add_recipe_to_graph(g, recipe, resolved)
        mark_recipe_processed(processed, DATASET_NUMBER, idx)
        recipes_reprocessed += 1

        time.sleep(RATE_LIMIT_DELAY)

    new_ingredients = len(known_ingredients) - ingredients_before

    print("\n💾 Saving state and ontology…")
    save_graph(g, OUTPUT_TTL)
    save_processed_recipes(processed)
    save_known_ingredients(known_ingredients)
    save_skipped_ingredients(skipped_ingredients)
    log_run(DATASET_NUMBER, min(target_indices), max(target_indices) + 1,
            recipes_reprocessed, new_ingredients, len(skipped_ingredients))

    print("\n✅ Reprocess complete!")
    print(f"  Recipes reprocessed     : {recipes_reprocessed}/{len(to_redo)}")
    print(f"  New ingredients added   : {new_ingredients}")
    print(f"  Total known ingredients : {len(known_ingredients)}")
    print(f"  Graph triple delta      : {len(g) - initial_triples:+d}")
    print_stats(g)


def main():
    parser = argparse.ArgumentParser(description="Reprocess recipes in FKG ontology")
    parser.add_argument("--indices", nargs="+", type=int, help="Specific row indices to reprocess")
    parser.add_argument("--empty", action="store_true", help="Reprocess all recipes currently with 0 ingredients")
    parser.add_argument("--non-interactive", action="store_true", help="Run without prompting for ingredient review")
    args = parser.parse_args()

    output_path = Path(OUTPUT_TTL)
    if not output_path.exists():
        print(f"❌ Ontology file {OUTPUT_TTL} does not exist.")
        sys.exit(1)

    g = load_graph(output_path)

    indices = []
    if args.indices:
        indices.extend(args.indices)

    if args.empty or not indices:
        empty_indices = get_empty_recipe_indices(g, DS1_PATH if DATASET_NUMBER == 1 else DS2_PATH)
        print(f"Found {len(empty_indices)} empty recipes in ontology graph.")
        indices.extend(empty_indices)

    indices = sorted(set(indices))
    if not indices:
        print("No recipes to reprocess.")
        return

    interactive = False if args.non_interactive else INTERACTIVE_REVIEW
    reprocess(indices, interactive=interactive)


if __name__ == "__main__":
    main()
