"""
Read File Agent - Handles file reading operations
Uses create_react_agent for simple tool-calling workflow
"""
import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from functools import wraps

# Load environment from read_file_agent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "read_file_agent", ".env")
load_dotenv(env_path)


@tool
def read_msg_file() -> str:
    """Read the content from read_file_agent/data/msg.txt file."""
    # Navigate to read_file_agent/data/msg.txt
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(base_dir, "read_file_agent", "data", "msg.txt")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"\n📂 Read file successfully: {len(content)} characters")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return f"File content:\n{content}"
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


# Initialize model
# Note: Custom OpenAI endpoint may not support all OpenAI parameters
class CustomChatOpenAI(ChatOpenAI):
    """Custom ChatOpenAI that doesn't send parallel_tool_calls parameter"""

    def bind_tools(self, tools, **kwargs):
        # Override to not set parallel_tool_calls
        kwargs.pop("parallel_tool_calls", None)
        return super().bind_tools(tools, **kwargs)


model = CustomChatOpenAI(
    model=os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b"),
    temperature=0,
    base_url=os.getenv("OPENAI_API_BASE_URL", "http://172.16.120.65:8089/v1"),
    api_key=os.getenv("OPENAI_API_KEY")  # type: ignore
)

# Create read_file_agent using prebuilt component
read_file_agent = create_react_agent(
    model=model,
    tools=[read_msg_file],
    prompt="You are a file reading specialist. Your job is to read files when requested. Use the read_msg_file tool to read the msg.txt file.",
    name="read_file_agent"
)
