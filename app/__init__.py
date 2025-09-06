from server.agent import create_history, ask
from server.models import create_llm
from server.config import Config
from server.tools import get_available_tools
from langchain_core.messages import HumanMessage, AIMessage

class Agent:
    def __init__(self):
        """Initialize the library agent with LLM and tools"""
        self.llm = create_llm(Config.MODEL)
        self.llm = self.llm.bind_tools(get_available_tools())
        self.history = create_history()
    
    def invoke(self, input_dict):
        """Process user input and return agent response"""
        user_input = input_dict.get("input", "")
        
        try:
            # Get response from agent
            response = ask(
                query=user_input,
                history=self.history,
                llm=self.llm
            )
            
            # Add to conversation history
            self.history.append(HumanMessage(content=user_input))
            self.history.append(AIMessage(content=response))
            
            # Return formatted response
            return {
                "messages": [{"role": "assistant", "content": response}],
                "output": response
            }
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            return {
                "messages": [{"role": "assistant", "content": error_msg}],
                "output": error_msg
            }

def build_agent():
    """Factory function to create an agent instance"""
    return Agent()