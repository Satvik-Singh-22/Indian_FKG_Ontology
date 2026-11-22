"""
Dataset loader and normalizer.
Loads both CSV formats and produces uniform recipe dicts.
"""

import pandas as pd
from pathlib import Path

from pipeline.config import DS1_PATH, DS2_PATH


def _safe_str(val) -> str | None:
    """Return stripped string or None if NaN/empty."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    return s if s else None


def load_dataset(dataset_number: int,
                 start_idx: int,
                 end_idx: int) -> list[dict]:
    """
    Load a dataset and return normalized recipe dicts for the given index range.

    Args:
        dataset_number: 1 for cleaned_db.csv, 2 for cuisines.csv
        start_idx: start row index (inclusive, 0-based)
        end_idx: end row index (exclusive)

    Returns:
        List of normalized recipe dicts with keys:
            name, raw_ingredients, cuisine, diet, course, prep_time,
            cook_time, total_time, servings, instructions, description,
            url, image_url, dataset_number, dataset_row_index
    """
    if dataset_number == 1:
        return _load_ds1(start_idx, end_idx)
    elif dataset_number == 2:
        return _load_ds2(start_idx, end_idx)
    else:
        raise ValueError(f"Unknown dataset number: {dataset_number}. Use 1 or 2.")


def get_dataset_size(dataset_number: int) -> int:
    """Return the total number of rows in a dataset."""
    path = DS1_PATH if dataset_number == 1 else DS2_PATH
    df = pd.read_csv(path)
    return len(df)


def _load_ds1(start_idx: int, end_idx: int) -> list[dict]:
    """
    Load Dataset 1 (cleaned_db.csv).

    Columns: TranslatedRecipeName, TranslatedIngredients, TotalTimeInMins,
             Cuisine, TranslatedInstructions, URL, Cleaned-Ingredients,
             image-url, Ingredient-count
    """
    print(f"\n[DS1] Loading {DS1_PATH} (rows {start_idx}–{end_idx}) …")
    df = pd.read_csv(DS1_PATH)
    df.columns = df.columns.str.strip()

    # Clamp range
    end_idx = min(end_idx, len(df))
    if start_idx >= len(df):
        print(f"[DS1] start_idx ({start_idx}) >= dataset length ({len(df)}). Nothing to load.")
        return []

    recipes = []
    for i in range(start_idx, end_idx):
        row = df.iloc[i]
        name = _safe_str(row.get("TranslatedRecipeName"))
        if not name:
            continue

        recipes.append({
            "name":             name,
            "raw_ingredients":  _safe_str(row.get("TranslatedIngredients")) or "",
            "cuisine":          _safe_str(row.get("Cuisine")),
            "diet":             None,  # DS1 doesn't have a diet column
            "course":           None,  # DS1 doesn't have a course column
            "prep_time":        None,
            "cook_time":        None,
            "total_time":       row.get("TotalTimeInMins"),
            "servings":         None,
            "instructions":     _safe_str(row.get("TranslatedInstructions")),
            "description":      None,
            "url":              _safe_str(row.get("URL")),
            "image_url":        _safe_str(row.get("image-url")),
            "dataset_number":   1,
            "dataset_row_index": i,
        })

    print(f"[DS1] Loaded {len(recipes)} recipes from rows {start_idx}–{end_idx}.")
    return recipes


def _load_ds2(start_idx: int, end_idx: int) -> list[dict]:
    """
    Load Dataset 2 (cuisines.csv).

    Columns: name, image_url, description, cuisine, course, diet,
             prep_time, ingredients, instructions
    """
    print(f"\n[DS2] Loading {DS2_PATH} (rows {start_idx}–{end_idx}) …")
    df = pd.read_csv(DS2_PATH)
    df.columns = df.columns.str.strip()

    # Clamp range
    end_idx = min(end_idx, len(df))
    if start_idx >= len(df):
        print(f"[DS2] start_idx ({start_idx}) >= dataset length ({len(df)}). Nothing to load.")
        return []

    recipes = []
    for i in range(start_idx, end_idx):
        row = df.iloc[i]
        name = _safe_str(row.get("name"))
        if not name:
            continue

        recipes.append({
            "name":             name,
            "raw_ingredients":  _safe_str(row.get("ingredients")) or "",
            "cuisine":          _safe_str(row.get("cuisine")),
            "diet":             _safe_str(row.get("diet")),
            "course":           _safe_str(row.get("course")),
            "prep_time":        row.get("prep_time"),
            "cook_time":        None,
            "total_time":       None,
            "servings":         None,
            "instructions":     _safe_str(row.get("instructions")),
            "description":      _safe_str(row.get("description")),
            "url":              None,
            "image_url":        _safe_str(row.get("image_url")),
            "dataset_number":   2,
            "dataset_row_index": i,
        })

    print(f"[DS2] Loaded {len(recipes)} recipes from rows {start_idx}–{end_idx}.")
    return recipes
