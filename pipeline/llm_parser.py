"""
Groq LLM ingredient extraction.
Handles single and batch parsing with rate limiting and fallback.
"""

import re
import json
import time
import pandas as pd
from groq import Groq

from pipeline.config import GROQ_API_KEY, GROQ_MODEL, RATE_LIMIT_DELAY, BATCH_SIZE


# ── Groq client ───────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)


# ── System prompt ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a culinary data extraction assistant specialising in Indian recipes.

Your task: given a raw ingredient string (which may contain quantities, units,
transliterations in brackets, and preparation notes), extract ONLY the clean
canonical English ingredient names.

Rules:
- Remove all quantities and units (cups, teaspoons, grams, etc.)
- Remove preparation notes (chopped, sliced, roasted, to taste, as required, etc.)
- Remove transliterations in brackets, e.g. "(Haldi)" from "Turmeric powder (Haldi)"
- Keep only the core ingredient name in plain English, title-cased
- If a line is a section header like "For tempering" or "For garnishing", skip it
- Deduplicate: if the same ingredient appears twice, include it once
- Return ONLY a JSON array of strings, nothing else. Example:
  ["Turmeric Powder", "Onion", "Mustard Seeds", "Curry Leaves"]
"""


def _strip_markdown_fences(content: str) -> str:
    """Remove markdown code fences from LLM response."""
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)
    return content.strip()


def parse_ingredients_single(raw: str, recipe_name: str = "") -> list[str]:
    """
    Send a single recipe's raw ingredient text to Groq.
    Returns a clean list of canonical ingredient names.
    """
    if not raw or pd.isna(raw):
        return []

    user_msg = f"Recipe: {recipe_name}\nRaw ingredients:\n{str(raw).strip()}"

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
        # Fallback: extract quoted strings
        fallback = re.findall(r'"([^"]+)"', content)
        return fallback if fallback else []
    except Exception as e:
        print(f"  [WARN] Groq error for '{recipe_name}': {e}")
        return []


def parse_ingredients_batch(rows: list[dict]) -> dict[int, list[str]]:
    """
    Parse ingredients for multiple recipes in one LLM call.

    Args:
        rows: list of {"idx": int, "name": str, "raw": str}

    Returns:
        {idx: [ingredient_name, ...]}
    """
    if not rows:
        return {}

    # Build numbered blocks for the LLM
    blocks = []
    for r in rows:
        blocks.append(f'[{r["idx"]}] Recipe: {r["name"]}\n{str(r["raw"]).strip()}')
    combined = "\n\n".join(blocks)

    batch_system = SYSTEM_PROMPT + """

IMPORTANT: You are processing MULTIPLE recipes at once. Return a JSON object
where each key is the recipe index number (as a string) and the value is the
array of ingredient names for that recipe. Example:
{"0": ["Turmeric", "Onion"], "1": ["Rice", "Mustard Seeds"]}
"""

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": batch_system},
                {"role": "user",   "content": combined},
            ],
            max_tokens=2048,
            temperature=0,
        )
        content = _strip_markdown_fences(resp.choices[0].message.content.strip())

        parsed = json.loads(content)
        result = {}
        for r in rows:
            key = str(r["idx"])
            if key in parsed and isinstance(parsed[key], list):
                result[r["idx"]] = [str(i).strip() for i in parsed[key] if str(i).strip()]
            else:
                result[r["idx"]] = []
        return result

    except Exception as e:
        print(f"  [WARN] Batch parse failed ({e}), falling back to per-recipe calls.")
        result = {}
        for r in rows:
            result[r["idx"]] = parse_ingredients_single(r["raw"], r["name"])
            time.sleep(RATE_LIMIT_DELAY)
        return result


def batch_parse_recipes(recipe_rows: list[dict]) -> list[list[str]]:
    """
    Run LLM ingredient parsing over a list of recipe dicts in batches.
    Automatically retries individual recipes that return empty from batch.

    Args:
        recipe_rows: list of dicts with keys "name" and "raw_ingredients"

    Returns:
        list (same length as input) of ingredient name lists
    """
    total = len(recipe_rows)
    all_results = [[] for _ in range(total)]

    batches = [
        list(range(i, min(i + BATCH_SIZE, total)))
        for i in range(0, total, BATCH_SIZE)
    ]

    print(f"  Parsing {total} recipes in {len(batches)} batch(es) of up to {BATCH_SIZE}…")

    for b_num, indices in enumerate(batches, 1):
        rows = []
        for local_idx, global_idx in enumerate(indices):
            recipe = recipe_rows[global_idx]
            raw = recipe.get("raw_ingredients", "")
            name = recipe.get("name", f"Recipe_{global_idx}")
            if pd.isna(raw):
                raw = ""
            rows.append({"idx": local_idx, "name": str(name), "raw": str(raw)})

        parsed = parse_ingredients_batch(rows)

        for local_idx, global_idx in enumerate(indices):
            all_results[global_idx] = parsed.get(local_idx, [])

        print(f"  Batch {b_num}/{len(batches)} done.")
        if b_num < len(batches):
            time.sleep(RATE_LIMIT_DELAY)

    # ── Retry empty results individually ──────────────────────────────
    retry_indices = [
        i for i in range(total)
        if not all_results[i]
        and recipe_rows[i].get("raw_ingredients", "").strip()
    ]

    if retry_indices:
        print(f"  ⟳ Retrying {len(retry_indices)} recipes individually "
              f"(empty from batch)…")
        for i in retry_indices:
            recipe = recipe_rows[i]
            raw = recipe.get("raw_ingredients", "")
            name = recipe.get("name", f"Recipe_{i}")
            result = parse_ingredients_single(raw, name)
            if result:
                all_results[i] = result
                print(f"    ✓ Retry success: {name} → {len(result)} ingredients")
            else:
                print(f"    ✗ Retry failed:  {name}")
            time.sleep(RATE_LIMIT_DELAY)

    return all_results
