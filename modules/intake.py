"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

def intake(user_input: str) -> dict:
    """
    Classify user input - always routes to Thought Partner reflection
    Returns: {"route": "THOUGHT_PARTNER", "domain": str}
    """

    # Determine domain based on content analysis
    domain = classify_domain(user_input)

    # Thought Partner always does reflection - no routing away
    return {
        "route": "THOUGHT_PARTNER",
        "domain": domain
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