"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class RunStatus(str, Enum):
    SHIFT_DETECTED = "SHIFT_DETECTED"
    NO_SHIFT_FOUND = "NO_SHIFT_FOUND"
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"

class FrameExtractionResult(BaseModel):
    stated_problem: str = Field(..., description="User's own description of what is going on")
    apparent_decision: str = Field(..., description="What they seem to think they are deciding between")
    hidden_tensions: List[str] = Field(default_factory=list, description="Pressures or worries present but not cleanly named")
    conflicting_values: List[str] = Field(default_factory=list, description="Values or goals that seem to be in conflict")
    false_binary: str = Field(default="", description="Any either/or they are treating as only options")
    missing_factors: List[str] = Field(default_factory=list, description="Important factors not being discussed but seem relevant")

class SocraticPassResult(BaseModel):
    question: str = Field(..., description="Specific question probing one frame dimension")
    new_constraint: str = Field(..., description="New constraint or angle introduced")
    frame_dimension: str = Field(..., description="Which frame element this probes: hidden_tensions, conflicting_values, false_binary, missing_factors, apparent_decision")

class ShiftDetectionResult(BaseModel):
    shift_detected: bool = Field(..., description="Whether a reasoning framework shift occurred")
    new_frame: str = Field(default="", description="New organizing frame if shift detected")
    old_frame: str = Field(..., description="Original frame being evaluated")
    organizing_distinction: str = Field(default="", description="Key distinction that creates the shift")
    explanation: str = Field(default="", description="Why this constitutes a shift")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in shift detection")

class TechnicalFailure(BaseModel):
    module: str = Field(..., description="Module where failure occurred")
    reason: str = Field(..., description="Reason for technical failure")
    raw_response: Optional[str] = Field(None, description="Raw LLM response if available")

class StepResult(BaseModel):
    type: str = Field(..., description="Type of step: frame, socratic_pass, shift_check, memory_summary, technical_failure")
    index: Optional[int] = Field(None, description="Pass number for numbered steps")
    data: dict = Field(default_factory=dict, description="Step-specific data")

class ThoughtPartnerResponse(BaseModel):
    mode: Literal["THOUGHT_PARTNER"] = "THOUGHT_PARTNER"
    run_status: RunStatus
    shift_detected: bool
    initial_frame: FrameExtractionResult
    final_frame: str
    organizing_distinction: str
    confidence: float
    constraints: List[str]
    questions: List[str]
    rejected_frames: List[str]
    memory: dict
    output: str
    steps: List[StepResult]
    technical_error: Optional[TechnicalFailure] = None