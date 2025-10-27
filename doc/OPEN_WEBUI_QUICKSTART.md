# Open WebUI 整合快速入門

## 🚀 快速開始

### 基本整合（無對話記憶）

```python
from supervisor_agent.webui_integration import OpenWebUIAdapter

# 初始化適配器
adapter = OpenWebUIAdapter(enable_memory=False)

# Open WebUI 串流介面
def chat_stream(user_message: str):
    """你的 Open WebUI endpoint"""
    data = {"message": user_message}

    for chunk in adapter.stream_response(data):
        yield chunk

# 使用
for output in chat_stream("請讀取 msg.txt 並產生 DATCOM 檔案"):
    print(output, end='', flush=True)
```

---

### 進階整合（有對話記憶 + Session 管理）

```python
from supervisor_agent.webui_integration import OpenWebUIAdapter

# 初始化適配器（啟用記憶管理）
adapter = OpenWebUIAdapter(
    enable_memory=True,
    max_recent_messages=4,       # 保留最近 4 條完整訊息
    compression_threshold=10     # 超過 10 條開始壓縮
)

# Open WebUI 串流介面（帶 session）
def chat_stream_with_memory(user_message: str, session_id: str = None):
    """你的 Open WebUI endpoint（支援連續對話）"""

    # 取得上一輪的 state（如果有）
    previous_state = None
    if session_id:
        previous_state = adapter.get_session_state(session_id)

    # 準備資料
    data = {
        "message": user_message,
        "session_id": session_id
    }

    # 串流輸出
    for chunk in adapter.stream_response(data, previous_state=previous_state):
        yield chunk

# 第一輪對話
session_id = "user_123"
for output in chat_stream_with_memory("請讀取 msg.txt 並產生 DATCOM 檔案", session_id):
    print(output, end='', flush=True)

# 第二輪對話（連續，可以參考上一輪）
for output in chat_stream_with_memory("剛才的翼型是什麼？", session_id):
    print(output, end='', flush=True)
```

---

## 📊 State 欄位說明

你的系統現在有以下 state 欄位可用：

### 1. `latest_datcom` - 最新的 DATCOM 資訊

```python
{
    "case_id": "PC-9",
    "output_path": "/path/to/for005.dat",
    "generated_at": "2025-10-22T12:34:56",
    "parameters": {
        "flight_conditions": {...},
        "wing": {"naca": "6-63-415", ...},
        "htail": {...},
        "vtail": {...}
    }
}
```

**使用場景**：
- 使用者詢問「剛才用了什麼翼型？」
- 修改參數時參考上次的設定

### 2. `parsed_file_data` - 解析後的檔案資料

```python
{
    "has_datcom_data": True,
    "file_type": "datcom_config",
    "sections": {"titles": [...], "count": 6},
    "key_values": {"NALPHA": "6", "MACH": "0.5489", ...},
    "stats": {"total_chars": 949, "total_lines": 45}
}
```

**使用場景**：
- 快速查詢檔案資訊
- 使用者詢問「檔案裡有幾個章節？」

### 3. `conversation_id` - Session ID

用於追蹤連續對話。

### 4. `conversation_history_summary` - 對話歷史摘要

自動壓縮舊訊息以節省 token。

---

## 🧠 對話記憶管理

### Token 節省效果

**沒有記憶管理**：
```
20 條訊息 × 平均 250 tokens = 5000 tokens
```

**使用記憶管理**：
```
1 條摘要 (200 tokens) + 4 條最近訊息 (1000 tokens) = 1200 tokens
節省: 76%
```

### 自訂記憶策略

```python
# 短對話（保留更多上下文）
adapter = OpenWebUIAdapter(
    enable_memory=True,
    max_recent_messages=6,
    compression_threshold=15
)

# 長對話（積極節省 token）
adapter = OpenWebUIAdapter(
    enable_memory=True,
    max_recent_messages=2,
    compression_threshold=5
)
```

---

## 💭 處理 `<think>` 標籤

你的 LLM 會輸出 `<think>` 標籤，這裡有兩個選擇：

### 選項 A：直接輸出（保留原始格式）

```python
# 預設行為，直接輸出
for chunk in adapter.stream_response(data):
    yield chunk

# 輸出：
# <think>
# User wants DATCOM file...
# </think>
# 好的，我來產生 DATCOM 檔案
```

### 選項 B：格式化為 Markdown（推薦）

