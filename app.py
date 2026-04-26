"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
import logging

from modules.intake import intake
from modules.frame_extractor import extract_frame
from modules.socratic_loop import run_socratic_pass, SOCRATIC_PASSES
from modules.shift_detector import detect_shift
from modules.memory import build_memory
from modules.composer import compose_output

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thought Partner", version="0.2")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="ui"), name="static")

class ThinkRequest(BaseModel):
    message: str

def thought_partner_pipeline(user_input: str):
    """Main pipeline implementation - pure reflection system"""

    # 1. Intake — classify domain only (always continues to reflection)
    intake_result = intake(user_input)

    # 2. Extract initial frame — no solving
    frame = extract_frame(user_input)

    constraints = []
    questions = []
    rejected_frames = []
    steps = []

    shift_result = {
        "shift_detected": False,
        "new_frame": "",
        "old_frame": "",
        "organizing_distinction": "",
        "explanation": "",
        "confidence": 0.0,
    }

    # Add initial frame step
    steps.append({
        "type": "frame",
        "frame": frame
    })

    # 3. Socratic loop — 3 to 6 passes
    for i in range(SOCRATIC_PASSES):
        socratic = run_socratic_pass(frame, constraints)
        constraints.append(socratic["new_constraint"])
        questions.append(socratic["question"])

        # Record step for UI timeline
        steps.append({
            "type": "socratic_pass",
            "index": i + 1,
            "question": socratic["question"],
            "new_constraint": socratic["new_constraint"],
            "constraints_so_far": list(constraints),
        })

        # 4. Check for shift after every pass
        shift_result = detect_shift(frame, constraints, questions)

        steps.append({
            "type": "shift_check",
            "index": i + 1,
            "shift_detected": shift_result["shift_detected"],
            "organizing_distinction": shift_result["organizing_distinction"],
            "confidence": shift_result["confidence"],
        })

        if shift_result["shift_detected"]:
            break
        else:
            rejected_frames.append(
                frame.get("apparent_decision", "initial frame")
            )

    # 5. Build memory — log rejected frames
    memory_obj = build_memory(
        frame=frame,
        rejected_frames=rejected_frames,
        shift_result=shift_result,
        constraints=constraints,
        questions=questions,
    )

    steps.append({
        "type": "memory_summary",
        "memory": memory_obj,
    })

    # 6. Compose output from new frame or honest no‑shift state
    output_text = compose_output(user_input, memory_obj, shift_result)

    # 7. Return final response
    return {
        "mode": "THOUGHT_PARTNER",
        "shift_detected": shift_result["shift_detected"],
        "initial_frame": frame,
        "final_frame": shift_result["new_frame"] or frame.get("apparent_decision", ""),
        "organizing_distinction": shift_result["organizing_distinction"],
        "confidence": shift_result["confidence"],
        "constraints": constraints,
        "questions": questions,
        "rejected_frames": rejected_frames,
        "memory": memory_obj,
        "output": output_text,
        "steps": steps,
    }

@app.post("/think")
async def think(request: ThinkRequest):
    """Main thinking endpoint"""
    try:
        result = thought_partner_pipeline(request.message)
        return result
    except Exception as e:
        logger.error(f"Error in thought_partner_pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Serve the main UI"""
    return FileResponse("ui/index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.2"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)