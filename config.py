"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model Configuration
DEFAULT_MODEL = "claude-sonnet-4-5"

# Socratic Loop Configuration
SOCRATIC_PASSES = 6


# Prompt File Paths
PROMPTS_DIR = "prompts"
FRAME_PROMPT_FILE = os.path.join(PROMPTS_DIR, "frame_prompt.txt")
SOCRATIC_PROMPT_FILE = os.path.join(PROMPTS_DIR, "socratic_prompt.txt")
SHIFT_PROMPT_FILE = os.path.join(PROMPTS_DIR, "shift_prompt.txt")
COMPOSE_PROMPT_FILE = os.path.join(PROMPTS_DIR, "compose_prompt.txt")

# UI Configuration
UI_DIR = "ui"

def validate_config():
    """Validate that required configuration is present"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    # Check that prompt files exist
    for prompt_file in [FRAME_PROMPT_FILE, SOCRATIC_PROMPT_FILE, SHIFT_PROMPT_FILE, COMPOSE_PROMPT_FILE]:
        if not os.path.exists(prompt_file):
            print(f"Warning: Prompt file {prompt_file} not found")

if __name__ == "__main__":
    validate_config()
    print("Configuration validated successfully")