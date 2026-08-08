import uuid
import json
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
from config import settings
from promtps import SYSTEM_PROMPT, EVALUATE_RESPONSE_PROMPT
from data_loader import load_curriculum

# In-memory interview session storage
interviews: Dict[str, 'InterviewAgent'] = {}

class InterviewAgent:
    """AI-powered technical interview agent for ABTalks cohort."""
    
    def __init__(self, candidate_id: str, candidate_profile: Dict[str, Any]):
        self.session_id = str(uuid.uuid4())
        self.candidate_id = candidate_id
        self.profile = candidate_profile
        self.curriculum = load_curriculum()
        
        # Interview state
        self.history: List[Dict[str, str]] = []
        self.main_questions: List[str] = []
        self.followup_count = 0
        self.covered_days: set = set()
        self.asked_days: Dict[int, List[str]] = {}  # Track what aspects of each day
        self.is_active = True
        
        # LLM setup
        self._setup_llm_client()
        
    def _setup_llm_client(self):
        """Initialize LLM client based on provider."""
        if settings.llm_provider == "ollama":
            self.client = AsyncOpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama"
            )
            self.model = settings.ollama_model
        elif settings.llm_provider == "groq":
            self.client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.groq_api_key
            )
            self.model = settings.groq_model
        else:  # OpenAI
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model
    
    async def start_interview(self) -> str:
        """Start the interview with greeting and first question."""
        prompt = self._build_system_prompt()
        response = await self._call_llm(prompt, system_override=True)
        self.history.append({"role": "interviewer", "content": response})
        return response
    
    async def process_message(self, user_message: str) -> tuple[str, bool]:
        """
        Process a user message and return (response, is_complete).
        
        Returns:
            tuple: (response text, whether interview is complete)
        """
        # Record candidate's response
        self.history.append({"role": "candidate", "content": user_message})
        
        # Check if we should end the interview
        if len(self.main_questions) >= 8 and len(self.covered_days) >= 4:
            closing = await self._generate_closing()
            self.history.append({"role": "interviewer", "content": closing})
            self.is_active = False
            return closing, True
        
        # Decide: follow-up or new question?
        needs_followup = await self._should_followup(user_message)
        
        if needs_followup and self.followup_count < 2:
            # Ask follow-up on current topic
            followup = await self._generate_followup()
            self.history.append({"role": "interviewer", "content": followup})
            self.followup_count += 1
            return followup, False
        else:
            # Move to next main question
            self.followup_count = 0
            next_question = await self._generate_next_main_question()
            self.history.append({"role": "interviewer", "content": next_question})
            
            # Check again after question
            if len(self.main_questions) >= 8 and len(self.covered_days) >= 4:
                self.is_active = False
                return next_question + "\n\nThank you for the interview!", True
            
            return next_question, False
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with context."""
        curriculum_ref = "\n".join([
            f"Day {d['day']}: {d.get('title', 'N/A')} (type: {d.get('type', 'N/A')})"
            for d in self.curriculum[:15]  # Limit output
        ])
        
        history_text = "\n".join([
            f"{'Interviewer' if m['role']=='interviewer' else 'Candidate'}: {m['content'][:200]}..."
            for m in self.history[-6:]
        ]) if self.history else "(interview just started)"
        
        return SYSTEM_PROMPT.format(
            candidate_name=self.profile.get('name', 'Candidate'),
            job_role=self.profile.get('job_role', 'N/A'),
            experience=self.profile.get('experience', 0),
            completed_days=', '.join(map(str, self.profile.get('completed_days', []))),
            attempted_days=str(self.profile.get('attempted_days', {})),
            skipped_days=', '.join(map(str, self.profile.get('skipped_days', []))),
            learning_signals='\n'.join(self.profile.get('learning_signals', [])),
            curriculum_ref=curriculum_ref,
            questions_count=len(self.main_questions),
            covered_days=', '.join(map(str, sorted(self.covered_days))) or "none yet",
            history=history_text,
        )
    
    async def _call_llm(self, prompt: str, system_override: bool = False) -> str:
        """Call LLM with message."""
        messages = []
        
        if system_override:
            messages.append({
                "role": "system",
                "content": "You are an expert technical interviewer. Keep responses concise and conversational."
            })
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        
        return response.choices[0].message.content.strip()
    
    async def _should_followup(self, user_message: str) -> bool:
        """Decide if answer warrants a follow-up question."""
        # Always follow up on very short answers
        word_count = len(user_message.split())
        if word_count < 20:
            return True
        
        # Get last question
        last_question = ""
        for msg in reversed(self.history[:-1]):  # Exclude the just-added user message
            if msg["role"] == "interviewer":
                last_question = msg["content"]
                break
        
        if not last_question:
            return False
        
        prompt = EVALUATE_RESPONSE_PROMPT.format(
            question=last_question,
            answer=user_message,
        )
        
        try:
            result = await self._call_llm(prompt)
            data = json.loads(result)
            return data.get("needs_followup", False)
        except:
            # Default: follow up if unclear
            return word_count < 40
    
    async def _generate_followup(self) -> str:
        """Generate a follow-up question on the current topic."""
        prompt = self._build_system_prompt()
        instruction = "\n\nThe candidate just answered. Ask a SPECIFIC follow-up question that dives deeper into what they said. Be conversational and reference what they mentioned."
        return await self._call_llm(prompt + instruction)
    
    async def _generate_next_main_question(self) -> str:
        """Generate the next main question on a different day/topic."""
        prompt = self._build_system_prompt()
        instruction = "\n\nTransition to a NEW main question on a different curriculum day. Ask about a topic they completed or attempted. Reference their background if relevant."
        
        response = await self._call_llm(prompt + instruction)
        
        # Track this as a main question
        self.main_questions.append(response)
        self._extract_and_track_day(response)
        
        return response
    
    def _extract_and_track_day(self, question_text: str) -> None:
        """Extract curriculum day from question and track it."""
        for day in self.curriculum:
            day_num = day.get('day')
            title = day.get('title', '').lower()
            
            # Check if day number or title mentioned in question
            if str(day_num) in question_text or title in question_text.lower():
                self.covered_days.add(day_num)
                if day_num not in self.asked_days:
                    self.asked_days[day_num] = []
                self.asked_days[day_num].append(question_text[:100])
                return
    
    async def _generate_closing(self) -> str:
        """Generate interview closing statement."""
        prompt = self._build_system_prompt()
        instruction = "\n\nWrap up the interview. Thank the candidate warmly. Mention they did well and that feedback will follow. Keep it to 2-3 sentences."
        return await self._call_llm(prompt + instruction)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get interview summary for feedback generation."""
        return {
            'session_id': self.session_id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.profile.get('name', 'Candidate'),
            'main_questions_asked': len(self.main_questions),
            'days_covered': sorted(list(self.covered_days)),
            'followup_count': self.followup_count,
            'total_turns': len(self.history),
        }
