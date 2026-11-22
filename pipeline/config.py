"""
Configuration loader for the FKG pipeline.
Reads settings from .env file in the project root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from rdflib import Namespace

# ── Load .env from project root ───────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Namespaces ─────────────────────────────────────────────────────────────
FKG       = Namespace("http://fkg.iiitd.ac.in/ontology#")
HEALS     = Namespace("http://purl.org/heals/food/")
HEALS_ING = Namespace("http://purl.org/heals/ingredient/")

# ── Groq LLM ──────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Dataset & processing ──────────────────────────────────────────────────
DATASET_NUMBER = int(os.getenv("DATASET_NUMBER", "1"))
START_INDEX     = int(os.getenv("START_INDEX", "0"))
END_INDEX       = int(os.getenv("END_INDEX", "100"))

# Dataset file paths (relative to project root)
DS1_PATH = PROJECT_ROOT / "data" / "raw" / "cleaned_db.csv"
DS2_PATH = PROJECT_ROOT / "data" / "raw" / "cuisines.csv"

# ── Interactive review ─────────────────────────────────────────────────────
INTERACTIVE_REVIEW = os.getenv("INTERACTIVE_REVIEW", "True").lower() in ("true", "1", "yes")

# ── Rate limiting ─────────────────────────────────────────────────────────
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "2.1"))
BATCH_SIZE       = int(os.getenv("BATCH_SIZE", "10"))

# ── Output ─────────────────────────────────────────────────────────────────
OUTPUT_TTL = Path(os.getenv("OUTPUT_TTL", str(PROJECT_ROOT / "pipeline" / "output" / "food_kg.ttl")))
if not OUTPUT_TTL.is_absolute():
    OUTPUT_TTL = PROJECT_ROOT / OUTPUT_TTL

# ── State persistence ─────────────────────────────────────────────────────
STATE_DIR = Path(os.getenv("STATE_DIR", str(PROJECT_ROOT / "pipeline" / "state")))
if not STATE_DIR.is_absolute():
    STATE_DIR = PROJECT_ROOT / STATE_DIR

# ── Logging ────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def print_config():
    """Print current configuration for debugging."""
    print("=" * 60)
    print("  FKG Pipeline Configuration")
    print("=" * 60)
    print(f"  GROQ_MODEL        : {GROQ_MODEL}")
    print(f"  DATASET_NUMBER    : {DATASET_NUMBER}")
    print(f"  START_INDEX       : {START_INDEX}")
    print(f"  END_INDEX         : {END_INDEX}")
    print(f"  INTERACTIVE_REVIEW: {INTERACTIVE_REVIEW}")
    print(f"  RATE_LIMIT_DELAY  : {RATE_LIMIT_DELAY}")
    print(f"  BATCH_SIZE        : {BATCH_SIZE}")
    print(f"  OUTPUT_TTL        : {OUTPUT_TTL}")
    print(f"  STATE_DIR         : {STATE_DIR}")
    print("=" * 60)
