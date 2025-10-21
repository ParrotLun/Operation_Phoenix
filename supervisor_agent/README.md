# Supervisor Multi-Agent System

A LangGraph multi-agent system using supervisor pattern to coordinate between specialized agents.

## Architecture

This system uses `langgraph-supervisor` to coordinate between two specialized agents:

1. **read_file_agent**: Handles file reading operations (specifically `read_file_agent/data/msg.txt`)
2. **tool_agent**: Handles general utility tasks (time, calculations, string operations)

```
User Input
    ↓
Supervisor (LLM-based routing)
    ↓
┌───────────────┬───────────────┐
│ read_file_agent│  tool_agent  │
└───────────────┴───────────────┘
    ↓               ↓
Response to User
```

## Key Design Principles (Following AGENT.md & GEMINI.md)

✅ **Deployment-First**: Graph exported as `app`, no checkpointer unless requested
✅ **Prebuilt Components**: Uses `create_react_agent` and `create_supervisor`
✅ **Simple State**: Uses MessagesState as base
✅ **Model Priority**: Uses custom OpenAI endpoint (configurable via .env)
✅ **No Complexity**: Each agent has single responsibility

## File Structure

```
supervisor_agent/
├── agent.py                 # Main supervisor (exports: app)
├── langgraph.json          # LangGraph configuration
├── requirements.txt        # Dependencies
├── test_supervisor.py      # Test script
├── agents/
│   ├── read_file_agent.py  # File reading specialist
│   └── tool_agent.py       # General utility agent
└── utils/
    └── state.py            # Shared state definition
```

## Installation

```bash
cd supervisor_agent
pip install -r requirements.txt
```

## Environment Configuration

Create or use existing `.env` file (currently using `../read_file_agent/.env`):

```
OPENAI_API_BASE_URL=http://172.16.120.65:8089/v1
OPENAI_API_KEY=your-api-key
DEFAULT_LLM_MODEL=openai/gpt-oss-20b
```

## Usage

### Run Tests

```bash
python3 -m supervisor_agent.test_supervisor
```

### Use Programmatically

```python
from supervisor_agent.agent import app

# Read file example
result = app.invoke({
    "messages": [{"role": "user", "content": "請讀取 msg.txt 文件"}]
})

# Tool agent example
result = app.invoke({
    "messages": [{"role": "user", "content": "What's the current time?"}]
})

# Get final response
final_message = result["messages"][-1]
print(final_message.content)
```

## Agents

### read_file_agent

**Purpose**: Read files from `read_file_agent/data/` directory

**Tools**:
- `read_msg_file()`: Reads msg.txt file

**Example requests**:
- "請讀取 msg.txt 文件"
- "Show me the content of msg.txt"
- "Read the file"

### tool_agent

**Purpose**: General utility operations

**Tools**:
- `get_current_time()`: Returns current date and time
- `calculate(expression)`: Safely evaluates math expressions
- `reverse_string(text)`: Reverses a string

**Example requests**:
- "What's the current time?"
- "Calculate 123 * 456"
- "Reverse the string 'hello'"

## Supervisor Logic

The supervisor analyzes user requests and routes them to the appropriate agent:

- File reading requests → `read_file_agent`
- Time/calculation/string operations → `tool_agent`

The supervisor uses an LLM to make intelligent routing decisions based on the user's intent.

## Custom OpenAI Endpoint Compatibility

This system includes a `CustomChatOpenAI` wrapper that removes the `parallel_tool_calls` parameter, which is not supported by some custom OpenAI-compatible endpoints.

```python
class CustomChatOpenAI(ChatOpenAI):
    """Custom ChatOpenAI that doesn't send parallel_tool_calls parameter"""

    def bind_tools(self, tools, **kwargs):
        kwargs.pop("parallel_tool_calls", None)
        return super().bind_tools(tools, **kwargs)
```

## Test Results

All three test cases pass successfully:

✅ **TEST 1**: Read File Request - Successfully reads and returns msg.txt content
✅ **TEST 2**: Tool Agent - Current Time - Returns current timestamp
✅ **TEST 3**: Tool Agent - Calculation - Correctly calculates 123 × 456 = 56,088

## Extending the System

### Add New Agent

1. Create new agent file in `agents/` directory
2. Use `create_react_agent()` with `name` parameter
3. Add to supervisor in [agent.py](supervisor_agent/agent.py):

```python
from supervisor_agent.agents.your_new_agent import your_new_agent

supervisor = create_supervisor(
    agents=[read_file_agent, tool_agent, your_new_agent],
    model=supervisor_model,
    prompt="Updated prompt mentioning new agent..."
)
```

### Add New Tools

Edit the respective agent file and add new `@tool` decorated functions:

```python
@tool
def your_new_tool(param: str) -> str:
    """Description of what the tool does."""
    # Implementation
    return result
```

Then add to the agent's tools list.

## Deployment

This agent is deployment-ready:

- Graph exported as `app`
- `langgraph.json` configuration included
- No checkpointer (stateless by default)
- Compatible with LangGraph Cloud/Platform

Deploy using:
```bash
langgraph up
```

## Architecture Notes

**【Core Judgment】** ✅ Worth doing
- Clean separation of concerns
- Uses prebuilt components (no manual StateGraph)
- Simple, maintainable structure
- Each agent has single responsibility

**【Solution】**
1. ✅ Simplified data structures (MessagesState)
2. ✅ Eliminated special cases (supervisor handles all routing)
3. ✅ Dumbest clear approach (prebuilt components)
4. ✅ Zero breakage (extends existing read_file_agent without modification)

## References

- [LangGraph Supervisor Pattern](https://langchain-ai.github.io/langgraph/reference/supervisor/)
- [create_react_agent Documentation](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
- Project guidelines: [AGENT.md](../doc/AGENT.md), [GEMINI.md](../doc/GEMINI.md)
