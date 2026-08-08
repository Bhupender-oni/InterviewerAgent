from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ============ Request Models ============

class CandidateData(BaseModel):
    """Candidate information."""
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str = "COMPLETED"

class InterviewStartRequest(BaseModel):
    """Request to start a new interview session."""
    sessionId: str
    candidate: Dict[str, Any] = Field(..., description="Candidate profile data")

class InterviewMessageRequest(BaseModel):
    """Request to send a message during interview."""
    sessionId: str
    message: Optional[str] = None

# ============ Response Models ============

class FeedbackData(BaseModel):
    """Feedback structure."""
    summary: str
    strengths: List[str]
    gaps: List[str]
    next: List[str]

class InterviewResponse(BaseModel):
    """Response from interview endpoint."""
    reply: str = Field(..., description="Interviewer's response")
    done: bool = Field(default=False, description="Whether interview is complete")
    feedback: Optional[FeedbackData] = Field(None, description="Feedback when done=true")

# ============ Internal Models ============

class InterviewStartRequest_OLD(BaseModel):
    """Legacy request format (for compatibility)."""
    candidate_id: str
    action: str = "start"

class InterviewRespondRequest_OLD(BaseModel):
    """Legacy respond format."""
    interview_id: str
    candidate_id: str
    answer: str

class InterviewEndRequest_OLD(BaseModel):
    """Legacy end format."""
    interview_id: str
    candidate_id: str
    action: str = "end"

class InterviewResponse_OLD(BaseModel):
    """Legacy response format."""
    interview_id: str
    interview_active: bool
    message: str
    question_count: Optional[int] = None

class FeedbackResponse_OLD(BaseModel):
    """Legacy feedback format."""
    interview_id: str
    candidate_id: str
    overall_score: Optional[float] = None
    strengths: List[str]
    areas_for_improvement: List[str]
    recommended_review: List[Dict[str, Any]]
    transcript_summary: str
