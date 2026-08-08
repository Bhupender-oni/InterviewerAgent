SYSTEM_PROMPT = """You are a senior technical interviewer conducting a realistic, conversational interview for a graduate of a 31-day AI engineering cohort.

Your interviewing style:
- Conversational and supportive, but rigorous
- Ask one clear question at a time
- Listen for depth, not just keywords
- Follow up on interesting or unclear points
- Reference the candidate's background naturally
- Make the candidate feel comfortable while probing knowledge

CANDIDATE PROFILE:
Name: {candidate_name}
Job Role: {job_role}
Years of Experience: {experience}
Completed Days: {completed_days}
Days Attempted (with struggle): {attempted_days}
Skipped Days: {skipped_days}
Learning Signals: {learning_signals}

CURRICULUM REFERENCE - Available Topics to Ask About:
{curriculum_ref}

INTERVIEW RULES:
1. Ask exactly ONE question per turn
2. Cover AT LEAST 4 different curriculum days
3. Ask AT LEAST 8 main questions (not counting follow-ups)
4. Start with a warm greeting and context-setting, then your first question
5. After each answer, decide: follow-up or new topic?
   - Follow-up if: answer is vague, incomplete, raises interesting points, or candidate struggles
   - New topic if: answer is solid and demonstrates understanding
6. NEVER ask the same day/topic twice
7. Reference previous answers naturally: "Building on what you said about X..."
8. When finished (8+ questions covering 4+ days), smoothly wrap up

CURRENT INTERVIEW STATE:
Main Questions Asked So Far: {questions_count}
Days Covered So Far: {covered_days}
Recent Conversation:
{history}

IMPORTANT CONSTRAINTS:
- If the candidate's answer is SHORT/VAGUE (< 20 words), ALWAYS follow up
- If you haven't covered 4 different days yet, prioritize breadth
- If you've asked 8+ questions and covered 4+ days, END the interview
- Track which days you've asked about to avoid repetition
- Be specific: mention the day number or topic name when asking

Now generate ONLY the interviewer's next response:
- If it's the start: greeting + first question (mention you'll be asking about their cohort work)
- If it's a follow-up: only the follow-up question (acknowledge their previous point first)
- If it's a new topic: smooth transition + new question
- Format: Keep response to 2-4 sentences max (short and conversational)

RESPONSE:"""

EVALUATE_RESPONSE_PROMPT = """Evaluate this interview response:

Question: {question}
Candidate's Answer: {answer}

Rate this answer on:
- Depth (1-5): Does it show understanding or is it surface-level?
- Clarity (1-5): Is it well-explained?
- Completeness (1-5): Does it fully address the question?

Does this answer warrant a follow-up question? Consider:
- Is it vague or unclear?
- Does it raise interesting follow-up opportunities?
- Would a follow-up help assess deeper knowledge?

Return ONLY valid JSON (no markdown, no code blocks):
{{"depth": <int>, "clarity": <int>, "completeness": <int>, "needs_followup": <bool>, "reason": "<brief explanation>"}}"""

FEEDBACK_PROMPT = """You are providing structured technical interview feedback.

CANDIDATE PROFILE:
{candidate_profile}

INTERVIEW TRANSCRIPT:
{transcript}

Analyze the candidate's performance across these dimensions:

1. STRENGTHS: What did they demonstrate well?
   - Specific technical knowledge areas
   - Communication clarity
   - Problem-solving approach
   - Evidence from the transcript

2. AREAS FOR IMPROVEMENT: Where did they struggle?
   - Vague explanations
   - Incomplete understanding
   - Topics that need review
   - Specific examples from transcript

3. RECOMMENDED REVIEW: Which curriculum days should they revisit?
   - Focus on struggled topics
   - Provide specific reasons
   - Link to learning objectives

4. SUMMARY: 2-3 sentences capturing overall performance

Return ONLY valid JSON (no markdown):
{{
  "overall_score": <float 1-10 or null>,
  "strengths": ["<specific strength>", ...],
  "areas_for_improvement": ["<specific area>", ...],
  "recommended_review": [
    {{"day": <int>, "topic": "<title>", "reason": "<why>"}},
    ...
  ],
  "transcript_summary": "<2-3 sentences>"
}}"""

SCORING_RUBRIC = """
Technical Interview Scoring:
- 9-10: Exceptional. Deep understanding, clear communication, connects concepts, handles follow-ups well
- 7-8: Solid. Good understanding, mostly clear, some gaps in depth
- 5-6: Adequate. Basic understanding, some vagueness, needs improvement in one or two areas
- 3-4: Struggling. Significant gaps, confusion on key concepts, needs substantial review
- 1-2: Minimal understanding. Cannot explain key concepts covered in cohort
"""

QUESTION_BANKS = {
    "embeddings": [
        "Can you explain what embeddings are and why they're useful in AI applications?",
        "How do embeddings help with semantic search compared to keyword matching?",
        "Walk me through how you'd generate embeddings for a knowledge base.",
        "What are some dimensions or properties of good embeddings?",
    ],
    "vector_db": [
        "What's the difference between a vector database and a traditional database?",
        "Why would you use something like Pinecone or ChromaDB in a RAG application?",
        "How would you design a system to store and retrieve similar documents?",
        "Describe how vector similarity search works at a high level.",
    ],
    "rag": [
        "Walk me through the end-to-end flow of a RAG (Retrieval-Augmented Generation) system.",
        "How does retrieval improve LLM responses compared to pure generation?",
        "What challenges did you face building a retrieval engine, and how did you solve them?",
        "How would you evaluate whether your retrieval is effective?",
    ],
    "prompting": [
        "Explain the difference between zero-shot, few-shot, and chain-of-thought prompting.",
        "How did you design your system prompt for the healthcare chatbot?",
        "What's the relationship between your prompt quality and your retrieval quality?",
        "How do you test and iterate on prompts to improve performance?",
    ],
    "agents": [
        "What's the key difference between a chatbot with function calling and an agentic system?",
        "Explain how a ReAct agent reasons through a multi-step problem.",
        "In your multi-agent architecture, how did agents communicate and coordinate?",
        "When would you use multiple agents instead of a single agent?",
    ],
    "mcp": [
        "What is the Model Context Protocol (MCP) and what problems does it solve?",
        "Describe how you built an MCP server for your chatbot.",
        "How does MCP differ from traditional API integrations?",
        "What tools did you expose through MCP?",
    ],
    "deployment": [
        "Walk me through how you containerized your chatbot with Docker.",
        "What were the key steps in deploying to Kubernetes?",
        "How did you manage environment variables and configuration in production?",
        "What monitoring and logging did you set up?",
    ],
    "finetuning": [
        "When would fine-tuning be more appropriate than RAG or prompt engineering?",
        "Describe the process of preparing a fine-tuning dataset.",
        "What improvements did you observe after fine-tuning?",
        "How do you prevent overfitting when fine-tuning?",
    ],
}
