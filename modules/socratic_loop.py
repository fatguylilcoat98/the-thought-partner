"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
from typing import Union, List
from config import SOCRATIC_PROMPT_FILE, SOCRATIC_PASSES
from schemas import FrameExtractionResult, SocraticPassResult, TechnicalFailure
from modules.llm_utils import call_llm_with_validation

logger = logging.getLogger(__name__)

def load_socratic_prompt():
    """Load the Socratic questioning prompt from file"""
    try:
        with open(SOCRATIC_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Socratic prompt file {SOCRATIC_PROMPT_FILE} not found")
        return None

def run_socratic_pass(
    frame: FrameExtractionResult,
    existing_constraints: List[str],
    pass_number: int
) -> Union[SocraticPassResult, TechnicalFailure]:
    """
    Run a single Socratic questioning pass with frame binding
    """
    prompt = load_socratic_prompt()
    if not prompt:
        return TechnicalFailure(
            module="socratic_loop",
            reason="Socratic prompt file not found"
        )

    # Format frame and constraints for the AI
    frame_context = f"""CURRENT FRAME:
Stated Problem: {frame.stated_problem}
Apparent Decision: {frame.apparent_decision}
Hidden Tensions: {frame.hidden_tensions}
Conflicting Values: {frame.conflicting_values}
False Binary: {frame.false_binary}
Missing Factors: {frame.missing_factors}

EXISTING CONSTRAINTS (do NOT repeat these):
{json.dumps(existing_constraints, indent=2)}

PASS NUMBER: {pass_number}

Choose one specific frame dimension to probe with a concrete question about the user's actual situation."""

    result, error = call_llm_with_validation(
        prompt=prompt,
        context=frame_context,
        response_model=SocraticPassResult
    )

    if result:
        # Validate that the constraint isn't repeated
        if result.new_constraint in existing_constraints:
            logger.warning(f"Socratic pass {pass_number} repeated constraint: {result.new_constraint}")
            return TechnicalFailure(
                module="socratic_loop",
                reason=f"Pass {pass_number} repeated existing constraint"
            )

        logger.info(f"Socratic pass {pass_number} successful: {result.frame_dimension}")
        return result
    else:
        logger.error(f"Socratic pass {pass_number} failed: {error}")
        return TechnicalFailure(
            module="socratic_loop",
            reason=f"Pass {pass_number} validation failed: {error}"
        )