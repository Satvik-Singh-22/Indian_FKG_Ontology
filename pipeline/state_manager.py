"""
State manager for multi-run persistence.
Tracks processed recipes, known ingredients, skipped ingredients, and run logs.
All state is stored as JSON files in the configured STATE_DIR.
"""

import json
from pathlib import Path
from datetime import datetime

from pipeline.config import STATE_DIR


def _ensure_dir():
    """Create state directory if it doesn't exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filename: str, default=None):
    """Load a JSON file from STATE_DIR, returning default if not found."""
    path = STATE_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def _save_json(filename: str, data):
    """Save data as JSON to STATE_DIR."""
    _ensure_dir()
    path = STATE_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════
#  PROCESSED RECIPES
# ══════════════════════════════════════════════════════════════════════════

def load_processed_recipes() -> dict[str, list[int]]:
    """
    Load the set of already-processed row indices per dataset.
    Returns: {"1": [0, 1, 2, ...], "2": [0, 5, 10, ...]}
    """
    return _load_json("processed_recipes.json", default={})


def save_processed_recipes(processed: dict[str, list[int]]):
    """Save processed recipe indices."""
    _save_json("processed_recipes.json", processed)


def is_recipe_processed(processed: dict, dataset_number: int, row_index: int) -> bool:
    """Check if a specific row has been processed."""
    key = str(dataset_number)
    return row_index in processed.get(key, [])


def mark_recipe_processed(processed: dict, dataset_number: int, row_index: int):
    """Mark a row as processed."""
    key = str(dataset_number)
    if key not in processed:
        processed[key] = []
    if row_index not in processed[key]:
        processed[key].append(row_index)


def unmark_recipe_processed(processed: dict, dataset_number: int, row_index: int):
    """Unmark a row as processed."""
    key = str(dataset_number)
    if key in processed and row_index in processed[key]:
        processed[key].remove(row_index)


# ══════════════════════════════════════════════════════════════════════════
#  KNOWN INGREDIENTS
# ══════════════════════════════════════════════════════════════════════════

def load_known_ingredients() -> dict[str, str]:
    """
    Load known ingredients mapping.
    Returns: {lowercase_name: canonical_name}
    """
    return _load_json("known_ingredients.json", default={})


def save_known_ingredients(known: dict[str, str]):
    """Save known ingredients mapping."""
    _save_json("known_ingredients.json", known)


# ══════════════════════════════════════════════════════════════════════════
#  SKIPPED INGREDIENTS
# ══════════════════════════════════════════════════════════════════════════

def load_skipped_ingredients() -> set[str]:
    """Load the set of skipped ingredient names."""
    data = _load_json("skipped_ingredients.json", default=[])
    return set(data)


def save_skipped_ingredients(skipped: set[str]):
    """Save skipped ingredient names."""
    _save_json("skipped_ingredients.json", sorted(skipped))


# ══════════════════════════════════════════════════════════════════════════
#  RUN LOG
# ══════════════════════════════════════════════════════════════════════════

def log_run(dataset_number: int, start_idx: int, end_idx: int,
            recipes_added: int, new_ingredients: int, skipped: int):
    """Append a run entry to the run log."""
    log = _load_json("run_log.json", default=[])
    log.append({
        "timestamp": datetime.now().isoformat(),
        "dataset_number": dataset_number,
        "start_index": start_idx,
        "end_index": end_idx,
        "recipes_added": recipes_added,
        "new_ingredients_added": new_ingredients,
        "ingredients_skipped": skipped,
    })
    _save_json("run_log.json", log)


def print_run_history():
    """Print all previous runs."""
    log = _load_json("run_log.json", default=[])
    if not log:
        print("  No previous runs found.")
        return
    print(f"\n  📜 Run History ({len(log)} runs):")
    for i, entry in enumerate(log, 1):
        print(f"    [{i}] {entry['timestamp']} | DS{entry['dataset_number']} "
              f"rows {entry['start_index']}–{entry['end_index']} | "
              f"+{entry['recipes_added']} recipes, "
              f"+{entry['new_ingredients_added']} ingredients")
