"""
Conversation Memory Manager
管理對話記憶，有效率地節省 token
"""
from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from datetime import datetime
import json


class ConversationMemoryManager:
    """
    對話記憶管理器

    功能：
    1. 檢測對話連續性（基於 conversation_id）
    2. 壓縮歷史訊息以節省 token
    3. 保留關鍵資訊（最近的對話、重要的結果）
    """

    def __init__(
        self,
        max_recent_messages: int = 4,  # 保留最近 N 條完整訊息
        max_summary_length: int = 500,  # 摘要最大長度
        compression_threshold: int = 10  # 超過 N 條訊息才進行壓縮
    ):
        self.max_recent_messages = max_recent_messages
        self.max_summary_length = max_summary_length
        self.compression_threshold = compression_threshold

    def has_conversation_context(self, state: Dict[str, Any]) -> bool:
        """
        檢查是否有對話上下文

        Returns:
            True 如果有 conversation_id，表示是連續對話
            False 如果是新對話
        """
        return bool(state.get("conversation_id"))

    def compress_messages(
        self,
        messages: List[BaseMessage],
        keep_recent: int = None
    ) -> tuple[List[BaseMessage], str]:
        """
        壓縮 messages，返回：
        1. 保留的最近訊息
        2. 歷史摘要字串

        策略：
        - 保留最近 N 條完整訊息（保持對話流暢）
        - 將舊訊息壓縮成摘要
        - 過濾掉冗長的中間步驟（如 ToolMessage）
        """
        keep_recent = keep_recent or self.max_recent_messages

        if len(messages) <= self.compression_threshold:
            # 訊息不多，不需要壓縮
            return messages, ""

        # 分割：舊訊息 vs 最近訊息
        old_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]

        # 生成舊訊息摘要
        summary = self._summarize_messages(old_messages)

        return recent_messages, summary

    def _summarize_messages(self, messages: List[BaseMessage]) -> str:
        """
        將一組訊息壓縮成摘要

        只保留關鍵資訊：
        - 使用者請求
        - 最終結果
        - 重要的中間步驟（如 DATCOM 產生）
        """
        summary_parts = []

        for msg in messages:
            content = getattr(msg, 'content', '')
            msg_type = type(msg).__name__

            # 使用者訊息：保留完整
            if isinstance(msg, HumanMessage):
                summary_parts.append(f"User: {content[:100]}...")

            # AI 回應：保留關鍵資訊
            elif isinstance(msg, AIMessage):
                # 檢查是否包含重要關鍵字
                important_keywords = [
                    'DATCOM', '檔案', '產生', '完成', '成功',
                    'file', 'generated', 'completed', 'success'
                ]

                if any(kw in content for kw in important_keywords):
                    # 保留重要回應
                    summary_parts.append(f"AI: {content[:100]}...")

        # 限制摘要長度
        full_summary = '\n'.join(summary_parts)
        if len(full_summary) > self.max_summary_length:
            full_summary = full_summary[:self.max_summary_length] + "..."

        return full_summary

    def prepare_context_for_llm(self, state: Dict[str, Any]) -> List[BaseMessage]:
        """
        準備給 LLM 的上下文（已優化 token 使用）

        返回：壓縮後的 messages + 摘要（如果有的話）
        """
        messages = state.get("messages", [])

        if len(messages) <= self.compression_threshold:
            # 不需要壓縮
            return messages

        # 壓縮訊息
        recent_messages, old_summary = self.compress_messages(messages)

        # 如果有舊摘要，添加為 SystemMessage
        if old_summary:
            summary_msg = SystemMessage(
                content=f"[對話歷史摘要]\n{old_summary}\n[以下是最近的對話]"
            )
            return [summary_msg] + recent_messages

        return recent_messages

    def extract_key_info_from_messages(
        self,
        messages: List[BaseMessage]
    ) -> Dict[str, Any]:
        """
        從訊息中提取關鍵資訊

        用於：
        - 記錄最近產生的 DATCOM 參數
        - 記錄解析出的檔案資料
        """
        key_info = {
            "datcom_generated": False,
            "datcom_params": None,
            "file_read": False,
            "file_content_preview": None,
            "last_user_request": None,
            "last_ai_response": None
        }

        for msg in reversed(messages):  # 從最新開始
            content = getattr(msg, 'content', '')

            # 最後的使用者請求
            if isinstance(msg, HumanMessage) and not key_info["last_user_request"]:
                key_info["last_user_request"] = content[:200]

            # 最後的 AI 回應
            if isinstance(msg, AIMessage) and not key_info["last_ai_response"]:
                key_info["last_ai_response"] = content[:200]

            # DATCOM 相關資訊
            if 'DATCOM' in content or 'for005.dat' in content:
                key_info["datcom_generated"] = True
                # 嘗試提取參數（簡單版本）
                if 'NALPHA' in content:
                    key_info["datcom_params"] = "Found DATCOM parameters in message"

            # 檔案讀取資訊
            if '已讀取' in content or 'read' in content.lower():
                key_info["file_read"] = True
                key_info["file_content_preview"] = content[:100]

        return key_info


class SessionManager:
    """
    Session 管理器
    處理對話 ID 和持久化（如果需要的話）
    """

    @staticmethod
    def generate_session_id() -> str:
        """生成新的 session ID"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import random
        random_suffix = ''.join(random.choices('0123456789abcdef', k=6))
        return f"session_{timestamp}_{random_suffix}"

    @staticmethod
    def is_same_session(
        state: Dict[str, Any],
        incoming_session_id: Optional[str]
    ) -> bool:
        """
        判斷是否為同一個 session

        Args:
            state: 當前 state
            incoming_session_id: 傳入的 session ID（來自客戶端）

        Returns:
            True 如果是同一個 session（連續對話）
        """
        current_session = state.get("conversation_id")

        if not current_session or not incoming_session_id:
            # 沒有 session ID，視為新對話
            return False

        return current_session == incoming_session_id


# 使用範例
"""
# 在你的 agent 或 supervisor 中使用：

memory_manager = ConversationMemoryManager(
    max_recent_messages=4,  # 保留最近 4 條訊息
    compression_threshold=10  # 超過 10 條才壓縮
)

# 1. 檢查是否有對話上下文
if memory_manager.has_conversation_context(state):
    print("這是連續對話")
else:
    print("這是新對話")

# 2. 準備給 LLM 的上下文（已優化）
optimized_messages = memory_manager.prepare_context_for_llm(state)

# 3. 提取關鍵資訊
key_info = memory_manager.extract_key_info_from_messages(state["messages"])
print(f"DATCOM 已產生: {key_info['datcom_generated']}")
"""
