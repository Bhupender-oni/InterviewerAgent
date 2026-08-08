import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuration for the Interview Agent."""
    
    # --- LLM Provider ---
    # Options: "ollama", "groq", "openai"
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    
    # --- Ollama Settings (local LLM) ---
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama2:7b")
    
    # --- Groq Settings (free cloud LLM) ---
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    # --- OpenAI Settings ---
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # --- LLM Parameters ---
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
    conversation_memory_turns: int = int(os.getenv("CONVERSATION_MEMORY", "6"))
    
    # --- Data Paths ---
    curriculum_path: str = os.getenv("CURRICULUM_PATH", "sample_data/curriculum.json")
    candidate_profiles_path: str = os.getenv("CANDIDATE_PROFILES_PATH", "sample_data/candidates.json")
    
    # --- Server Settings ---
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Print configuration on startup (non-sensitive)
if __name__ == "__main__":
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"Model: {settings.ollama_model if settings.llm_provider == 'ollama' else (settings.groq_model if settings.llm_provider == 'groq' else settings.openai_model)}")
    print(f"Curriculum: {settings.curriculum_path}")
    print(f"Candidates: {settings.candidate_profiles_path}")
