"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import re
from config import PROTECTION_KEYWORDS

def classify_protection_risk(user_input: str) -> dict:
    """
    Classify protection risk level with nuanced analysis
    Returns: {"level": "high"|"medium"|"low", "triggers": [], "reason": ""}
    """
    input_lower = user_input.lower()

    # HIGH RISK: Immediate concrete threats requiring hard stop
    high_risk_patterns = [
        # Time-sensitive deadlines
        r"(\d+\s+(days?|hours?|minutes?)\s+(to|until|before))",
        r"(today|tomorrow|this week|by\s+\w+day)",
        r"(deadline|due date|court date|eviction notice)",

        # Active immediate threats
        r"(changing\s+the\s+locks|being\s+evicted|getting\s+fired\s+tomorrow)",
        r"(police\s+(are\s+)?coming|being\s+arrested|warrant)",
        r"(already\s+sent|gave\s+them|wired\s+funds|sent\s+them\s+money)",
        r"(in\s+danger|might\s+hurt|going\s+to\s+harm|violence)",
        r"(served\s+papers|legal\s+action\s+filed|lawsuit\s+started)",

        # Imminent financial harm
        r"(account\s+frozen|cards\s+cancelled|credit\s+destroyed)",
        r"(repo\s+man|repossession\s+scheduled|taking\s+my\s+car)",
    ]

    # MEDIUM RISK: Potential consequences but can reflect
    medium_risk_patterns = [
        # Workplace pressure/retaliation
        r"(boss\s+is\s+(pressuring|forcing|making\s+me)|workplace|manager)",
        r"(losing\s+my\s+job|getting\s+fired|retaliation|whistleblow)",
        r"(report\s+it|push\s+back|speak\s+up|file\s+complaint)",

        # Authority/power dynamics
        r"(landlord|employer|supervisor|teacher|doctor|lawyer)",
        r"(pressure\s+on\s+me|go\s+along\s+with|cover\s+up|hide)",

        # Legal/ethical concerns (not immediate)
        r"(legal\s+advice|attorney|discrimination|harassment)",
        r"(something\s+(feels\s+)?wrong|not\s+right|unethical|illegal)",
        r"(cutting\s+corners|blame|fraud|cover)",

        # Financial pressure (not immediate)
        r"(debt\s+collector|credit\s+card|loan|mortgage|rent)",
        r"(can't\s+afford|running\s+out\s+of\s+money|broke)",
    ]

    # REFLECTION INDICATORS: Override protection if clearly seeking perspective
    reflection_indicators = [
        r"(how\s+should\s+i\s+think|need\s+perspective|how\s+to\s+approach)",
        r"(i'm\s+(torn|stuck|confused)|don't\s+know\s+what|can't\s+decide)",
        r"(part\s+of\s+me|going\s+back\s+and\s+forth|conflicted)",
        r"(should\s+i|what\s+if|how\s+do\s+i\s+decide)",
    ]

    triggers = []
    reasons = []

    # Check for high risk patterns
    for pattern in high_risk_patterns:
        if re.search(pattern, input_lower):
            triggers.append(pattern)
            reasons.append("immediate threat detected")

    if triggers:
        return {
            "level": "high",
            "triggers": triggers[:3],  # Limit to first 3 matches
            "reason": "Immediate concrete risk requiring urgent action"
        }

    # Check for reflection indicators (override medium risk)
    reflection_found = any(re.search(pattern, input_lower) for pattern in reflection_indicators)

    # Check for medium risk patterns
    for pattern in medium_risk_patterns:
        if re.search(pattern, input_lower):
            triggers.append(pattern)
            reasons.append("potential consequences")

    if triggers and not reflection_found:
        return {
            "level": "medium",
            "triggers": triggers[:3],
            "reason": "Potential real-world consequences but suitable for reflection"
        }
    elif triggers and reflection_found:
        return {
            "level": "low",  # Reflection request overrides medium risk
            "triggers": triggers[:3],
            "reason": "User explicitly seeking perspective despite potential consequences"
        }

    # Default to low risk
    return {
        "level": "low",
        "triggers": [],
        "reason": "No significant risk indicators detected"
    }

def intake(user_input: str) -> dict:
    """
    Classify and route user input with nuanced risk assessment
    Returns: {"route": str, "domain": str, "risk": dict}
    """

    # Perform risk classification
    risk = classify_protection_risk(user_input)

    # Determine domain based on content analysis
    domain = classify_domain(user_input)

    return {
        "route": "PROTECTION" if risk["level"] == "high" else "THOUGHT_PARTNER",
        "domain": domain,
        "risk": risk
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

def route_to_protection(user_input: str, risk: dict) -> dict:
    """
    Generate high-risk protection mode response
    """
    trigger_summary = f"urgency detected: {', '.join(risk['triggers'][:2])}" if risk["triggers"] else "immediate risk"

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
        "memory": {
            "protection_trigger": risk["triggers"],
            "risk_level": risk["level"],
            "context_identified": risk["reason"]
        },
        "output": "This looks urgent and could require concrete steps. Reflection is paused so we can focus on protection.",
        "steps": [
            {
                "type": "protection",
                "trigger_keywords": risk["triggers"],
                "risk_level": risk["level"],
                "context": risk["reason"]
            }
        ],
        "mode_detail": "PROTECTION"
    }