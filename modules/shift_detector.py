"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
from typing import Union, List
from config import SHIFT_PROMPT_FILE
from schemas import FrameExtractionResult, ShiftDetectionResult, TechnicalFailure
from modules.llm_utils import call_llm_with_validation

logger = logging.getLogger(__name__)

def load_shift_prompt():
    """Load the shift detection prompt from file"""
    try:
        with open(SHIFT_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Shift prompt file {SHIFT_PROMPT_FILE} not found")
        return None

def detect_shift(
    frame: FrameExtractionResult,
    constraints: List[str],
    questions: List[str]
) -> Union[ShiftDetectionResult, TechnicalFailure]:
    """
    Detect if a reasoning framework shift has occurred
    """
    prompt = load_shift_prompt()
    if not prompt:
        return TechnicalFailure(
            module="shift_detector",
            reason="Shift detection prompt file not found"
        )

    # Format the reflection process for analysis
    context = f"""INITIAL FRAME:
{json.dumps(frame.dict(), indent=2)}

CONSTRAINTS APPLIED:
{json.dumps(constraints, indent=2)}

QUESTIONS ASKED:
{json.dumps(questions, indent=2)}

Analyze whether a genuine reasoning framework shift has occurred based on the criteria in your instructions."""

    result, error = call_llm_with_validation(
        prompt=prompt,
        context=context,
        response_model=ShiftDetectionResult
    )

    if result:
        # Validate confidence is in proper range
        if not (0.0 <= result.confidence <= 1.0):
            logger.warning(f"Invalid confidence value: {result.confidence}, clamping to 0.0-1.0")
            result.confidence = max(0.0, min(1.0, result.confidence))

        # Set old_frame from initial frame if not provided
        if not result.old_frame:
            result.old_frame = frame.apparent_decision or frame.stated_problem

        logger.info(f"Shift detection completed: {result.shift_detected} (confidence: {result.confidence})")
        return result
    else:
        logger.error(f"Shift detection failed: {error}")
        return TechnicalFailure(
            module="shift_detector",
            reason=f"Shift detection validation failed: {error}"
        )