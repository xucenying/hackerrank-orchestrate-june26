"""
context_builder.py — Assembles per-claim context from CSV inputs.

Reads claim row, user history, and evidence requirements,
and returns a structured context dict ready for downstream agents.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from config import EVIDENCE_REQUIREMENTS_CSV, USER_HISTORY_CSV


async def build_context(claim_row: dict, client) -> dict:
    user_history_df = pd.read_csv(USER_HISTORY_CSV)
    match = user_history_df[user_history_df["user_id"] == claim_row["user_id"]]
    user_history = match.iloc[0].to_dict() if not match.empty else {}

    evidence_df = pd.read_csv(EVIDENCE_REQUIREMENTS_CSV)
    relevant = evidence_df[
        evidence_df["claim_object"].str.lower()
        == str(claim_row["claim_object"]).lower()
    ]
    if relevant.empty:
        evidence_requirements = (
            "No specific evidence requirements found for this object type."
        )
    else:
        evidence_requirements = relevant.to_string(index=False)

    return {
        "user_history": user_history,
        "evidence_requirements": evidence_requirements,
    }
