# AI Interview Agent

A production-ready technical interview agent for evaluating ABTalks AI Engineering Cohort graduates.

## Features

✅ **Spec-Compliant API** - Unified `/api/interview` endpoint matching technical requirements
✅ **Adaptive Interview Flow** - Intelligent follow-ups and question routing based on responses
✅ **Multi-Provider LLM Support** - Ollama (local), Groq (free cloud), OpenAI
✅ **Structured Feedback** - Actionable insights on strengths, gaps, and recommendations
✅ **Production-Ready** - Docker, error handling, health checks, comprehensive logging
✅ **Fully Asynchronous** - High-concurrency FastAPI backend
✅ **Candidate Profile Integration** - Personalized questions based on learning journey

## Quick Start

### Option 1: Local with Ollama (Recommended for Development)

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model
ollama pull llama2:7b

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Run the server
python -m uvicorn main:app --reload

# 5. Test (in another terminal)
python test_agent.py

# 6. Visit API docs
# http://localhost:8000/docs
```

### Option 2: Docker Compose (Recommended for Production)

```bash
# Start with Ollama and auto-download model
docker compose up --pull always -d

# Wait for Ollama to download the model (~10 min for first run)
docker logs interview-agent -f

# Once ready, test
curl http://localhost:8000/health
```

### Option 3: Cloud LLM (No Local Setup)

```bash
# Option A: Using Groq (free, fast)
export GROQ_API_KEY="your_key_from_https://console.groq.com"
export LLM_PROVIDER=groq

# Option B: Using OpenAI
export OPENAI_API_KEY="your_key"
export LLM_PROVIDER=openai

# Then run
python -m uvicorn main:app
```

## API Reference

### Base URL
```
http://localhost:8000
```

### Unified Endpoint: `POST /api/interview`

#### Start a New Interview
```bash
curl -X POST http://localhost:8000/api/interview \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-001",
    "candidate": {
      "id": "CAND-001",
      "name": "Sarah Johnson",
      "jobRole": "Senior Data Engineer",
      "yearsExperience": 9,
      "education": "MS Computer Science",
      "status": "COMPLETED"
    }
  }'
```

**Response:**
```json
{
  "reply": "Welcome to your technical interview...",
  "done": false
}
```

#### Continue Interview
```bash
curl -X POST http://localhost:8000/api/interview \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-001",
    "message": "Embeddings are numerical representations of text that capture semantic meaning..."
  }'
```

**Response (during interview):**
```json
{
  "reply": "Great! Tell me more about how you'd use embeddings in a RAG system...",
  "done": false
}
```

**Response (interview complete):**
```json
{
  "reply": "Thank you for the interview! Here's your feedback...",
  "done": true,
  "feedback": {
    "summary": "Strong understanding of RAG concepts with minor gaps in deployment...",
    "strengths": [
      "Clear understanding of embeddings and vector search",
      "Well-structured approach to RAG architecture",
      "Good awareness of production considerations"
    ],
    "gaps": [
      "Fine-tuning concepts need clarification",
      "Deployment experience appears limited"
    ],
    "next": [
      "Day 14: Fine-Tuning: Concepts & When to Use It - Understand when fine-tuning vs. prompting",
      "Day 28: Docker & Kubernetes Deployment - Review container orchestration"
    ]
  }
}
```

### Available Candidates
```bash
curl http://localhost:8000/candidates
```

Returns:
```json
{
  "candidates": ["CAND-001", "CAND-002", "CAND-003", ...]
}
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Configuration

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Key variables:

```env
# LLM Provider
LLM_PROVIDER=ollama  # or groq, openai

# If using Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama2:7b

# If using Groq
GROQ_API_KEY=your_key
GROQ_MODEL=mixtral-8x7b-32768

# If using OpenAI
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini

# LLM parameters
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
```

## Testing

Run comprehensive test suite:

```bash
python test_agent.py
```

Tests:
- ✓ Data loading (curriculum, candidates)
- ✓ Interview agent initialization and flow
- ✓ Feedback generation
- ✓ API contract validation

## Architecture

