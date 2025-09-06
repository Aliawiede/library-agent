from langchain_groq import ChatGroq
from server.config import Config

def create_llm(model_config=None):
    """
    Create a Groq-powered LLM using the given model configuration.
    """
    if model_config is None:
        model_config = Config.MODEL

    try:
        llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,      # مفتاح API من Config
            model_name=model_config.name,      # الاسم الصحيح للنموذج
            temperature=model_config.temperature,
            verbose=False
        )
        return llm
    except Exception as e:
        raise Exception(
            f"Failed to initialize Groq LLM: {str(e)}\n"
            "Please check:\n"
            "1. GROQ_API_KEY is set correctly\n"
            "2. You have internet connection\n"
            "3. Your Groq API key is valid\n"
            "Get API key from: https://console.groq.com/"
        )
