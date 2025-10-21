"""
Supervisor Multi-Agent System
Coordinates between read_file_agent and tool_agent using supervisor pattern
"""
import os
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from dotenv import load_dotenv

# 導入自訂的 SupervisorState
from supervisor_agent.utils.state import SupervisorState

# 方式 1: 從 subgraphs/ 資料夾導入（wrapper）
# from supervisor_agent.subgraphs.read_file_subgraph import read_file_subgraph

# 方式 2: 直接從 read_file_agent/ 資料夾導入原始 graph（推薦）
from read_file_agent.agent import graph as read_file_agent

from supervisor_agent.agents.tool_agent import tool_agent

# Load environment
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "read_file_agent", ".env")
load_dotenv(env_path)

# Custom ChatOpenAI that doesn't send parallel_tool_calls parameter
class CustomChatOpenAI(ChatOpenAI):
    """Custom ChatOpenAI that doesn't send parallel_tool_calls parameter"""

    def bind_tools(self, tools, **kwargs):
        # Override to not set parallel_tool_calls
        kwargs.pop("parallel_tool_calls", None)
        return super().bind_tools(tools, **kwargs)


# Initialize supervisor model
supervisor_model = CustomChatOpenAI(
    model=os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b"),
    temperature=0,
    base_url=os.getenv("OPENAI_API_BASE_URL", "http://172.16.120.65:8089/v1"),
    api_key=os.getenv("OPENAI_API_KEY")  # type: ignore
)

# Create supervisor that coordinates both agents
# 注意：這裡直接使用原始的 read_file_agent（從 read_file_agent/ 資料夾導入）
# 使用自訂的 SupervisorState 以支援 file_content 欄位
supervisor = create_supervisor(
    agents=[read_file_agent, tool_agent],
    model=supervisor_model,
    state_schema=SupervisorState,  # ✅ 使用自訂 state schema
    parallel_tool_calls=False,  # Disable parallel tool calls for custom OpenAI endpoint
    prompt="""You are a supervisor managing two specialized agents:

1. **read_file_agent**: Handles all file reading operations. Use this agent when the user wants to read files, especially msg.txt.

2. **tool_agent**: Handles general utility tasks like getting current time, performing calculations, or reversing strings.

Your job is to:
- Analyze the user's request
- Route the task to the appropriate agent
- Return the agent's response to the user

When unsure which agent to use, prefer read_file_agent for file operations and tool_agent for everything else.
"""
)

# Export as app for LangGraph deployment
app = supervisor.compile()
