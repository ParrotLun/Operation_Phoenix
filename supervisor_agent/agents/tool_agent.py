"""
Tool Agent - Handles general tool operations
Uses create_react_agent with basic utility tools
"""
import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from datetime import datetime

# Load environment from read_file_agent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "read_file_agent", ".env")
load_dotenv(env_path)


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def calculate(expression: str) -> str:
    """
    Safely evaluate a mathematical expression.
    Example: "2 + 2" returns "4"
    """
    try:
        # Safe evaluation - only allow numbers and basic operators
        allowed_chars = set("0123456789+-*/()%. ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and +, -, *, /, (), %, . are allowed."

        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


@tool
def reverse_string(text: str) -> str:
    """Reverse a given string."""
    return f"Reversed: {text[::-1]}"


# Initialize model
class CustomChatOpenAI(ChatOpenAI):
    """Custom ChatOpenAI that doesn't send parallel_tool_calls parameter"""

    def bind_tools(self, tools, **kwargs):
        # Override to not set parallel_tool_calls
        kwargs.pop("parallel_tool_calls", None)
        return super().bind_tools(tools, **kwargs)


model = CustomChatOpenAI(
    model=os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b"),
    temperature=0,
    base_url=os.getenv("OPENAI_API_BASE_URL", "http://172.16.120.65:8087/v1"),
    api_key=os.getenv("OPENAI_API_KEY")  # type: ignore
)

# Create tool_agent using prebuilt component
tool_agent = create_react_agent(
    model=model,
    tools=[get_current_time, calculate, reverse_string],
    prompt="You are a general utility assistant. You can get the current time, perform calculations, and reverse strings. Use these tools to help users with their requests.",
    name="tool_agent"
)
