# State 管理與對話記憶指南

## 📊 新增的 State 欄位

### 1. `latest_datcom` - 最新產生的 DATCOM 內容

**用途**: 記錄最近一次產生的 DATCOM 檔案資訊

**資料結構**:
```python
{
    "case_id": "PC-9",
    "output_path": "/path/to/for005.dat",
    "generated_at": "2025-10-22T12:34:56",
    "parameters": {
        "flight_conditions": {
            "nalpha": 6,
            "alschd": "1.0,2.0,3.0,4.0,5.0,6.0",
            "nmach": 1,
            "mach": "0.5489",
            ...
        },
        "wing": {
            "naca": "6-63-415",
            "chrdtp": 3.7402,
            ...
        },
        "htail": {...},
        "vtail": {...}
    }
}
```

**使用場景**:
- ✅ 讓使用者查詢「剛才產生的 DATCOM 用了什麼參數？」
- ✅ 修改參數時可以參考上一次的設定
- ✅ 對話記憶：「使用上次相同的翼型」

**如何訪問**:
```python
# 在 agent 中
if state.get("latest_datcom"):
    last_params = state["latest_datcom"]["parameters"]
    print(f"上次使用的翼型: {last_params['wing']['naca']}")
```

---

### 2. `parsed_file_data` - 解析後的檔案資料

**用途**: 記錄從檔案中解析出的結構化資料

**資料結構**:
```python
{
    "has_datcom_data": True,
    "file_type": "datcom_config",
    "sections": {
        "titles": ["飛行條件", "合成參數", "機身外形", ...],
        "count": 6
    },
    "key_values": {
        "NALPHA": "6",
        "MACH": "0.5489",
        "XCG": "11.3907",
        ...
    },
    "stats": {
        "total_chars": 949,
        "total_lines": 45,
        "has_numbers": True,
        "has_sections": True
    },
    "data_preview": "## PC-9 飛機 DATCOM 配置..."
}
```

**使用場景**:
- ✅ 快速檢查檔案類型（是否為 DATCOM 配置）
- ✅ 提取關鍵參數而不需要重新解析完整文字
- ✅ 對話記憶：「檔案裡有幾個章節？」「馬赫數是多少？」

**如何訪問**:
```python
# 檢查檔案類型
if state.get("parsed_file_data"):
    parsed = state["parsed_file_data"]
    if parsed["has_datcom_data"]:
        print(f"這是 DATCOM 配置檔案，包含 {parsed['sections']['count']} 個章節")
        print(f"馬赫數: {parsed['key_values'].get('MACH', 'N/A')}")
```

---

### 3. `conversation_id` - 對話 Session ID

**用途**: 識別連續對話

**資料格式**: `"session_20251022_123456_a1b2c3"`

**使用場景**:
- ✅ 判斷是新對話還是連續對話
- ✅ Open WebUI 整合時傳遞 session ID
- ✅ 實現對話持久化（如果需要）

---

### 4. `conversation_history_summary` - 對話歷史摘要

**用途**: 壓縮舊對話以節省 token

**資料格式**: 字串摘要

**範例**:
```
User: 請讀取 msg.txt...
AI: 已讀取檔案...
User: 產生 DATCOM 檔案...
AI: DATCOM 檔案已產生...
```

**使用場景**:
- ✅ 超過 10 條訊息時自動壓縮
- ✅ 保留最近 4 條完整訊息
- ✅ 將舊訊息壓縮成摘要

---

## 🧠 對話記憶管理

### ConversationMemoryManager

**初始化**:
```python
from supervisor_agent.utils.memory_manager import ConversationMemoryManager

memory_manager = ConversationMemoryManager(
    max_recent_messages=4,       # 保留最近 4 條完整訊息
    max_summary_length=500,      # 摘要最大 500 字元
    compression_threshold=10     # 超過 10 條訊息才壓縮
)
```

**功能 1: 檢測對話連續性**

```python
# 判斷是否為連續對話
if memory_manager.has_conversation_context(state):
    print("✅ 這是連續對話，可以參考歷史")
else:
    print("🆕 這是新對話")
```

