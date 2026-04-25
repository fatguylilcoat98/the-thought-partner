"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import logging
import os
from anthropic import Anthropic
from config import DEFAULT_MODEL, COMPOSE_PROMPT_FILE

logger = logging.getLogger(__name__)

def get_client():
    """Get Anthropic client with lazy initialization"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return Anthropic(api_key=api_key)

def load_compose_prompt():
    """Load the output composition prompt from file"""
    try:
        with open(COMPOSE_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Compose prompt file {COMPOSE_PROMPT_FILE} not found, using default")
        return """You are the voice of Thought Partner.
You only speak after a reasoning framework shift OR after the reflection loop is exhausted.

If a shift occurred:

Briefly acknowledge what they came in with (in their terms).
Name what changed (the new distinction or frame).
State the new frame clearly, in plain language.
Identify the real tension that is now visible.
Offer ONE grounded next step they could take.
Offer ONE follow-up question they can keep thinking about.

If NO shift occurred:

Be honest — no better frame was found.
Name the main unresolved constraints or uncertainties.
Do NOT pretend to have an answer.
Invite them to rephrase or bring a smaller slice if appropriate.

Tone: grounded, direct, respectful.
Not therapeutic. Not preachy. No false certainty.

Return plain text for a human reader. No JSON, no markdown."""

def compose_output(user_input: str, memory_obj: dict, shift_result: dict) -> str:
    """
    Compose the final output using the memory and shift result
    """
    try:
        prompt = load_compose_prompt()
        client = get_client()

        # Prepare context for the composer
        context = f"""User's original input:
{user_input}

Memory of the reflection process:
Initial frame: {memory_obj['initial_frame']}
Shift detected: {shift_result['shift_detected']}
Final frame: {memory_obj['final_frame']}
Organizing distinction: {memory_obj['organizing_distinction']}
Confidence: {memory_obj['confidence']}
Explanation: {memory_obj['shift_explanation']}
Constraints applied: {memory_obj['constraints_applied']}
Questions asked: {memory_obj['questions_asked']}
Rejected frames: {len(memory_obj['rejected_frames'])} alternatives explored

Compose the response to the user based on whether a shift occurred."""

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
        return response_text

    except Exception as e:
        logger.error(f"Error in compose_output: {e}")

        # Fallback composition based on whether shift was detected
        if shift_result["shift_detected"]:
            return f"""I notice you came in thinking about: {memory_obj['initial_frame'].get('stated_problem', 'your situation')}

Through our reflection, a different frame emerged: {memory_obj['organizing_distinction']}

The real tension seems to be: {memory_obj['final_frame']}

One step you could take: Consider how this new framing changes your available options.

Something to keep thinking about: What does this new perspective reveal about what really matters here?"""
        else:
            return f"""I worked through your situation — {memory_obj['initial_frame'].get('stated_problem', 'what you described')} — but didn't find a clearer frame.

The main tensions that remain unresolved: {', '.join(memory_obj['constraints_applied'][-3:]) if memory_obj['constraints_applied'] else 'multiple competing considerations'}

Rather than forcing an answer, it might help to bring a smaller piece of this or rephrase what's most pressing right now.

What aspect feels most urgent or confusing?"""