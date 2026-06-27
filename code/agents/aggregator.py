"""
aggregator.py — Merges outputs from all agents into the final output row.

Takes results from context_builder, image_analyst, claim_verifier, and
risk_scorer and produces a dict matching the 14-column output schema.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_VALID_SEVERITY = {"none", "low", "medium", "high", "unknown"}
_VALID_ISSUE_TYPE = {
    "dent",
    "scratch",
    "crack",
    "glass_shatter",
    "broken_part",
    "missing_part",
    "torn_packaging",
    "crushed_packaging",
    "water_damage",
    "stain",
    "none",
    "unknown",
}
_VALID_CLAIM_STATUS = {"supported", "contradicted", "not_enough_information"}


def _norm_str(value, valid_set: set, fallback: str) -> str:
    v = str(value).strip().lower() if value is not None else ""
    return v if v in valid_set else fallback


def _to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


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
        "evidence_standard_met": _to_bool(image_analysis.get("evidence_standard_met")),
        "evidence_standard_met_reason": image_analysis.get(
            "evidence_standard_met_reason"
        ),
        "risk_flags": risk_score.get("risk_flags"),
        "issue_type": _norm_str(
            image_analysis.get("issue_type"), _VALID_ISSUE_TYPE, "unknown"
        ),
        "object_part": image_analysis.get("object_part"),
        "claim_status": _norm_str(
            claim_verification.get("claim_status"),
            _VALID_CLAIM_STATUS,
            "not_enough_information",
        ),
        "claim_status_justification": claim_verification.get(
            "claim_status_justification"
        ),
        "supporting_image_ids": image_analysis.get("supporting_image_ids"),
        "valid_image": _to_bool(image_analysis.get("valid_image")),
        "severity": _norm_str(
            image_analysis.get("severity"), _VALID_SEVERITY, "unknown"
        ),
    }