**功能 2: 準備優化的 LLM Context**

```python
# 自動壓縮訊息，節省 token
optimized_messages = memory_manager.prepare_context_for_llm(state)

# optimized_messages 包含：
# - 如果超過 10 條：[SystemMessage(摘要)] + 最近 4 條
# - 如果不超過：所有訊息
```

**功能 3: 提取關鍵資訊**

```python
key_info = memory_manager.extract_key_info_from_messages(state["messages"])

print(f"DATCOM 已產生: {key_info['datcom_generated']}")
print(f"檔案已讀取: {key_info['file_read']}")
print(f"最後請求: {key_info['last_user_request']}")
```

---

## 🔄 Open WebUI 整合

### 基本整合

```python
from supervisor_agent.agent import app
from supervisor_agent.utils.memory_manager import ConversationMemoryManager, SessionManager

memory_manager = ConversationMemoryManager()

def stream_to_webui(data):
    """
    Open WebUI 串流介面

    Args:
        data: {
            "message": "使用者輸入",
            "session_id": "可選的 session ID"
        }
    """
    # 1. 準備初始 state
    from langchain_core.messages import HumanMessage

    initial_state = {
        "messages": [HumanMessage(content=data["message"])]
    }

    # 2. 檢查是否為連續對話
    if "session_id" in data and data["session_id"]:
        initial_state["conversation_id"] = data["session_id"]
    else:
        # 生成新的 session ID
        initial_state["conversation_id"] = SessionManager.generate_session_id()

    # 3. 串流執行
    for chunk in app.stream(initial_state, stream_mode="updates"):
        if "agent" in chunk:
            for msg in chunk["agent"].get("messages", []):
                content = getattr(msg, 'content', '')
                if content:
                    yield f"{content}\n\n"

    yield "\n\n"
```

### 帶記憶管理的整合

```python
def stream_with_memory(data, previous_state=None):
    """
    帶對話記憶的串流介面

    Args:
        data: {"message": str, "session_id": str}
        previous_state: 上一輪對話的 state（如果有）
    """
    from langchain_core.messages import HumanMessage

    # 如果有上一輪 state，繼續對話
    if previous_state and memory_manager.has_conversation_context(previous_state):
        # 連續對話
        print("📝 連續對話模式")

        # 壓縮歷史訊息
        optimized_messages = memory_manager.prepare_context_for_llm(previous_state)

        # 添加新的使用者訊息
        new_state = {
            **previous_state,
            "messages": optimized_messages + [HumanMessage(content=data["message"])]
        }
    else:
        # 新對話
        print("🆕 新對話模式")
        new_state = {
            "messages": [HumanMessage(content=data["message"])],
            "conversation_id": SessionManager.generate_session_id()
        }

    # 串流執行
    for chunk in app.stream(new_state, stream_mode="updates"):
        if "agent" in chunk:
            for msg in chunk["agent"].get("messages", []):
                content = getattr(msg, 'content', '')
                if content:
                    yield f"{content}\n\n"

    yield "\n\n"
```

---

## 🎯 使用範例

### 範例 1: 查詢最近的 DATCOM 參數

**使用者**: "剛才產生的 DATCOM 用了什麼翼型？"

```python
# 在 agent 的 prompt 中可以這樣引導：
"""
如果使用者詢問「剛才」「上次」「最近」產生的 DATCOM 資訊：
- 檢查 state.latest_datcom
- 提取相關參數並回答
"""

# Supervisor 會看到：
state = {
    "latest_datcom": {
        "parameters": {
            "wing": {"naca": "6-63-415", ...}
        }
    }
}

# 回應：
"剛才產生的 DATCOM 使用的翼型是 NACA 6-63-415"
```

---

### 範例 2: 參考檔案解析結果

**使用者**: "檔案裡有幾個章節？"

```python
# Agent 可以直接從 parsed_file_data 取得
state = {
    "parsed_file_data": {
        "sections": {
            "titles": ["飛行條件", "合成參數", ...],
            "count": 6
        }
    }
}

# 回應：
"檔案包含 6 個章節：飛行條件、合成參數、機身外形、主翼、水平尾翼、垂直尾翼"
```

