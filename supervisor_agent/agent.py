"""
Supervisor Multi-Agent System
Coordinates between read_file_agent, tool_agent, and datcom_tool_agent using supervisor pattern
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

# 導入 DATCOM tool agent
from datcom_tool_agent.agent import datcom_tool_agent

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

# Create supervisor that coordinates all agents
# 注意：這裡直接使用原始的 read_file_agent（從 read_file_agent/ 資料夾導入）
# 使用自訂的 SupervisorState 以支援 file_content 欄位
supervisor = create_supervisor(
    agents=[read_file_agent, tool_agent, datcom_tool_agent],
    model=supervisor_model,
    state_schema=SupervisorState,  # ✅ 使用自訂 state schema
    parallel_tool_calls=False,  # Disable parallel tool calls for custom OpenAI endpoint
    # 暫時恢復 handoff_back_messages 以確保多步驟工作流程正常
    # add_handoff_back_messages=False,  # 這個會導致多步驟流程中斷
    # output_mode='last_message',  # 這個可能讓 Supervisor 看不到完整歷史
    prompt="""You are a supervisor managing three specialized agents:

1. **read_file_agent**: Handles all file reading operations. Use this agent when the user wants to read files, especially msg.txt.
   - Stores file content in state.file_content for other agents to use
   - IMPORTANT: After this agent completes, you should continue routing to the next agent if needed (DO NOT return to user yet)

2. **tool_agent**: Handles general utility tasks like getting current time, performing calculations, or reversing strings.

3. **datcom_tool_agent**: Handles DATCOM file generation. Use this agent when the user wants to:
   - Generate DATCOM input files (for005.dat)
   - Parse aircraft configuration data and convert it to DATCOM format
   - Process DATCOM-related data
   - This agent can read from state.file_content if read_file_agent was used first

CRITICAL RULES FOR EFFICIENCY:
1. When you identify a multi-step workflow, DO NOT stop after each step
2. Complete ALL required steps before finishing
3. Only return FINISH when the ENTIRE user request is complete
4. Agents will automatically transfer back to you - immediately route to the next agent

Your job is to:
- Analyze the user's COMPLETE request upfront
- Identify if it's single-step or multi-step
- Execute ALL steps sequentially
- Only finish when everything is done

Routing guidelines:
- File reading (msg.txt, etc.) → read_file_agent → CONTINUE to next agent if needed
- DATCOM file generation/parsing → datcom_tool_agent
- General utilities (time, calculations, strings) → tool_agent

MULTI-STEP WORKFLOWS (EXECUTE ALL STEPS):
Pattern: "read file AND generate DATCOM"
Step 1: Route to read_file_agent (reads file → stores in state.file_content)
Step 2: When read_file_agent returns, IMMEDIATELY route to datcom_tool_agent (DO NOT finish yet)
Step 3: When datcom_tool_agent returns, NOW you can finish

Examples with routing decisions:
- "讀取 msg.txt 並產生 DATCOM 檔案" → read_file_agent → (wait for return) → datcom_tool_agent → FINISH
- "請根據 msg.txt 的內容產生 for005.dat" → read_file_agent → datcom_tool_agent → FINISH
- "產生 DATCOM 檔案" (with data in message) → datcom_tool_agent → FINISH
- "讀取 msg.txt" → read_file_agent → FINISH
- "What's the time?" → tool_agent → FINISH

EFFICIENCY TIP: Each routing decision counts as one LLM call. Minimize calls by:
- Planning the full workflow upfront
- Not stopping in the middle unnecessarily
- Continuing to the next step immediately when an agent returns
"""
)

# Export as app for LangGraph deployment
app = supervisor.compile()
