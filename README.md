# Thought Partner v0.2
## The Good Neighbor Guard

**Built by Christopher Hughes · Sacramento, CA**  
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)  
*Truth · Safety · We Got Your Back*

---

## Overview

Thought Partner is a **reflection-native AI system** that fundamentally changes how AI assists with complex thinking. 

**This is NOT a chatbot.** This is NOT a generic Q&A system.

Thought Partner delays answering until it has improved the problem frame through a structured internal Socratic loop. The visible reasoning panel on the right side of the UI is not decoration — **it IS the product**.

### Tagline
*"We don't answer your question. We fix the question first."*

---

## How It Works

### The Pipeline

1. **Intake**: Route urgent situations to Protection Mode or continue to reflection
2. **Frame Extraction**: Identify how the problem is currently framed (without solving)
3. **Socratic Loop**: 3-6 passes of questioning to introduce productive constraints
4. **Shift Detection**: Determine if a reasoning framework shift has occurred
5. **Memory Building**: Create inspectable trail of the reflection process
6. **Output Composition**: Respond based on new frame or honest no-shift state

### Protection Mode

Certain keywords trigger immediate routing to Protection Mode:
- `eviction`, `scam`, `deadline`, `fraud`, `threat`, `lockout`, `urgent`
- `legal`, `lawsuit`, `court`, `arrested`, `violence`, `stolen` 
- `fired`, `harassment`, `discrimination`, `warrant`

When triggered, reflection is paused and the system offers to switch to concrete action-focused guidance.

### Framework Shifts

A reasoning framework shift occurs when:
- A new organizing distinction emerges
- It restructures how the problem is understood
- The system would now reason FROM this frame, not just ABOUT it
- It resolves multiple conflicting constraints simultaneously

Shifts are NOT:
- Better wording
- More detail  
- A softer binary
- A simple restatement

---

## Technical Architecture

### Backend
- **Framework**: FastAPI + Python
- **LLM Integration**: Anthropic Claude API
- **Architecture**: Modular pipeline with specialized components

### Frontend
- **Stack**: Vanilla HTML/CSS/JavaScript
- **Layout**: Two-panel desktop layout (conversation left, live reasoning right)
- **Mobile**: Responsive stacked layout
- **Aesthetic**: Dark theme (#0c0c0e) with warm gold accents (#c8a96e)

### File Structure
```
thought_partner/
├── app.py                 # FastAPI application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── README.md            # This file
├── modules/
│   ├── intake.py        # Input routing and classification
│   ├── frame_extractor.py # Initial frame extraction
│   ├── socratic_loop.py  # Socratic questioning engine
│   ├── shift_detector.py # Framework shift detection
│   ├── memory.py        # Process memory building
│   ├── composer.py      # Output composition
│   └── protection.py    # Protection mode handling
├── prompts/
│   ├── frame_prompt.txt    # Frame extraction prompt
│   ├── socratic_prompt.txt # Socratic questioning prompt
│   ├── shift_prompt.txt    # Shift detection prompt
│   └── compose_prompt.txt  # Output composition prompt
└── ui/
    ├── index.html       # Main UI
    ├── styles.css       # Styling and aesthetics
    └── app.js          # Frontend logic
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Anthropic API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/fatguylilcoat98/thought-partner.git
   cd thought-partner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

4. **Run the application**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open in browser**
   Navigate to `http://localhost:8000`

### Deploy to Render

1. **Connect repository to Render**
   - Create new Web Service
   - Connect to GitHub repository

2. **Configure environment**
   - Add `ANTHROPIC_API_KEY` environment variable
   - Render will use the included `render.yaml` configuration

3. **Deploy**
   - Render will automatically build and deploy from the repository

---

## API Reference

### Main Endpoint

**POST** `/think`

Request body:
```json
{
  "message": "string"
}
```

Response:
```json
{
  "mode": "THOUGHT_PARTNER" | "PROTECTION",
  "shift_detected": boolean,
  "initial_frame": {},
  "final_frame": "string",
  "organizing_distinction": "string", 
  "confidence": 0.0,
  "constraints": [],
  "questions": [],
  "rejected_frames": [],
  "memory": {},
  "output": "string",
  "steps": []
}
```

### Health Check

**GET** `/health`

Returns application status and version.

---

## Design Philosophy

### System Rules (Absolute)

- **NEVER** answer on the first pass
- **ALWAYS** extract a frame before doing anything else
- **ALWAYS** run the Socratic loop (minimum 3 passes unless shift detected earlier)
- **MUST** either detect a shift OR explicitly report "no better frame found"
- **MUST** show live reasoning in right panel for every run
- **MUST** route to Protection when keywords detected
- **DO NOT** collapse into generic chatbot behavior under any condition

### User Experience

The right panel "Live Reasoning" is the core product feature:

1. **Initial Frame Card**: Shows extracted problem framing
2. **Socratic Pass Cards**: Display questions and new constraints
3. **Shift Check Cards**: Show detection attempts and confidence
4. **Memory Card**: Final summary of the reflection process

Each card animates in sequentially, making the thinking process transparent and inspectable.

---

## Contributing

This system is designed around specific philosophical principles:

1. **Reflection before answers**: Never provide solutions without first improving the problem framing
2. **Transparency**: The reasoning process must be fully visible
3. **Protection first**: Route urgent situations to appropriate support immediately
4. **Framework consciousness**: Focus on *how* people think about problems, not just *what* they think

---

## License & Attribution

Created as part of The Good Neighbor Guard mission:  
*Truth · Safety · We Got Your Back*

For questions or support, contact Christopher Hughes in Sacramento, CA.

---

*Built with the belief that better questions lead to better answers.*