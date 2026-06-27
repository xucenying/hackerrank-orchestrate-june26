"""
image_analyst.py — Analyses claim images using Claude vision.

Loads image files, sends them to claude-sonnet-4-6 with a structured
prompt, and returns per-image analysis results.
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.utils import extract_json
from config import DATASET_DIR, MAX_TOKENS, MODEL
from prompts.templates import build_image_analyst_prompt


def _detect_media_type(data: bytes) -> str:
    if data[:4] == b"\x89PNG":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return "image/jpeg"


async def analyze_images(claim_row: dict, evidence_requirements: str, client) -> dict:
    image_paths = [
        p.strip() for p in str(claim_row["image_paths"]).split(";") if p.strip()
    ]

    image_blocks = []
    for rel_path in image_paths:
        full_path = DATASET_DIR / rel_path
        raw_bytes = full_path.read_bytes()
        media_type = _detect_media_type(raw_bytes)
        b64 = base64.standard_b64encode(raw_bytes).decode("utf-8")
        image_blocks.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64},
            }
        )

    prompt = build_image_analyst_prompt(
        claim_object=claim_row["claim_object"],
        user_claim=claim_row["user_claim"],
        evidence_requirements=evidence_requirements,
    )
    content_blocks = image_blocks + [{"type": "text", "text": prompt}]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": content_blocks}],
    )

    raw = response.content[0].text.strip()
    result = extract_json(raw)
    if result is not None:
        return result
    return {
        "valid_image": False,
        "issue_type": "unknown",
        "object_part": "unknown",
        "severity": "unknown",
        "supporting_image_ids": "none",
        "evidence_standard_met": False,
        "evidence_standard_met_reason": "parse error",
    }
