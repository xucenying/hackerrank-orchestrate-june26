"""
risk_scorer.py — Computes risk flags from user history and claim data.

Applies risk rules based on historical claim frequency, claim object,
and severity to populate the risk_flags field.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import MAX_TOKENS, MODEL
from prompts.templates import build_risk_scorer_prompt


async def score_risk(
    claim_row: dict, image_analysis: dict, user_history: dict, client
) -> dict:
    prompt = build_risk_scorer_prompt(
        user_history=user_history,
        image_analysis_result=image_analysis,
    )

    response = await client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        return json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError, AttributeError):
        return {"risk_flags": "manual_review_required"}
