from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from models import (
    InterviewStartRequest, InterviewMessageRequest, InterviewResponse,
    FeedbackData
)
from agent import InterviewAgent, interviews
from data_loader import load_candidate_profile, get_available_candidates
from feedback import generate_feedback

app = FastAPI(
    title="AI Interview Agent API",
    description="Technical interview agent for ABTalks AI Engineering Cohort",
    version="1.0.0"
)

# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "available_candidates": len(get_available_candidates())}

# ============ Spec-Compliant Endpoint ============

@app.post("/api/interview")
async def interview_endpoint(request: dict) -> dict:
    """
    Main interview endpoint supporting unified request/response protocol.
    
    Request formats:
    - Start: {"sessionId": "abc-123", "candidate": {...}}
    - Continue: {"sessionId": "abc-123", "message": "candidate response"}
    
    Response formats:
    - Active: {"reply": "...", "done": false}
    - Complete: {"reply": "...", "done": true, "feedback": {...}}
    """
    
    session_id = request.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=400, detail="sessionId is required")
    
    # Check if this is an existing session
    if session_id in interviews:
        # Continue interview
        message = request.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="message is required for existing session")
        
        agent = interviews[session_id]
        response_text, is_complete = await agent.process_message(message)
        
        result = {
            "reply": response_text,
            "done": is_complete
        }
        
        if is_complete:
            # Generate feedback
            feedback = await generate_feedback(agent)
            result["feedback"] = {
                "summary": feedback.get('transcript_summary', 'Interview completed.'),
                "strengths": feedback.get('strengths', []),
                "gaps": feedback.get('areas_for_improvement', []),
                "next": [
                    f"Day {r['day']}: {r['topic']} - {r['reason']}"
                    for r in feedback.get('recommended_review', [])
                ]
            }
            # Clean up
            del interviews[session_id]
        
        return result
    
    else:
        # New session
        candidate_data = request.get("candidate")
        if not candidate_data:
            raise HTTPException(status_code=400, detail="candidate data is required for new session")
        
        # Extract candidate ID - support multiple formats
        candidate_id = candidate_data.get("id") or candidate_data.get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=400, detail="candidate.id is required")
        
        try:
            # Try to load profile from stored candidates
            profile = load_candidate_profile(candidate_id)
        except ValueError:
            # If not found, create a profile from provided data
            profile = {
                'candidate_id': candidate_id,
                'name': candidate_data.get('name', 'Candidate'),
                'job_role': candidate_data.get('jobRole', 'N/A'),
                'experience': candidate_data.get('yearsExperience', 0),
                'completed_days': [],
                'attempted_days': {},
                'skipped_days': [],
                'learning_signals': [],
            }
        
        # Create interview agent
        agent = InterviewAgent(candidate_id=candidate_id, candidate_profile=profile)
        greeting = await agent.start_interview()
        
        # Store agent
        interviews[session_id] = agent
        
        return {
            "reply": greeting,
            "done": False
        }

# ============ Admin/Debug Endpoints ============

@app.get("/candidates")
async def list_candidates():
    """List all available candidate IDs for testing."""
    try:
        candidates = get_available_candidates()
        return {"candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def list_sessions():
    """List active interview sessions (debug only)."""
    return {
        "active_sessions": list(interviews.keys()),
        "count": len(interviews)
    }

# ============ Error Handlers ============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "reply": "An error occurred during the interview.",
            "done": True,
            "error": str(exc)
        }
    )

# ============ Root ============

@app.get("/")
async def root():
    """API root with documentation."""
    return {
        "name": "AI Interview Agent",
        "version": "1.0.0",
        "description": "Technical interview for ABTalks cohort graduates",
        "endpoints": {
            "POST /api/interview": "Main interview endpoint (start/continue)",
            "GET /health": "Health check",
            "GET /candidates": "List available candidates",
            "GET /sessions": "List active sessions (debug)",
        },
        "example_start": {
            "sessionId": "session-001",
            "candidate": {
                "id": "CAND-001",
                "name": "Sarah Johnson",
                "jobRole": "Senior Data Engineer",
                "yearsExperience": 9
            }
        },
        "example_continue": {
            "sessionId": "session-001",
            "message": "I believe embeddings are numerical representations of text that capture semantic meaning..."
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
