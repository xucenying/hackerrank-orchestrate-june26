"""
aggregator.py — Merges outputs from all agents into the final output row.

Takes results from context_builder, image_analyst, claim_verifier, and
risk_scorer and produces a dict matching the 14-column output schema.
"""


def aggregate(
    claim_row: dict,
    context: dict,
    image_analysis: dict,
    claim_verification: dict,
    risk_score: dict,
) -> dict:
    return {
        "user_id": claim_row["user_id"],
        "image_paths": claim_row["image_paths"],
        "user_claim": claim_row["user_claim"],
        "claim_object": claim_row["claim_object"],
        "evidence_standard_met": image_analysis.get("evidence_standard_met"),
        "evidence_standard_met_reason": image_analysis.get(
            "evidence_standard_met_reason"
        ),
        "risk_flags": risk_score.get("risk_flags"),
        "issue_type": image_analysis.get("issue_type"),
        "object_part": image_analysis.get("object_part"),
        "claim_status": claim_verification.get("claim_status"),
        "claim_status_justification": claim_verification.get(
            "claim_status_justification"
        ),
        "supporting_image_ids": image_analysis.get("supporting_image_ids"),
        "valid_image": image_analysis.get("valid_image"),
        "severity": image_analysis.get("severity"),
    }
