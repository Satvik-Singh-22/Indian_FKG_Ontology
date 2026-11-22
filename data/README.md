# Data

## `raw/`

Source recipe datasets. These are the inputs to the KG construction pipeline
(`pipeline/dataset_loader.py`).

| File | Description |
| --- | --- |
| `cleaned_db.csv` | Dataset 1 — no diet/course columns; ~50k rows |
| `cuisines.csv` | Dataset 2 — includes cuisine, course and diet labels |

> `data/raw/cuisines.csv` is the full recipe dataset. It is **not** the small
> `URI,Label` cuisine vocabulary from the early ontology build; that file is
> archived at `legacy/data/cuisine_labels.csv`.

## `curated/`

Human-reviewable artifacts used by retrieval and generation.

| File | Produced by | Used by |
| --- | --- | --- |
| `ingredient_canonical.json` | offline Groq pass + manual review | `fkg/ingredient_expander.py` |
| `ingredient_groups_review.csv` | review export of the canonical map | manual review |
| `kg_vocab.json` | `python -m fkg.query_parser --build-vocab` | `fkg/query_parser.py` |
| `recipe_courses.json` | `scripts/classify_course.py --build` | `fkg/kg_store.py`, `fkg/hybrid_retriever.py` |
| `recipe_courses_review.csv` | review export of the course map | manual review |

The built knowledge graph lives at `pipeline/output/food_kg.ttl` and is
generated, not tracked. `ontology/` holds the earlier standalone Turtle
deliverables.