---

### 範例 3: 連續對話修改參數

**第一輪對話**:
```
User: 請讀取 msg.txt 並產生 DATCOM 檔案
AI: ✅ 已產生 for005.dat
State: {
    "latest_datcom": {"parameters": {"wing": {"naca": "6-63-415"}}},
    "conversation_id": "session_123"
}
```

**第二輪對話**（同一個 session）:
```
User: 把翼型改成 NACA 2412
AI: 我會使用上次的參數，只修改翼型為 NACA 2412
    [參考 state.latest_datcom 的其他參數]
    ✅ 已產生新的 for005.dat
```

---

## 📊 Token 節省效果

### 沒有記憶管理

```
消息數: 20 條
總 tokens: ~5000
問題: 大量冗余的中間步驟訊息
```

### 使用記憶管理

```
消息數: 20 條 → 壓縮為 1 條摘要 + 4 條最近訊息
總 tokens: ~1500
節省: 70%
```

---

## ⚙️ 配置建議

### 短對話場景（<10 輪）

```python
memory_manager = ConversationMemoryManager(
    max_recent_messages=6,       # 保留更多最近訊息
    compression_threshold=15     # 較高的壓縮閾值
)
```

### 長對話場景（>20 輪）

```python
memory_manager = ConversationMemoryManager(
    max_recent_messages=3,       # 只保留最近 3 條
    max_summary_length=300,      # 更短的摘要
    compression_threshold=8      # 更早開始壓縮
)
```

### 高效能要求

```python
memory_manager = ConversationMemoryManager(
    max_recent_messages=2,       # 最少保留
    max_summary_length=200,      # 極簡摘要
    compression_threshold=5      # 積極壓縮
)
```

---

## 🔍 除錯工具

### 檢查 State 內容

```python
def debug_state(state):
    """列印 state 的關鍵資訊"""
    print("=" * 60)
    print("📊 State Debug Info")
    print("=" * 60)

    # 基本資訊
    print(f"Messages: {len(state.get('messages', []))} 條")
    print(f"Conversation ID: {state.get('conversation_id', 'None')}")

    # DATCOM 相關
    if state.get("latest_datcom"):
        print(f"✅ Latest DATCOM: {state['latest_datcom']['case_id']}")
        print(f"   Generated at: {state['latest_datcom']['generated_at']}")
    else:
        print("❌ No DATCOM data")

    # 檔案解析
    if state.get("parsed_file_data"):
        parsed = state["parsed_file_data"]
        print(f"✅ Parsed file: {parsed['file_type']}")
        print(f"   Sections: {parsed.get('sections', {}).get('count', 0)}")
    else:
        print("❌ No parsed file data")

    # 記憶管理
    if state.get("conversation_history_summary"):
        summary = state["conversation_history_summary"]
        print(f"📝 History summary: {len(summary)} chars")
    else:
        print("🆕 No conversation history")

    print("=" * 60)
```

---

## 📚 相關檔案

- **State 定義**: `supervisor_agent/utils/state.py`
- **記憶管理**: `supervisor_agent/utils/memory_manager.py`
- **DATCOM Agent**: `datcom_tool_agent/agent.py` (更新 latest_datcom)
- **Read File Agent**: `read_file_agent/agent.py` (更新 parsed_file_data)

---

## ❓ 常見問題

### Q1: 對話連續性如何判斷？

A: 基於 `conversation_id`：
- 有相同 `conversation_id` = 連續對話
- 沒有或不同 = 新對話

### Q2: 如何清除對話記憶？

A: 傳遞新的 `conversation_id` 或不傳遞（系統會生成新的）

### Q3: `latest_datcom` 會被覆蓋嗎？

A: 是的，每次產生新 DATCOM 會覆蓋。如果需要保留歷史，需要另外實現歷史記錄。

### Q4: 記憶管理會影響效能嗎？

A: 輕微影響（壓縮需要處理時間），但節省的 token 帶來的速度提升更大。

---

**最後更新**: 2025-10-22
**相關議題**: Open WebUI 整合, Token 優化, 對話記憶
