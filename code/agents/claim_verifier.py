"""
claim_verifier.py — Verifies a damage claim against image evidence.

Compares the user's stated claim with image analysis results and
evidence requirements to determine evidence_standard_met and issue_type.
"""

import json

from code.config import MAX_TOKENS, MODEL
from code.prompts.templates import build_claim_verifier_prompt


async def verify_claim(claim_row: dict, image_analysis: dict, client) -> dict:
    prompt = build_claim_verifier_prompt(
        user_claim=claim_row["user_claim"],
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
        return {
            "claim_status": "not_enough_information",
            "claim_status_justification": "parse error",
        }
