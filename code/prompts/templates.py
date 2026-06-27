import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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
  issue_type             — exactly one of the values listed below
  object_part            — the specific part of the {claim_object} that is damaged (e.g. "front bumper", "screen", "corner"); use "unknown" if not determinable
  severity               — exactly one of the values listed below
  supporting_image_ids   — list of image identifiers (filenames or indices) that best support the claim; empty list if none
  evidence_standard_met  — boolean: true if the submitted images satisfy the minimum evidence requirements above
  evidence_standard_met_reason — one sentence explaining why the evidence standard was or was not met

severity must be exactly one of: none, low, medium, high, unknown
- none = no damage visible
- low = minor cosmetic damage
- medium = moderate damage affecting function
- high = severe damage
- unknown = cannot determine from images

severity calibration:
- Most everyday visible damage (dents, scratches, cracks, stains) is "medium".
- Reserve "high" for objects that are completely destroyed, crushed, or inoperable.
- Reserve "low" for damage that is barely visible or purely cosmetic.

issue_type must be exactly one of:
dent, scratch, crack, broken_part, torn_packaging, crushed_packaging,
water_damage, stain, none, unknown
- dent: deformation/depression in a surface without breaking it
- scratch: surface mark that removes paint or coating
- crack: fracture line through a material (glass, plastic, casing)
- broken_part: a component is snapped off or structurally separated
- torn_packaging: outer packaging has a rip, hole, or tear
- crushed_packaging: outer packaging is deformed/compressed
- water_damage: liquid has infiltrated the object (swelling, corrosion, short circuit signs)
- stain: discolouration on a surface without structural damage
- none: images are clear and confirm NO damage at all
- unknown: images are too blurry, obstructed, or off-angle to identify the issue type

none vs unknown rule (applies to both issue_type and severity):
- Use "none" ONLY when you can positively confirm that no damage is present.
- Use "unknown" whenever the images are unclear, missing, show the wrong object, or do not let you make a confident determination.

You must use ONLY the exact values listed above. Do not use synonyms,
variations, or capitalization differences. Return only lowercase values.

Rules:
- Base every answer on what is visually present in the images. Do not infer beyond what is visible.
- If multiple images are provided, consider all of them together.
- If the images show the wrong object or clearly contradict the claim, set valid_image=false and issue_type="unknown".
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
- "contradicted": use this when the images actively disprove the claim — for example: the image shows a different object than claimed, the object appears completely undamaged when the user claims damage, or the damage shown is of a completely different type or location than described.
- "not_enough_information": the images are ambiguous, blurry, show the wrong angle, or are missing key evidence needed to confirm or deny the claim.
- When valid_image is false or issue_type is "unknown", prefer "not_enough_information" over "contradicted" unless the wrong-object evidence is unambiguous.
- When the image analysis shows no_damage or issue_type "none" but the user claims damage, use "contradicted".
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
