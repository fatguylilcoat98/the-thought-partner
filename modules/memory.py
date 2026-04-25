"""
Thought Partner — The Good Neighbor Guard
Built by Christopher Hughes · Sacramento, CA
Created with the help of AI collaborators (Claude · GPT · Gemini · Groq · Perplexity)
Truth · Safety · We Got Your Back
"""

def build_memory(frame: dict, rejected_frames: list, shift_result: dict,
                constraints: list, questions: list) -> dict:
    """
    Build memory object that makes the process inspectable
    """

    # Process rejected frames
    rejected_frame_objects = []
    for frame_text in rejected_frames:
        rejected_frame_objects.append({
            "frame": frame_text,
            "reason": "did not resolve all constraints"
        })

    # Build comprehensive memory object
    memory = {
        "initial_frame": frame,
        "constraints_applied": constraints,
        "questions_asked": questions,
        "rejected_frames": rejected_frame_objects,
        "shift_detected": shift_result["shift_detected"],
        "final_frame": shift_result["new_frame"] or frame.get("apparent_decision", ""),
        "organizing_distinction": shift_result["organizing_distinction"],
        "confidence": shift_result["confidence"],
        "shift_explanation": shift_result["explanation"],
        "process_summary": {
            "total_socratic_passes": len(questions),
            "total_constraints": len(constraints),
            "rejected_frame_count": len(rejected_frames),
            "shift_confidence": shift_result["confidence"]
        }
    }

    return memory

def get_memory_summary(memory: dict) -> str:
    """
    Generate a human-readable summary of the memory object
    """
    summary_parts = []

    if memory["shift_detected"]:
        summary_parts.append(f"✓ Framework shift detected with {memory['confidence']:.1%} confidence")
        summary_parts.append(f"New organizing distinction: {memory['organizing_distinction']}")
        summary_parts.append(f"Final frame: {memory['final_frame']}")
    else:
        summary_parts.append("✗ No framework shift detected")
        summary_parts.append(f"Explored {memory['process_summary']['total_socratic_passes']} questions")
        summary_parts.append(f"Applied {memory['process_summary']['total_constraints']} constraints")

    if memory["rejected_frames"]:
        summary_parts.append(f"Rejected {len(memory['rejected_frames'])} alternative frames")

    return "\n".join(summary_parts)