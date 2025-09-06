from datetime import datetime
from typing import List
import traceback

from server.config import Config, create_llm
from server.tools import get_available_tools, call_tool
from server.logging import green_border_style, log_panel

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


def load_prompt():
    try:
        with open("prompts/system.txt", "r") as f:
            return f.read().strip()
    except:
        return f"You are Library Desk Agent. Today is {datetime.now().strftime('%Y-%m-%d')}. Help with book orders, inventory, and customer queries."

SYSTEM_PROMPT = load_prompt()

def create_history() -> List[BaseMessage]:
    return [SystemMessage(content=SYSTEM_PROMPT)]

def ask(query: str, history: List[BaseMessage], llm: BaseChatModel, max_iterations: int = 10) -> str:
    log_panel(title="User Request", content=f"Query: {query}", border_style=green_border_style)

    n_iterations = 0
    messages = history.copy()
    messages.append(HumanMessage(content=query))

    while n_iterations < max_iterations:
        response = llm.invoke(messages)
        messages.append(response)

        tool_calls = getattr(response, "tool_calls", [])
        if not tool_calls:
            return response.content

        for tool_call in tool_calls:
            tool_response = call_tool(tool_call)
            messages.append(tool_response)

        n_iterations += 1

    raise RuntimeError("Maximum number of iterations reached. Try a simpler query.")


class Agent:
    def __init__(self):
        self.llm = create_llm(Config.MODEL)
        tools = get_available_tools()
        try:
            self.llm = self.llm.bind_tools(tools)
        except AttributeError:
            print("Warning: LLM does not support bind_tools. Tools will not be available.")

        self.history = create_history()

    def invoke(self, input_dict):
        user_input = input_dict.get("input", "")

        try:
            response = ask(
                query=user_input,
                history=self.history,
                llm=self.llm
            )
            
            self.history.append(HumanMessage(content=user_input))
            self.history.append(AIMessage(content=response))
            
            return {
                "messages": [{"role": "assistant", "content": response}],
                "output": response
            }

        except Exception as e:
            traceback.print_exc()
            error_msg = f"Error processing request: {str(e)}"
            return {
                "messages": [{"role": "assistant", "content": error_msg}],
                "output": error_msg
            }


def build_agent():
    return Agent()