"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import logging
from typing import Union
from config import COMPOSE_PROMPT_FILE
from schemas import RunStatus, ShiftDetectionResult, TechnicalFailure
from modules.llm_utils import call_llm_with_validation
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ComposerResult(BaseModel):
    output: str

def load_compose_prompt():
    """Load the output composition prompt from file"""
    try:
        with open(COMPOSE_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Compose prompt file {COMPOSE_PROMPT_FILE} not found")
        return None

def compose_output(
    user_input: str,
    memory_obj: dict,
    shift_result: Union[ShiftDetectionResult, TechnicalFailure],
    run_status: RunStatus
) -> str:
    """
    Compose the final output based on the reflection outcome
    """

    # Handle technical failure immediately
    if run_status == RunStatus.TECHNICAL_FAILURE:
        return "The reflection process hit a technical issue before a reliable reframe could be produced. Please try rephrasing your question or try again."

    # For successful runs, use the LLM to compose output
    prompt = load_compose_prompt()
    if not prompt:
        return "Technical issue: Could not load output composition instructions."

    # Determine outcome type for context
    if run_status == RunStatus.SHIFT_DETECTED:
        outcome_context = f"""REFLECTION OUTCOME: Framework shift detected

Original input: {user_input}

Initial frame: {memory_obj.get('initial_frame', {})}
Final frame: {shift_result.new_frame if hasattr(shift_result, 'new_frame') else 'Unknown'}
Organizing distinction: {shift_result.organizing_distinction if hasattr(shift_result, 'organizing_distinction') else 'Unknown'}
Confidence: {shift_result.confidence if hasattr(shift_result, 'confidence') else 0}

Constraints explored: {memory_obj.get('constraints_applied', [])}
Questions asked: {memory_obj.get('questions_asked', [])}"""

    else:  # NO_SHIFT_FOUND
        outcome_context = f"""REFLECTION OUTCOME: No framework shift found

Original input: {user_input}

Initial frame: {memory_obj.get('initial_frame', {})}
Constraints explored: {memory_obj.get('constraints_applied', [])}
Questions asked: {memory_obj.get('questions_asked', [])}

The reflection process completed successfully but no better frame emerged."""

    result, error = call_llm_with_validation(
        prompt=prompt,
        context=outcome_context,
        response_model=ComposerResult
    )

    if result:
        return result.output
    else:
        logger.error(f"Output composition failed: {error}")
        # Provide fallback based on run status
        if run_status == RunStatus.SHIFT_DETECTED:
            return f"I found a different way to frame your question, but encountered a technical issue in composing the response. The key insight was: {getattr(shift_result, 'organizing_distinction', 'framework shift detected')}"
        else:
            return f"I explored your question through several angles but didn't find a clearer frame. The main tensions remain: {', '.join(memory_obj.get('constraints_applied', [])[-3:])}"