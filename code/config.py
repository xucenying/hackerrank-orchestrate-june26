"""
config.py — Central configuration and environment variable loading.

Reads ANTHROPIC_API_KEY and any other runtime settings from the
environment; exposes typed constants used across the codebase.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY is not set. "
        "Export it in your shell or add it to a .env file."
    )

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
MAX_CONCURRENT_CLAIMS = 5

ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT_DIR / "dataset"
CLAIMS_CSV = DATASET_DIR / "claims.csv"
SAMPLE_CLAIMS_CSV = DATASET_DIR / "sample_claims.csv"
USER_HISTORY_CSV = DATASET_DIR / "user_history.csv"
EVIDENCE_REQUIREMENTS_CSV = DATASET_DIR / "evidence_requirements.csv"
IMAGES_DIR = DATASET_DIR / "images"
OUTPUT_CSV = ROOT_DIR / "output.csv"