```python
from supervisor_agent.webui_integration import ThinkTagFormatter

formatter = ThinkTagFormatter()

for chunk in adapter.stream_response(data):
    # 格式化 <think> 標籤
    formatted = formatter.format_thinking(chunk)
    yield formatted

# 輸出：
# 💭 **思考中...**
# ```thinking
# User wants DATCOM file...
# ```
#
# 好的，我來產生 DATCOM 檔案
```

---

## 🔧 完整 Open WebUI 整合範例

```python
from supervisor_agent.webui_integration import (
    OpenWebUIAdapter,
    ThinkTagFormatter
)
from typing import Iterator

class ChatService:
    """你的 Chat Service"""

    def __init__(self):
        self.adapter = OpenWebUIAdapter(
            enable_memory=True,
            max_recent_messages=4,
            compression_threshold=10
        )
        self.formatter = ThinkTagFormatter()

    def stream_chat(
        self,
        user_message: str,
        session_id: str = None,
        format_thinking: bool = True
    ) -> Iterator[str]:
        """
        串流聊天介面

        Args:
            user_message: 使用者訊息
            session_id: Session ID（連續對話）
            format_thinking: 是否格式化 <think> 標籤

        Yields:
            格式化的輸出
        """
        # 取得上一輪 state
        previous_state = None
        if session_id:
            previous_state = self.adapter.get_session_state(session_id)

        # 準備資料
        data = {
            "message": user_message,
            "session_id": session_id
        }

        # 串流輸出
        for chunk in self.adapter.stream_response(data, previous_state):
            if format_thinking:
                # 格式化 <think> 標籤
                chunk = self.formatter.format_thinking(chunk)

            yield chunk

    def clear_session(self, session_id: str):
        """清除 session"""
        self.adapter.clear_session(session_id)


# 使用範例
service = ChatService()

# 第一輪對話
print("User: 請讀取 msg.txt 並產生 DATCOM 檔案")
print("AI: ", end='')
for output in service.stream_chat(
    user_message="請讀取 msg.txt 並產生 DATCOM 檔案",
    session_id="user_123",
    format_thinking=True
):
    print(output, end='', flush=True)

print("\n" + "="*60)

# 第二輪對話（連續）
print("User: 剛才的翼型是什麼？")
print("AI: ", end='')
for output in service.stream_chat(
    user_message="剛才的翼型是什麼？",
    session_id="user_123",
    format_thinking=True
):
    print(output, end='', flush=True)
```

---

## 🎯 Open WebUI 整合檢查清單

### 必須實作

- [x] 串流介面（`yield` chunks）
- [x] Session 管理
- [x] 錯誤處理

### 建議實作

- [x] 對話記憶管理（節省 token）
- [x] `<think>` 標籤格式化
- [x] State 持久化（使用 Redis 或資料庫）

### 可選實作

- [ ] 多使用者並發處理
- [ ] Rate limiting
- [ ] Logging 和 monitoring

---

## 🐛 除錯工具

### 檢查 State 內容

```python
def debug_state(state):
    """列印 state 關鍵資訊"""
    print(f"Messages: {len(state.get('messages', []))}")
    print(f"Session: {state.get('conversation_id', 'None')}")
    print(f"Latest DATCOM: {'✅' if state.get('latest_datcom') else '❌'}")
    print(f"Parsed file: {'✅' if state.get('parsed_file_data') else '❌'}")

# 使用
result = adapter.get_session_state(session_id)
if result:
    debug_state(result)
```

---

## 📚 相關文件

- **詳細指南**: [doc/STATE_AND_MEMORY_GUIDE.md](doc/STATE_AND_MEMORY_GUIDE.md)
- **API 文件**: `supervisor_agent/webui_integration.py`
- **測試範例**: `supervisor_agent/test/test_new_features.py`

---

## ❓ 常見問題

### Q1: 對話連續性如何判斷？

A: 基於 `session_id`。相同 `session_id` = 連續對話。

### Q2: 如何清除對話記憶？

A:
```python
adapter.clear_session(session_id)
# 或傳遞新的 session_id
```

### Q3: `<think>` 標籤一定要格式化嗎？

A: 不一定。你可以：
- 直接輸出（Open WebUI 顯示原始 HTML-like 標籤）
- 格式化為 Markdown（更美觀）
- 完全移除（使用正則）

### Q4: 如何存取 `latest_datcom` 資訊？

A:
```python
previous_state = adapter.get_session_state(session_id)
if previous_state and previous_state.get("latest_datcom"):
    wing_naca = previous_state["latest_datcom"]["parameters"]["wing"]["naca"]
```

### Q5: 記憶管理會影響效能嗎？

A: 輕微影響（壓縮需要時間），但節省的 token 帶來更大的速度提升。

---

**最後更新**: 2025-10-22
**版本**: 1.0
