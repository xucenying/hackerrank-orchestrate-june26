"""
image_analyst.py — Analyses claim images using Claude vision.

Loads image files, sends them to claude-sonnet-4-6 with a structured
prompt, and returns per-image analysis results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
