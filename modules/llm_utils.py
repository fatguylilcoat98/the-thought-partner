"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import json
import logging
import os
from typing import Type, TypeVar, Optional, Tuple
from pydantic import BaseModel, ValidationError
from anthropic import Anthropic

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def get_client():
    """Get Anthropic client with lazy initialization"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return Anthropic(api_key=api_key)

def call_llm_with_validation(
    prompt: str,
    context: str,
    response_model: Type[T],
    model: str = "claude-sonnet-4-5",
    max_retries: int = 2
) -> Tuple[Optional[T], Optional[str]]:
    """
    Call LLM with structured validation and retry logic

    Returns:
        (validated_result, error_message) - one will be None
    """

    client = get_client()

    for attempt in range(max_retries + 1):
        try:
            # Prepare the full prompt
            full_prompt = f"{prompt}\n\n{context}"
            if attempt > 0:
                full_prompt += f"\n\nPrevious attempt failed validation. Please ensure your response is valid JSON matching the exact schema required."

            logger.info(f"LLM call attempt {attempt + 1} for {response_model.__name__}")

            # Call the model
            message = client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )

            raw_response = message.content[0].text.strip()
            logger.debug(f"Raw LLM response: {raw_response}")

            # Try to parse JSON
            try:
                json_data = json.loads(raw_response)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    return None, f"JSON parsing failed after {max_retries + 1} attempts. Last error: {str(e)}"
                continue

            # Try to validate with Pydantic
            try:
                validated_result = response_model(**json_data)
                logger.info(f"Successfully validated {response_model.__name__} on attempt {attempt + 1}")
                return validated_result, None
            except ValidationError as e:
                logger.warning(f"Pydantic validation error on attempt {attempt + 1}: {e}")
                if attempt == max_retries:
                    return None, f"Schema validation failed after {max_retries + 1} attempts. Last error: {str(e)}"
                continue

        except Exception as e:
            logger.error(f"Unexpected error in LLM call attempt {attempt + 1}: {e}")
            if attempt == max_retries:
                return None, f"LLM call failed after {max_retries + 1} attempts. Last error: {str(e)}"
            continue

    return None, "Maximum retries exceeded"

def create_repair_prompt(original_prompt: str, validation_error: str, response_model: Type[BaseModel]) -> str:
    """Create a repair prompt for retry attempts"""

    schema_example = response_model.schema()

    return f"""
{original_prompt}

IMPORTANT: Your previous response failed validation with this error:
{validation_error}

Please provide a response that exactly matches this JSON schema:
{json.dumps(schema_example, indent=2)}

Return ONLY valid JSON. No markdown, no commentary, no extra text.
"""