```
┌─────────────────────┐
│   FastAPI Server    │
├─────────────────────┤
│  /api/interview     │
│  /health            │
│  /candidates        │
└──────────┬──────────┘
           │
      ┌────▼─────┐
      │InterviewAgent│
      ├────────────┤
      │ • Session  │
      │ • History  │
      │ • Tracking │
      └────┬───────┘
           │
      ┌────▼────────┐
      │ LLM Client  │
      ├─────────────┤
      │ • Ollama    │
      │ • Groq      │
      │ • OpenAI    │
      └────────────┘
```

## Data Flow

1. **Interview Start** → Agent loads candidate profile and curriculum
2. **Greeting** → LLM generates contextual greeting and first question
3. **Candidate Response** → System evaluates answer for depth and completeness
4. **Decision** → Follow-up or move to new topic based on analysis
5. **Feedback** → After 8+ questions over 4+ days, generate structured feedback
6. **Cleanup** → Session removed from memory after completion

## Performance Considerations

- **Memory**: In-memory session storage (scale with Redis for multi-instance)
- **Latency**: Depends on LLM provider (Groq ~3-5s, OpenAI ~2-3s, Ollama ~5-10s)
- **Concurrency**: Async FastAPI handles hundreds of concurrent sessions
- **Cost**: 
  - Ollama: Free (local compute required)
  - Groq: Free tier (generous limits)
  - OpenAI: ~$0.01-0.05 per interview

## Interview Quality

The agent is designed to:

✓ Ask real-world technical questions (not trivia)
✓ Adapt based on candidate background and signals
✓ Follow up on interesting or unclear points
✓ Maintain natural conversational flow
✓ Cover diverse topics (min 4 curriculum days)
✓ Provide actionable feedback with specific recommendations

## Troubleshooting

**"LLM connection failed"**
- Ensure your provider is running/configured
- For Ollama: `ollama serve` in separate terminal
- For Groq/OpenAI: Verify API keys in `.env`

**"Candidate not found"**
- Use `/candidates` endpoint to list available IDs
- Or provide full candidate data in start request

**"Interview not responding"**
- Check logs: `docker logs interview-agent`
- Verify LLM provider health
- For Ollama, ensure model is pulled: `ollama pull llama2:7b`

**Long response times**
- Ollama: Download larger/faster models or use cloud provider
- Try Groq (faster) or OpenAI (more reliable)

## Production Deployment

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: interview-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: interview-agent
  template:
    metadata:
      labels:
        app: interview-agent
    spec:
      containers:
      - name: interview-agent
        image: interview-agent:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: LLM_PROVIDER
          value: "groq"
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: groq-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

### Docker Build

```bash
docker build -t interview-agent:1.0.0 .
docker run -p 8000:8000 \
  -e LLM_PROVIDER=groq \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  interview-agent:1.0.0
```

## Project Structure

```
interview_agent/
├── main.py                  # FastAPI app & endpoints
├── agent.py                 # Interview logic
├── feedback.py              # Feedback generation
├── prompts.py               # LLM prompts
├── models.py                # Pydantic models
├── data_loader.py           # Curriculum & candidate loading
├── config.py                # Configuration
├── test_agent.py            # Comprehensive tests
├── requirements.txt         # Dependencies
├── Dockerfile               # Container definition
├── docker-compose.yml       # Local setup
├── .dockerignore             # Docker build filter
├── .env.example              # Config template
└── sample_data/
    ├── curriculum.json      # 31-day curriculum
    ├── candidates.json      # Candidate profiles
    └── technical-spec.md    # API specification
```

## Next Steps

1. **Testing**
   - Run `python test_agent.py` locally
   - Test the `/docs` Swagger UI
   - Try with different candidates

2. **Customization**
   - Modify prompts in `prompts.py` for different interview styles
   - Add more candidate data to `candidates.json`
   - Adjust LLM parameters in `config.py`

3. **Scaling**
   - Switch to Redis for distributed session storage
   - Deploy with multiple replicas
   - Set up monitoring (prometheus, grafana)

4. **Integration**
   - Build a frontend (React/Vue)
   - Integrate with your recruitment system
   - Add voice interaction (WebRTC)

## License

Proprietary - ABTalks AI Engineering Cohort

## Support

For issues or questions:
- Check the troubleshooting section
- Review logs: `docker logs interview-agent`
- Test with: `python test_agent.py`
