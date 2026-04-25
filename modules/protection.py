"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

def handle_protection_mode(user_input: str, trigger_keywords: list) -> dict:
    """
    Handle protection mode routing and response generation
    """

    # Generate protection message based on trigger keywords
    keyword_specific_messages = {
        "eviction": "This involves housing law and tenant rights.",
        "scam": "This involves potential fraud or consumer protection.",
        "deadline": "This involves time-sensitive legal or financial matters.",
        "fraud": "This involves potential criminal activity or consumer protection.",
        "threat": "This involves personal safety or potential criminal activity.",
        "lockout": "This involves tenant rights or property access.",
        "urgent": "This appears to be time-sensitive.",
        "legal": "This involves legal rights or procedures.",
        "lawsuit": "This involves active legal proceedings.",
        "court": "This involves legal proceedings or court requirements.",
        "arrested": "This involves criminal justice or legal representation.",
        "violence": "This involves personal safety or potential criminal activity.",
        "stolen": "This involves potential theft or property crimes.",
        "fired": "This involves employment law and worker rights.",
        "harassment": "This involves civil rights or workplace protections.",
        "discrimination": "This involves civil rights and legal protections.",
        "warrant": "This involves criminal proceedings or legal obligations."
    }

    # Get specific context based on keywords
    context_messages = []
    for keyword in trigger_keywords:
        if keyword in keyword_specific_messages:
            context_messages.append(keyword_specific_messages[keyword])

    context_text = " ".join(set(context_messages))  # Remove duplicates

    # Generate protection response
    protection_message = f"""This looks like a situation that may need Protection Mode (triggered by: {', '.join(trigger_keywords)}).

{context_text}

Reflection is paused. Protection Mode focuses on immediate, concrete steps rather than exploring different perspectives.

Do you want to switch to Protection Mode to focus on actionable steps for your situation?"""

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
            "protection_trigger": trigger_keywords,
            "context_identified": context_text
        },
        "output": protection_message,
        "steps": [
            {
                "type": "protection",
                "trigger_keywords": trigger_keywords,
                "context": context_text
            }
        ],
        "mode_detail": "PROTECTION"
    }