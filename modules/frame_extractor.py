"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import logging
from typing import Union, Tuple
from config import FRAME_PROMPT_FILE
from schemas import FrameExtractionResult, TechnicalFailure
from modules.llm_utils import call_llm_with_validation

logger = logging.getLogger(__name__)

def load_frame_prompt():
    """Load the frame extraction prompt from file"""
    try:
        with open(FRAME_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"Frame prompt file {FRAME_PROMPT_FILE} not found")
        return None

def extract_frame(user_input: str) -> Union[FrameExtractionResult, TechnicalFailure]:
    """
    Extract the initial frame from user input using Claude with validation
    """
    prompt = load_frame_prompt()
    if not prompt:
        return TechnicalFailure(
            module="frame_extractor",
            reason="Frame prompt file not found"
        )

    context = f"User Input:\n{user_input}"

    result, error = call_llm_with_validation(
        prompt=prompt,
        context=context,
        response_model=FrameExtractionResult
    )

    if result:
        logger.info("Frame extraction successful")
        return result
    else:
        logger.error(f"Frame extraction failed: {error}")
        return TechnicalFailure(
            module="frame_extractor",
            reason=error or "Unknown extraction error"
        )