"""
Shared state definition for supervisor multi-agent system
"""
from langgraph.graph import MessagesState
from typing import Optional, Dict, Any
from datetime import datetime


class SupervisorState(MessagesState):
    """
    State shared across all agents in supervisor pattern.
    Uses MessagesState as base - contains messages field with add_messages reducer.
    """
    # Additional fields beyond messages
    file_content: Optional[str] = None  # type: ignore # For read_file_agent results
    next: Optional[str] = None  # type: ignore # For supervisor routing decisions
    remaining_steps: int = 25  # type: ignore # Required by create_supervisor (max steps)

    # New fields for DATCOM workflow
    latest_datcom: Optional[Dict[str, Any]] = None  # type: ignore # 最新產生的 DATCOM 內容
    parsed_file_data: Optional[Dict[str, Any]] = None  # type: ignore # 從檔案解析出的結構化資料

    # Conversation context
    conversation_id: Optional[str] = None  # type: ignore # 對話 session ID
    conversation_history_summary: Optional[str] = None  # type: ignore # 對話歷史摘要（節省 token）
