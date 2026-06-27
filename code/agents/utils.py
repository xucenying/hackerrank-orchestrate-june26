import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def extract_json(text: str) -> dict | None:
    """Try three strategies to extract a JSON object from a model response.

    1. Direct json.loads on the full text.
    2. Regex to find the outermost { ... } span.
    3. Extract contents of a ```json ... ``` code fence.

    Returns the parsed dict, or None if all strategies fail.
    """
    # Strategy 1: parse as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: find outermost braces
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 3: code fence
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass

    return None
