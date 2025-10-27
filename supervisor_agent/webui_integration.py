"""
Open WebUI 整合模組
提供串流介面和對話記憶管理
"""
from typing import Iterator, Dict, Any, Optional
from langchain_core.messages import HumanMessage
from supervisor_agent.agent import app
from supervisor_agent.utils.memory_manager import ConversationMemoryManager, SessionManager


class OpenWebUIAdapter:
    """
    Open WebUI 適配器

    功能：
    1. 串流輸出（yield chunks）
    2. 對話記憶管理
    3. Session 管理
    4. State 持久化支援
    """

    def __init__(
        self,
        enable_memory: bool = True,
        max_recent_messages: int = 4,
        compression_threshold: int = 10
    ):
        """
        初始化適配器

        Args:
            enable_memory: 是否啟用對話記憶管理
            max_recent_messages: 保留最近幾條完整訊息
            compression_threshold: 超過幾條訊息開始壓縮
        """
        self.graph = app
        self.enable_memory = enable_memory

        if enable_memory:
            self.memory_manager = ConversationMemoryManager(
                max_recent_messages=max_recent_messages,
                compression_threshold=compression_threshold
            )
        else:
            self.memory_manager = None

        # 簡單的 session storage（生產環境應使用 Redis 或資料庫）
        self.session_states = {}

    def stream_response(
        self,
        data: Dict[str, Any],
        previous_state: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """
        Open WebUI 串流介面

        Args:
            data: {
                "message": str,           # 使用者訊息
                "session_id": str,        # 可選的 session ID
                "stream_mode": str        # 可選，預設 "updates"
            }
            previous_state: 上一輪對話的 state（可選）

        Yields:
            格式化的串流輸出
        """
        message = data.get("message", "")
        session_id = data.get("session_id")
        stream_mode = data.get("stream_mode", "updates")

        # 準備初始 state
        initial_state = self._prepare_initial_state(
            message=message,
            session_id=session_id,
            previous_state=previous_state
        )

        # 串流執行
        try:
            for chunk in self.graph.stream(initial_state, stream_mode=stream_mode):
                yield from self._format_chunk(chunk)

            # 儲存 state（如果啟用 memory）
            if self.enable_memory and session_id:
                # 這裡應該儲存完整的 final state
                # 在生產環境中，應該從 graph 取得 final state
                pass

        except Exception as e:
            yield f"\n❌ Error: {str(e)}\n\n"

    def _prepare_initial_state(
        self,
        message: str,
        session_id: Optional[str],
        previous_state: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        準備初始 state

        處理：
        1. Session ID
        2. 對話記憶壓縮
        3. 保留重要 state 欄位
        """
        # 新訊息
        new_message = HumanMessage(content=message)

        # 檢查是否為連續對話
        if previous_state and self.enable_memory:
            # 從上一輪 state 恢復
            if self.memory_manager.has_conversation_context(previous_state):
                # 壓縮歷史訊息
                optimized_messages = self.memory_manager.prepare_context_for_llm(
                    previous_state
                )

                # 組合新 state
                return {
                    "messages": optimized_messages + [new_message],
                    "conversation_id": previous_state.get("conversation_id"),
                    # 保留重要的 state 欄位
                    "latest_datcom": previous_state.get("latest_datcom"),
                    "parsed_file_data": previous_state.get("parsed_file_data"),
                    "file_content": previous_state.get("file_content")
                }

        # 新對話
        if not session_id:
            session_id = SessionManager.generate_session_id()

        return {
            "messages": [new_message],
            "conversation_id": session_id
        }

    def _format_chunk(self, chunk: Dict[str, Any]) -> Iterator[str]:
        """
        格式化 chunk 為 Open WebUI 輸出

        Args:
            chunk: LangGraph stream chunk

        Yields:
            格式化的字串
        """
        if "agent" not in chunk:
            return

        # 取得 agent 的 messages
        agent_data = chunk["agent"]
        messages = agent_data.get("messages", [])

        for msg in messages:
            content = getattr(msg, 'content', '')
            if content:
                # 直接輸出內容（包含 <think> 標籤）
                yield f"{content}\n\n"

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        取得 session state

        Args:
            session_id: Session ID

        Returns:
            State dict 或 None
        """
        return self.session_states.get(session_id)

    def save_session_state(self, session_id: str, state: Dict[str, Any]):
        """
        儲存 session state

        Args:
            session_id: Session ID
            state: State dict
        """
        self.session_states[session_id] = state

    def clear_session(self, session_id: str):
        """
        清除 session

        Args:
            session_id: Session ID
        """
        if session_id in self.session_states:
            del self.session_states[session_id]


class ThinkTagFormatter:
    """
    <think> 標籤格式化器
    用於美化輸出
    """

    @staticmethod
    def format_thinking(content: str) -> str:
        """
        格式化包含 <think> 標籤的內容

        將 <think>...</think> 轉換為 Markdown 格式的思考區塊
        """
        import re

        # 匹配 <think>...</think>
        think_pattern = r'<think>(.*?)</think>'

        def replace_think(match):
            thinking_content = match.group(1).strip()
            return f"\n💭 **思考中...**\n```thinking\n{thinking_content}\n```\n\n"

        # 替換所有 <think> 標籤
        formatted = re.sub(think_pattern, replace_think, content, flags=re.DOTALL)

        return formatted


# ==================== 使用範例 ====================

"""
# 基本使用（無記憶）
adapter = OpenWebUIAdapter(enable_memory=False)

for chunk in adapter.stream_response({"message": "請讀取 msg.txt"}):
    print(chunk, end='', flush=True)


# 進階使用（有記憶）
adapter = OpenWebUIAdapter(
    enable_memory=True,
    max_recent_messages=4,
    compression_threshold=10
)

# 第一輪對話
session_id = "user_123_session"
data1 = {
    "message": "請讀取 msg.txt 並產生 DATCOM 檔案",
    "session_id": session_id
}

for chunk in adapter.stream_response(data1):
    print(chunk, end='', flush=True)

# 儲存 state（簡化版，實際應從 graph 取得）
# adapter.save_session_state(session_id, final_state)

# 第二輪對話（連續）
previous_state = adapter.get_session_state(session_id)
data2 = {
    "message": "剛才的翼型是什麼？",
    "session_id": session_id
}

for chunk in adapter.stream_response(data2, previous_state=previous_state):
    print(chunk, end='', flush=True)


# 使用 <think> 標籤格式化
formatter = ThinkTagFormatter()
content_with_think = '''<think>
User wants DATCOM file
Need to route to datcom_tool_agent
</think>
好的，我來產生 DATCOM 檔案'''

formatted = formatter.format_thinking(content_with_think)
print(formatted)

# 輸出：
# 💭 **思考中...**
# ```thinking
# User wants DATCOM file
# Need to route to datcom_tool_agent
# ```
#
# 好的，我來產生 DATCOM 檔案
"""
