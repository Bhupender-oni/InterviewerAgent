import json
from typing import Dict, Any
from openai import AsyncOpenAI
from config import settings
from promtps import FEEDBACK_PROMPT

async def generate_feedback(agent) -> Dict[str, Any]:
    """Generate structured feedback after interview."""
    
    # Setup LLM client
    if settings.llm_provider == "ollama":
        client = AsyncOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama"
        )
        model = settings.ollama_model
    elif settings.llm_provider == "groq":
        client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key
        )
        model = settings.groq_model
    else:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        model = settings.openai_model
    
    # Build transcript
    transcript = "\n".join([
        f"{'Interviewer' if m['role']=='interviewer' else 'Candidate'}: {m['content']}"
        for m in agent.history
    ])
    
    # Build candidate profile summary
    profile = agent.profile
    candidate_profile = f"""
Name: {profile.get('name', 'Candidate')}
Role: {profile.get('job_role', 'N/A')}
Experience: {profile.get('experience', 0)} years
Completed Days: {', '.join(map(str, profile.get('completed_days', [])))}
Attempted (with effort): {profile.get('attempted_days', {})}
Skipped: {', '.join(map(str, profile.get('skipped_days', [])))}
"""
    
    # Generate feedback
    prompt = FEEDBACK_PROMPT.format(
        candidate_profile=candidate_profile,
        transcript=transcript,
    )
    
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500,
    )
    
    raw_response = response.choices[0].message.content.strip()
    
    # Parse JSON feedback
    try:
        # Try to extract JSON if wrapped in markdown
        if "```json" in raw_response:
            raw_response = raw_response.split("```json")[1].split("```")[0]
        elif "```" in raw_response:
            raw_response = raw_response.split("```")[1].split("```")[0]
        
        feedback = json.loads(raw_response)
        
        # Ensure required fields
        feedback.setdefault('overall_score', None)
        feedback.setdefault('strengths', [])
        feedback.setdefault('areas_for_improvement', [])
        feedback.setdefault('recommended_review', [])
        feedback.setdefault('transcript_summary', 'Interview completed.')
        
        return feedback
        
    except json.JSONDecodeError:
        # Fallback if parsing fails
        return {
            'overall_score': None,
            'strengths': [
                'Participated in the interview',
                'Demonstrated knowledge of covered topics',
            ],
            'areas_for_improvement': [
                'Review core concepts',
                'Practice articulating technical concepts',
            ],
            'recommended_review': [],
            'transcript_summary': 'Interview completed. Refer to transcript for details.',
        }
