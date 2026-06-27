"""
image_analyst.py — Analyses claim images using Claude vision.

Loads image files, sends them to claude-sonnet-4-6 with a structured
prompt, and returns per-image analysis results.
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import MAX_TOKENS, MODEL, ROOT_DIR
from prompts.templates import build_image_analyst_prompt

_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


async def analyze_images(claim_row: dict, evidence_requirements: str, client) -> dict:
    image_paths = [
        p.strip() for p in str(claim_row["image_paths"]).split(";") if p.strip()
    ]

    image_blocks = []
    for rel_path in image_paths:
        full_path = ROOT_DIR / rel_path
        media_type = _MEDIA_TYPES.get(full_path.suffix.lower(), "image/jpeg")
        data = base64.standard_b64encode(full_path.read_bytes()).decode("utf-8")
        image_blocks.append(
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": data},
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
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError, AttributeError):
        return {
            "valid_image": False,
            "issue_type": "unknown",
            "object_part": "unknown",
            "severity": "unknown",
            "supporting_image_ids": "none",
            "evidence_standard_met": False,
            "evidence_standard_met_reason": "parse error",
        }
