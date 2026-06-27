import json


def build_image_analyst_prompt(
    claim_object: str,
    user_claim: str,
    evidence_requirements: str,
) -> str:
    return f"""You are an insurance damage-claim analyst. Images are the primary source of truth.

Claim object: {claim_object}
User claim transcript:
{user_claim}

Minimum evidence requirements for this object type:
{evidence_requirements}

Analyze every provided image and return a single JSON object with exactly these keys:

  valid_image            — boolean: true if at least one image clearly shows the claimed object
  issue_type             — one of: physical_damage | liquid_damage | theft | loss | no_damage | unknown
  object_part            — the specific part of the {claim_object} that is damaged (e.g. "front bumper", "screen", "corner"); use "unknown" if not determinable
  severity               — one of: minor | moderate | severe | total_loss | none | unknown
  supporting_image_ids   — list of image identifiers (filenames or indices) that best support the claim; empty list if none
  evidence_standard_met  — boolean: true if the submitted images satisfy the minimum evidence requirements above
  evidence_standard_met_reason — one sentence explaining why the evidence standard was or was not met

Rules:
- Base every answer on what is visually present in the images. Do not infer beyond what is visible.
- If multiple images are provided, consider all of them together.
- Return ONLY valid JSON. No explanation, no markdown, no code fences.
"""


def build_claim_verifier_prompt(
    user_claim: str,
    image_analysis_result: dict,
) -> str:
    analysis_json = json.dumps(image_analysis_result, indent=2)
    return f"""You are an insurance claim verifier.

User claim transcript:
{user_claim}

Image analysis result:
{analysis_json}

Based on the user's stated claim and the image analysis above, decide whether the images support the claim.

Return a JSON object with exactly these keys:

  claim_status               — one of: supported | contradicted | not_enough_information
  claim_status_justification — one or two sentences grounded in specific image evidence that explains the decision

Rules:
- "supported": the images clearly show damage consistent with what the user described.
- "contradicted": the images clearly contradict the user's description (e.g. wrong object, no visible damage).
- "not_enough_information": the images are ambiguous, missing, or do not address key aspects of the claim.
- Ground the justification in concrete observations from the image analysis. Do not speculate.
- Return ONLY valid JSON. No explanation, no markdown, no code fences.
"""


def build_risk_scorer_prompt(
    user_history: dict,
    image_analysis_result: dict,
) -> str:
    history_json = json.dumps(user_history, indent=2)
    analysis_json = json.dumps(image_analysis_result, indent=2)
    return f"""You are an insurance fraud and risk analyst.

User claim history:
{history_json}

Image analysis result:
{analysis_json}

Identify all risk flags that apply to this claim. Choose only from this list:

  none
  blurry_image
  cropped_or_obstructed
  low_light_or_glare
  wrong_angle
  wrong_object
  wrong_object_part
  damage_not_visible
  claim_mismatch
  possible_manipulation
  non_original_image
  text_instruction_present
  user_history_risk
  manual_review_required

Rules:
- Apply "none" only if no other flag applies. Do not combine "none" with other flags.
- Apply "user_history_risk" if the user history shows an elevated number of prior claims or prior rejections.
- Apply "manual_review_required" if you have moderate-to-high uncertainty about any aspect of the claim.
- risk_flags must be a semicolon-separated string of applicable flags (e.g. "blurry_image;wrong_angle").
- Return ONLY valid JSON. No explanation, no markdown, no code fences.

Return a JSON object with exactly this key:

  risk_flags — semicolon-separated string of applicable flags from the list above
"""
