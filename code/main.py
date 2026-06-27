"""
main.py — Entry point for the damage claim verification system.

Reads dataset/claims.csv, processes each claim concurrently via
asyncio.gather, and writes results to output.csv.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

import anthropic
import pandas as pd

from code.agents.aggregator import aggregate
from code.agents.claim_verifier import verify_claim
from code.agents.context_builder import build_context
from code.agents.image_analyst import analyze_images
from code.agents.risk_scorer import score_risk
from code.config import (
    ANTHROPIC_API_KEY,
    CLAIMS_CSV,
    MAX_CONCURRENT_CLAIMS,
    OUTPUT_CSV,
)

OUTPUT_COLUMNS = [
    "user_id",
    "image_paths",
    "user_claim",
    "claim_object",
    "evidence_standard_met",
    "evidence_standard_met_reason",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "claim_status_justification",
    "supporting_image_ids",
    "valid_image",
    "severity",
]


async def process_claim(claim_row: dict, client, semaphore: asyncio.Semaphore) -> dict:
    user_id = claim_row.get("user_id", "unknown")
    print(f"Processing claim {user_id}...")

    async with semaphore:
        try:
            context = await build_context(claim_row, client)
            image_analysis = await analyze_images(
                claim_row, context["evidence_requirements"], client
            )
            claim_verification, risk_score = await asyncio.gather(
                verify_claim(claim_row, image_analysis, client),
                score_risk(claim_row, image_analysis, context["user_history"], client),
            )
            return aggregate(
                claim_row, context, image_analysis, claim_verification, risk_score
            )
        except Exception as exc:
            print(f"  Error processing claim {user_id}: {exc}")
            return {
                "user_id": user_id,
                "image_paths": claim_row.get("image_paths"),
                "user_claim": claim_row.get("user_claim"),
                "claim_object": claim_row.get("claim_object"),
                "evidence_standard_met": None,
                "evidence_standard_met_reason": None,
                "risk_flags": "manual_review_required",
                "issue_type": None,
                "object_part": None,
                "claim_status": "not_enough_information",
                "claim_status_justification": str(exc),
                "supporting_image_ids": None,
                "valid_image": None,
                "severity": None,
            }


async def run_pipeline(input_csv, output_csv) -> None:
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CLAIMS)

    df = pd.read_csv(input_csv)
    rows = df.to_dict(orient="records")

    results = await asyncio.gather(
        *[process_claim(row, client, semaphore) for row in rows]
    )

    out_df = pd.DataFrame(results, columns=OUTPUT_COLUMNS)
    out_df.to_csv(output_csv, index=False)

    print(f"\nDone. {len(results)} claim(s) processed → {output_csv}")


def main() -> None:
    asyncio.run(run_pipeline(CLAIMS_CSV, OUTPUT_CSV))


if __name__ == "__main__":
    main()
