"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, FRAME_PROMPT_FILE

logger = logging.getLogger(__name__)

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def load_frame_prompt():
    """Load the frame extraction prompt from file"""
    try:
        with open(FRAME_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Frame prompt file {FRAME_PROMPT_FILE} not found, using default")
        return """You are a Frame Extractor. DO NOT solve the problem.
Your only job is to extract how this problem is currently framed.
Do not give advice or options. Do not speak to the user.
Return ONLY valid JSON. No preamble. No markdown.

Extract the following fields:

stated_problem: the user's own description of what is going on.
apparent_decision: what they seem to think they are deciding between.
hidden_tensions: list of pressures or worries that are present but not cleanly named.
conflicting_values: list of values or goals that seem to be in conflict.
false_binary: any either/or the user is treating as the only options.
missing_factors: list of important factors that are not being discussed but seem relevant.

Expected JSON:
{
  "stated_problem": "",
  "apparent_decision": "",
  "hidden_tensions": [],
  "conflicting_values": [],
  "false_binary": "",
  "missing_factors": []
}"""

def extract_frame(user_input: str) -> dict:
    """
    Extract the initial frame from user input using Claude
    """
    try:
        prompt = load_frame_prompt()

        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\nUser Input:\n{user_input}"
                }
            ]
        )

        response_text = message.content[0].text.strip()

        # Parse JSON response
        try:
            frame = json.loads(response_text)

            # Validate required fields
            required_fields = ["stated_problem", "apparent_decision", "hidden_tensions",
                             "conflicting_values", "false_binary", "missing_factors"]

            for field in required_fields:
                if field not in frame:
                    frame[field] = [] if field.endswith(('tensions', 'values', 'factors')) else ""

            return frame

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse frame extraction JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Return fallback frame
            return {
                "stated_problem": user_input[:200] + "..." if len(user_input) > 200 else user_input,
                "apparent_decision": "unclear",
                "hidden_tensions": ["parsing error - using fallback"],
                "conflicting_values": [],
                "false_binary": "",
                "missing_factors": []
            }

    except Exception as e:
        logger.error(f"Error in extract_frame: {e}")
        # Return fallback frame
        return {
            "stated_problem": user_input[:200] + "..." if len(user_input) > 200 else user_input,
            "apparent_decision": "unclear",
            "hidden_tensions": ["API error - using fallback"],
            "conflicting_values": [],
            "false_binary": "",
            "missing_factors": []
        }