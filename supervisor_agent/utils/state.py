"""
Shared state definition for supervisor multi-agent system
"""
from langgraph.graph import MessagesState
from typing import Optional


class SupervisorState(MessagesState):
    """
    State shared across all agents in supervisor pattern.
    Uses MessagesState as base - contains messages field with add_messages reducer.
    """
    # Additional fields beyond messages
    file_content: Optional[str] = None  # type: ignore # For read_file_agent results
    next: Optional[str] = None  # type: ignore # For supervisor routing decisions
    remaining_steps: int = 25  # type: ignore # Required by create_supervisor (max steps)
