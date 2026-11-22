# Indian Food Knowledge Graph

An RDF knowledge graph for Indian recipes, built from curated recipe data and designed for structured search and downstream retrieval-augmented generation.

| Graph snapshot | Source data |
| --- | ---: |
| **1,998 recipes** · **44,305 RDF triples** | **170,533 recipes** across two source CSVs |

The repository includes the construction pipeline, source datasets, ontology deliverables, and the approved Turtle graph artifact.

## Repository layout

- `pipeline/` — ingestion, LLM-assisted parsing, ingredient resolution, and RDF graph construction.
- `data/` — source CSVs and curated review data.
- `ontology/` — standalone ontology Turtle files.
- `artifacts/food_kg.ttl` — versioned graph snapshot for downstream consumers.

## Requirements and setup

Python 3.11.14 is pinned in `.python-version`. From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `GROQ_API_KEY` in `.env` before running LLM-assisted pipeline steps. Optional notebook dependencies are in `requirements-dev.txt`.

The pipeline uses `data/raw/cleaned_db.csv` by default. Set `DATASET_NUMBER=2` in `.env` to use `cuisines.csv`; use `START_INDEX`, `END_INDEX`, and `INTERACTIVE_REVIEW` to control a run.

## Build and validate

Run commands from the repository root so Python resolves the local packages:

```bash
python -m pipeline.run_pipeline
python -m pipeline.sparql_tests
```

The pipeline writes its working graph to `pipeline/output/food_kg.ttl` and resumable state to `pipeline/state/`. The approved, checked-in graph is [`artifacts/food_kg.ttl`](artifacts/food_kg.ttl).

## Graph handoff

Validate a generated graph before promoting it to `artifacts/food_kg.ttl`. Tag graph updates so downstream applications can pin a known version. API keys, checkpoints, and intermediate build output are excluded from Git.

See `data/README.md` for data details and `docs/reports/README.md` for project reports.
