"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, SHIFT_PROMPT_FILE

logger = logging.getLogger(__name__)

def get_client():
    """Get Anthropic client with lazy initialization"""
    return Anthropic(api_key=ANTHROPIC_API_KEY)

def load_shift_prompt():
    """Load the shift detection prompt from file"""
    try:
        with open(SHIFT_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Shift prompt file {SHIFT_PROMPT_FILE} not found, using default")
        return """You are a Shift Detector.
Your job is to decide whether a reasoning framework shift has occurred.

A shift exists when ALL are true:

A new organizing distinction emerges.
It restructures how the problem is understood.
The system would now reason FROM this frame, not just ABOUT it.
It resolves multiple conflicting constraints simultaneously.

A shift is NOT:

better wording,
more detail,
a softer binary,
a simple restatement of the initial frame.

You will receive:

the initial frame,
the list of constraints,
the list of questions asked.

Decide whether a shift has occurred and describe it.

Return ONLY valid JSON:
{
"shift_detected": true/false,
"new_frame": "",
"old_frame": "",
"organizing_distinction": "",
"explanation": "",
"confidence": 0.0
}"""

def detect_shift(frame: dict, constraints: list, questions: list) -> dict:
    """
    Detect if a reasoning framework shift has occurred
    Returns shift detection result
    """
    try:
        prompt = load_shift_prompt()
        client = get_client()

        # Format the context for the AI
        context = f"""Initial frame:
{json.dumps(frame, indent=2)}

Constraints applied:
{json.dumps(constraints, indent=2)}

Questions asked:
{json.dumps(questions, indent=2)}

Analyze whether a reasoning framework shift has occurred."""

        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{context}"
                }
            ]
        )

        response_text = message.content[0].text.strip()

        try:
            result = json.loads(response_text)

            # Validate and set defaults
            shift_result = {
                "shift_detected": result.get("shift_detected", False),
                "new_frame": result.get("new_frame", ""),
                "old_frame": result.get("old_frame", frame.get("stated_problem", "")),
                "organizing_distinction": result.get("organizing_distinction", ""),
                "explanation": result.get("explanation", ""),
                "confidence": float(result.get("confidence", 0.0))
            }

            # Ensure confidence is between 0 and 1
            if shift_result["confidence"] > 1.0:
                shift_result["confidence"] = shift_result["confidence"] / 100.0

            return shift_result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse shift detection JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Return fallback - no shift detected
            return {
                "shift_detected": False,
                "new_frame": "",
                "old_frame": frame.get("stated_problem", ""),
                "organizing_distinction": "",
                "explanation": "Parsing error - could not detect shift",
                "confidence": 0.0
            }

    except Exception as e:
        logger.error(f"Error in detect_shift: {e}")
        # Return fallback - no shift detected
        return {
            "shift_detected": False,
            "new_frame": "",
            "old_frame": frame.get("stated_problem", ""),
            "organizing_distinction": "",
            "explanation": "API error - could not detect shift",
            "confidence": 0.0
        }