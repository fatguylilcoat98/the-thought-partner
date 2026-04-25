"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, SOCRATIC_PROMPT_FILE, SOCRATIC_PASSES

logger = logging.getLogger(__name__)

def get_client():
    """Get Anthropic client with lazy initialization"""
    return Anthropic(api_key=ANTHROPIC_API_KEY)

def load_socratic_prompt():
    """Load the Socratic questioning prompt from file"""
    try:
        with open(SOCRATIC_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Socratic prompt file {SOCRATIC_PROMPT_FILE} not found, using default")
        return """You are a Socratic Reflection Engine.
You talk to the internal system, NOT directly to the user.
You see the current frame and the constraints so far.
Your job is to introduce NEW constraints that increase clarity by increasing tension.

RULES — absolute:

You MUST NOT answer the problem.
You MUST NOT resolve the tension.
You MUST NOT repeat a prior constraint.
Ask exactly ONE question.
The question must introduce a NEW constraint or angle.
Each question must increase productive tension, not relieve it.
You may be concrete and specific.

Return ONLY valid JSON:
{"question": "", "new_constraint": ""}"""

def run_socratic_pass(frame: dict, constraints: list) -> dict:
    """
    Run a single Socratic questioning pass
    Returns: {"question": str, "new_constraint": str}
    """
    try:
        prompt = load_socratic_prompt()
        client = get_client()

        # Format the context for the AI
        context = f"""Current frame:
{json.dumps(frame, indent=2)}

Constraints so far:
{json.dumps(constraints, indent=2)}

Generate the next Socratic question and constraint."""

        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=500,
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

            # Validate required fields
            if "question" not in result or "new_constraint" not in result:
                raise ValueError("Missing required fields")

            return {
                "question": result["question"],
                "new_constraint": result["new_constraint"]
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Socratic pass JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Return fallback
            return {
                "question": f"What aspect of this situation requires deeper examination? (Pass {len(constraints) + 1})",
                "new_constraint": f"parsing_error_constraint_{len(constraints) + 1}"
            }

    except Exception as e:
        logger.error(f"Error in run_socratic_pass: {e}")
        # Return fallback
        return {
            "question": f"What underlying assumption might be limiting the framing? (Pass {len(constraints) + 1})",
            "new_constraint": f"api_error_constraint_{len(constraints) + 1}"
        }