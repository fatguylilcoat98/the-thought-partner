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
from typing import Union

from modules.intake import intake
from modules.frame_extractor import extract_frame
from modules.socratic_loop import run_socratic_pass, SOCRATIC_PASSES
from modules.shift_detector import detect_shift
from modules.memory import build_memory
from modules.composer import compose_output
from schemas import (
    ThoughtPartnerResponse, FrameExtractionResult, SocraticPassResult,
    ShiftDetectionResult, TechnicalFailure, RunStatus, StepResult
)

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

def thought_partner_pipeline(user_input: str) -> ThoughtPartnerResponse:
    """Main pipeline with comprehensive error handling and validation"""

    # 1. Intake — classify domain only (always continues to reflection)
    intake_result = intake(user_input)

    # 2. Extract initial frame with validation
    frame_result = extract_frame(user_input)
    if isinstance(frame_result, TechnicalFailure):
        logger.error(f"Frame extraction failed: {frame_result.reason}")
        return ThoughtPartnerResponse(
            run_status=RunStatus.TECHNICAL_FAILURE,
            shift_detected=False,
            initial_frame=FrameExtractionResult(
                stated_problem=user_input[:200] + "..." if len(user_input) > 200 else user_input,
                apparent_decision="",
                hidden_tensions=[],
                conflicting_values=[],
                false_binary="",
                missing_factors=[]
            ),
            final_frame="",
            organizing_distinction="",
            confidence=0.0,
            constraints=[],
            questions=[],
            rejected_frames=[],
            memory={},
            output="The reflection process hit a technical issue before a reliable reframe could be produced.",
            steps=[StepResult(
                type="technical_failure",
                data={"module": frame_result.module, "reason": frame_result.reason}
            )],
            technical_error=frame_result
        )

    frame = frame_result
    constraints = []
    questions = []
    rejected_frames = []
    steps = []

    # Add initial frame step
    steps.append(StepResult(
        type="frame",
        data={"frame": frame.dict()}
    ))

    # 3. Socratic loop with validation
    shift_result: Union[ShiftDetectionResult, TechnicalFailure, None] = None

    for i in range(SOCRATIC_PASSES):
        # Run Socratic pass
        socratic_result = run_socratic_pass(frame, constraints, i + 1)

        if isinstance(socratic_result, TechnicalFailure):
            logger.error(f"Socratic pass {i + 1} failed: {socratic_result.reason}")
            return ThoughtPartnerResponse(
                run_status=RunStatus.TECHNICAL_FAILURE,
                shift_detected=False,
                initial_frame=frame,
                final_frame="",
                organizing_distinction="",
                confidence=0.0,
                constraints=constraints,
                questions=questions,
                rejected_frames=rejected_frames,
                memory={},
                output="The reflection process hit a technical issue during Socratic questioning.",
                steps=steps + [StepResult(
                    type="technical_failure",
                    data={"module": socratic_result.module, "reason": socratic_result.reason}
                )],
                technical_error=socratic_result
            )

        # Successful Socratic pass
        constraints.append(socratic_result.new_constraint)
        questions.append(socratic_result.question)

        # Record step
        steps.append(StepResult(
            type="socratic_pass",
            index=i + 1,
            data={
                "question": socratic_result.question,
                "new_constraint": socratic_result.new_constraint,
                "frame_dimension": socratic_result.frame_dimension,
                "constraints_so_far": list(constraints)
            }
        ))

        # 4. Check for shift after every pass
        shift_result = detect_shift(frame, constraints, questions)

        if isinstance(shift_result, TechnicalFailure):
            logger.error(f"Shift detection failed on pass {i + 1}: {shift_result.reason}")
            return ThoughtPartnerResponse(
                run_status=RunStatus.TECHNICAL_FAILURE,
                shift_detected=False,
                initial_frame=frame,
                final_frame="",
                organizing_distinction="",
                confidence=0.0,
                constraints=constraints,
                questions=questions,
                rejected_frames=rejected_frames,
                memory={},
                output="The reflection process hit a technical issue during shift detection.",
                steps=steps + [StepResult(
                    type="technical_failure",
                    data={"module": shift_result.module, "reason": shift_result.reason}
                )],
                technical_error=shift_result
            )

        # Record shift check step
        steps.append(StepResult(
            type="shift_check",
            index=i + 1,
            data={
                "shift_detected": shift_result.shift_detected,
                "organizing_distinction": shift_result.organizing_distinction,
                "confidence": shift_result.confidence
            }
        ))

        # Break if shift detected
        if shift_result.shift_detected:
            break
        else:
            rejected_frames.append(
                frame.apparent_decision or "initial frame"
            )

    # 5. Build memory
    memory_obj = build_memory(
        frame=frame,
        rejected_frames=rejected_frames,
        shift_result=shift_result,
        constraints=constraints,
        questions=questions,
    )

    steps.append(StepResult(
        type="memory_summary",
        data={"memory": memory_obj}
    ))

    # 6. Determine run status
    if shift_result.shift_detected:
        run_status = RunStatus.SHIFT_DETECTED
    else:
        run_status = RunStatus.NO_SHIFT_FOUND

    # 7. Compose output
    output_text = compose_output(user_input, memory_obj, shift_result, run_status)

    # 8. Return complete response
    return ThoughtPartnerResponse(
        run_status=run_status,
        shift_detected=shift_result.shift_detected,
        initial_frame=frame,
        final_frame=shift_result.new_frame or frame.apparent_decision,
        organizing_distinction=shift_result.organizing_distinction,
        confidence=shift_result.confidence,
        constraints=constraints,
        questions=questions,
        rejected_frames=rejected_frames,
        memory=memory_obj,
        output=output_text,
        steps=steps,
        technical_error=None
    )

@app.post("/think")
async def think(request: ThinkRequest) -> ThoughtPartnerResponse:
    """Main thinking endpoint with comprehensive error handling"""
    try:
        result = thought_partner_pipeline(request.message)
        return result
    except Exception as e:
        logger.error(f"Unexpected error in thought_partner_pipeline: {str(e)}")
        return ThoughtPartnerResponse(
            run_status=RunStatus.TECHNICAL_FAILURE,
            shift_detected=False,
            initial_frame=FrameExtractionResult(
                stated_problem=request.message[:200] + "..." if len(request.message) > 200 else request.message,
                apparent_decision="",
                hidden_tensions=[],
                conflicting_values=[],
                false_binary="",
                missing_factors=[]
            ),
            final_frame="",
            organizing_distinction="",
            confidence=0.0,
            constraints=[],
            questions=[],
            rejected_frames=[],
            memory={},
            output="The reflection process encountered an unexpected error.",
            steps=[],
            technical_error=TechnicalFailure(
                module="pipeline",
                reason=str(e)
            )
        )

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