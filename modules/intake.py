"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import re
from config import PROTECTION_KEYWORDS

def intake(user_input: str) -> dict:
    """
    Classify and route user input
    Returns: {"route": "PROTECTION" or "THOUGHT_PARTNER", "domain": str, "trigger_keywords": list}
    """

    # Convert to lowercase for keyword detection
    input_lower = user_input.lower()

    # Check for protection keywords
    trigger_keywords = []
    for keyword in PROTECTION_KEYWORDS:
        if keyword in input_lower:
            trigger_keywords.append(keyword)

    # Determine domain based on content analysis
    domain = classify_domain(user_input)

    # Route decision
    if trigger_keywords:
        return {
            "route": "PROTECTION",
            "domain": domain,
            "trigger_keywords": trigger_keywords
        }
    else:
        return {
            "route": "THOUGHT_PARTNER",
            "domain": domain,
            "trigger_keywords": []
        }

def classify_domain(user_input: str) -> str:
    """
    Classify the domain of the user's input
    Returns: "decision" | "conflict" | "uncertainty" | "planning" | "general"
    """
    input_lower = user_input.lower()

    # Decision indicators
    decision_words = ["should", "choose", "decide", "option", "alternative", "either", "or", "versus"]
    if any(word in input_lower for word in decision_words):
        return "decision"

    # Conflict indicators
    conflict_words = ["conflict", "disagreement", "tension", "against", "opposing", "clash", "dispute"]
    if any(word in input_lower for word in conflict_words):
        return "conflict"

    # Uncertainty indicators
    uncertainty_words = ["unsure", "confused", "unclear", "don't know", "uncertain", "mixed feelings"]
    if any(phrase in input_lower for phrase in uncertainty_words):
        return "uncertainty"

    # Planning indicators
    planning_words = ["plan", "strategy", "approach", "next steps", "future", "goal", "objective"]
    if any(word in input_lower for word in planning_words):
        return "planning"

    return "general"

def route_to_protection(user_input: str, intake_result: dict) -> dict:
    """
    Generate protection mode response
    """
    trigger_keywords_str = ", ".join(intake_result["trigger_keywords"])

    return {
        "mode": "PROTECTION",
        "shift_detected": False,
        "initial_frame": {},
        "final_frame": "",
        "organizing_distinction": "",
        "confidence": 0.0,
        "constraints": [],
        "questions": [],
        "rejected_frames": [],
        "memory": {},
        "output": (
            f"This looks like a situation that may need Protection Mode "
            f"(triggered by: {trigger_keywords_str}). "
            "Reflection is paused. Do you want to switch to Protection Mode to focus on concrete steps?"
        ),
        "steps": [
            {
                "type": "protection",
                "trigger_keywords": intake_result["trigger_keywords"]
            }
        ],
        "mode_detail": "PROTECTION"
    }