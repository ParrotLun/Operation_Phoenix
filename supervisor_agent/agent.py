"""
Supervisor Multi-Agent System
Coordinates between read_file_agent, tool_agent, and datcom_tool_agent using supervisor pattern
Note: tool_agent is kept for system stability, though not actively used
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

from supervisor_agent.agents.tool_agent import tool_agent  # Kept for stability

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
    prompt="""You are a supervisor managing two main specialized agents:

NOTE: tool_agent exists but is NOT actively used - ignore it for routing decisions

1. **read_file_agent**: Handles all file reading operations. Use this agent when the user wants to read files, especially msg.txt.
   - Stores file content in state.file_content for other agents to use
   - IMPORTANT: After this agent completes, you should continue routing to the next agent if needed (DO NOT return to user yet)

2. **datcom_tool_agent**: Handles DATCOM file generation. Use this agent when the user wants to:
   - Generate DATCOM input files (for005.dat)
   - Parse aircraft configuration data and convert it to DATCOM format
   - Process DATCOM-related data
   - This agent can read from state.file_content if read_file_agent was used first

CRITICAL RULES FOR MULTI-STEP WORKFLOWS:
1. Analyze the COMPLETE user request FIRST
2. If the request contains keywords like "並"/"and"/"then"/"產生"/"generate" = MULTI-STEP WORKFLOW
3. NEVER finish after just one step in a multi-step workflow
4. When an agent returns to you, check if MORE work is needed
5. Only finish when ALL requested tasks are complete

MULTI-STEP WORKFLOW DETECTION:
- "讀取...並產生..." = 2 steps: read THEN generate
- "讀取...然後..." = 2 steps: read THEN next action
- "read...and generate..." = 2 steps: read THEN generate
- "read...then write..." = 2 steps: read THEN write

EXECUTION STEPS FOR "read file AND generate DATCOM":
Step 1: Route to read_file_agent
        └─> Wait for return
Step 2: read_file_agent returns → IMMEDIATELY route to datcom_tool_agent (DO NOT FINISH!)
        └─> Wait for return
Step 3: datcom_tool_agent returns → NOW finish and respond to user

SINGLE vs MULTI-STEP EXAMPLES:
❌ WRONG: "讀取 msg.txt 並產生 DATCOM 檔案" → read_file_agent → FINISH (missing datcom step!)
✅ CORRECT: "讀取 msg.txt 並產生 DATCOM 檔案" → read_file_agent → datcom_tool_agent → FINISH

❌ WRONG: "Read msg.txt and generate DATCOM" → read_file_agent → FINISH (missing datcom step!)
✅ CORRECT: "Read msg.txt and generate DATCOM" → read_file_agent → datcom_tool_agent → FINISH

✅ CORRECT: "讀取 msg.txt" → read_file_agent → FINISH (single step, ok to finish)
✅ CORRECT: "產生 DATCOM 檔案" → datcom_tool_agent → FINISH (single step, ok to finish)

YOUR DECISION PROCESS:
1. Read user request
2. Count how many actions requested (read? generate? both?)
3. If 2 actions → Execute BOTH before finishing
4. If 1 action → Execute it and finish

REMEMBER: "並"/"and" means DO BOTH STEPS!
"""
)

# Export as app for LangGraph deployment
app = supervisor.compile()
