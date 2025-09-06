import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

load_dotenv()

@dataclass
class ModelConfig:
    name: str
    temperature: float

LLAMA_3_3_70B = ModelConfig("llama-3.3-70b-versatile", 0.0)

class Config:
    SEED = 42
    MODEL = LLAMA_3_3_70B
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is required in .env file")
    
    class Path:
        APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
        DATA_DIR = APP_HOME / "db"
        DATABASE_PATH = DATA_DIR / "library.db"

def create_llm(model_config: ModelConfig = Config.MODEL) -> BaseChatModel:
    return ChatGroq(
        model=model_config.name,
        temperature=model_config.temperature,
        api_key=Config.GROQ_API_KEY
    )