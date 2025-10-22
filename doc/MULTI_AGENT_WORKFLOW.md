# Multi-Agent Workflow: Read File → Generate DATCOM

## 🎯 目標

實現 Supervisor 協調多個 agents 的協同工作流程：
1. **read_file_agent** 讀取 msg.txt → 存入 `state.file_content`
2. **datcom_tool_agent** 讀取 `state.file_content` → 解析 → 產生 for005.dat

## 🏗️ 架構

```
用戶請求: "讀取 msg.txt 並產生 DATCOM 檔案"
    ↓
┌─────────────────────────────────────────┐
│  Supervisor (LLM-based routing)         │
│  - 分析用戶請求                          │
│  - 識別為多步驟工作流程                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Step 1: read_file_agent                │
│  - 讀取 msg.txt                          │
│  - 存入 state.file_content               │
└─────────────────────────────────────────┘
    ↓ (state.file_content = "...")
┌─────────────────────────────────────────┐
│  Step 2: datcom_tool_agent              │
│  - 檢查 state.file_content               │
│  - LLM 解析內容                          │
│  - 提取 57 個參數                        │
│  - 呼叫 write_datcom_file tool          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  output/for005.dat ✅                   │
└─────────────────────────────────────────┘
```

## 🔑 關鍵實現

### 1. SupervisorState (共享狀態)

**檔案**: `supervisor_agent/utils/state.py`

```python
from langgraph.graph import MessagesState
from typing import Optional

class SupervisorState(MessagesState):
    """
    State shared across all agents in supervisor pattern.
    """
    file_content: Optional[str] = None  # ✅ 用於共享檔案內容
    next: Optional[str] = None
    remaining_steps: int = 25
```

**關鍵點**:
- ✅ 繼承 `MessagesState`（包含 messages 和 add_messages reducer）
- ✅ 添加 `file_content` 欄位讓 agents 共享數據
- ✅ 所有 agents 都使用同一個 state schema

### 2. read_file_agent (讀檔並存入 state)

**檔案**: `read_file_agent/agent.py`

```python
def read_file_node(state: AgentState) -> dict:
    """讀取 msg.txt 文件並存到 state"""
    # ... 讀取檔案 ...
    content = f.read()

    return {
        "messages": [response],
        "file_content": content  # ✅ 存入 state
    }
```

**關鍵點**:
- ✅ 讀取檔案後回傳 `file_content`
- ✅ 同時也在 `messages` 中包含回應（讓用戶看到）

### 3. datcom_tool_agent (讀取 state.file_content)

**檔案**: `datcom_tool_agent/agent.py`

**修改 1: 使用 SupervisorState**
```python
from supervisor_agent.utils.state import SupervisorState

datcom_tool_agent = create_react_agent(
    model=model,
    tools=[write_datcom_file],
    state_schema=SupervisorState,  # ✅ 使用 SupervisorState
    prompt="""...""",
    name="datcom_tool_agent"
)
```

**修改 2: 更新 Prompt**
```python
prompt="""You are a DATCOM file generation specialist.

Your job is to:
1. Check if there is file content in state.file_content (from read_file_agent)
2. If file_content exists, use that as the primary source
3. Otherwise, analyze the user's message
4. Extract all required parameters
5. Call the write_datcom_file tool

IMPORTANT - Accessing file_content:
- The state contains a 'file_content' field
- If you see previous messages from read_file_agent, the content is in state.file_content
- Always prioritize state.file_content over user message if it exists
"""
```

**關鍵點**:
- ✅ Agent 知道去檢查 `state.file_content`
- ✅ 優先使用 `file_content`，沒有才用 user message
- ✅ LLM 會自動解析 `file_content` 中的數據

### 4. Supervisor (協調多步驟工作流程)

**檔案**: `supervisor_agent/agent.py`

**更新的 Prompt**:
```python
prompt="""You are a supervisor managing three specialized agents:

1. read_file_agent: Handles file reading
   - Stores file content in state.file_content

2. tool_agent: General utilities

3. datcom_tool_agent: DATCOM file generation
   - Can read from state.file_content

MULTI-STEP WORKFLOWS:
When user requests to "read file AND generate DATCOM":
1. First route to read_file_agent
   - File content will be stored in state.file_content
2. Then route to datcom_tool_agent
   - Will automatically access state.file_content

Examples:
- "讀取 msg.txt 並產生 DATCOM 檔案" → read_file_agent THEN datcom_tool_agent
- "請根據 msg.txt 的內容產生 for005.dat" → read_file_agent THEN datcom_tool_agent
"""
```

**關鍵點**:
- ✅ Supervisor 知道這是多步驟工作流程
- ✅ 明確說明順序：先讀檔，再處理
- ✅ 提供範例讓 LLM 理解

## 📝 測試檔案

### msg.txt (測試數據)

**位置**: `read_file_agent/data/msg.txt`

```
## PC-9 飛機 DATCOM 配置

## 飛行條件
NALPHA=6
ALSCHD= 1.0,2.0,3.0,4.0,5.0,6.0
NMACH= 1
MACH= 0.5489
...
```

### 測試腳本

**位置**: `supervisor_agent/test_datcom_workflow.py`

```bash
cd /home/c1140921/Operation_Phoenix
python3 -m supervisor_agent.test_datcom_workflow
```

**測試內容**:
1. ✅ 多步驟工作流程（讀檔 → 產生 DATCOM）
2. ✅ 直接產生（不讀檔，數據在 message 中）
3. ✅ 驗證 state.file_content 是否正確傳遞
4. ✅ 檢查輸出檔案是否產生

## 🔄 完整工作流程

### 場景 1: 讀檔後產生 DATCOM

```
1. 用戶輸入
   "讀取 msg.txt 並產生 DATCOM 檔案"

2. Supervisor 分析
   → 識別關鍵字: "讀取 msg.txt", "產生 DATCOM"
   → 判斷為多步驟工作流程

3. 路由到 read_file_agent
   → read_file_agent 讀取 msg.txt
   → 存入 state.file_content
   → 回傳訊息: "已讀取 msg.txt 文件內容"

4. Supervisor 繼續
   → 看到檔案已讀取
   → 路由到 datcom_tool_agent

5. datcom_tool_agent 處理
   → 檢查 state.file_content ✅
   → LLM 解析內容
   → 提取參數:
     - nalpha=6
     - alschd="1.0,2.0,3.0,4.0,5.0,6.0"
     - ... (共 57 個)
   → 呼叫 write_datcom_file tool

6. write_datcom_file tool 執行
   → 建立 Pydantic models
   → 驗證數據 ✅
   → 呼叫 DatcomGenerator
   → 格式化輸出
   → 寫入 output/for005.dat

7. 回傳結果
   "✅ Successfully wrote DATCOM file to: .../output/for005.dat"
```

### 場景 2: 直接產生（不讀檔）

```
1. 用戶輸入
   "產生 DATCOM 檔案: 攻角 1-6 度, 馬赫數 0.5..."

2. Supervisor 分析
   → 識別: "產生 DATCOM"
   → 數據在 message 中
   → 直接路由到 datcom_tool_agent

3. datcom_tool_agent 處理
   → 檢查 state.file_content → 無
   → 從 user message 解析數據
   → 提取參數
   → 呼叫 write_datcom_file tool

4. 產生檔案
   → output/for005.dat ✅
```

## 🎨 設計決策

### ✅ 為什麼用 state.file_content？

**選項 A**: 用 state.file_content（✅ 選擇）
```python
class SupervisorState(MessagesState):
    file_content: Optional[str] = None
```

**選項 B**: 只用 messages（❌ 不選）
```python
# datcom_tool_agent 需要從 messages 中搜尋 read_file_agent 的回應
# 複雜、不可靠
```

**理由**:
- ✅ 明確的數據傳遞（explicit is better than implicit）
- ✅ 類型安全（Optional[str]）
- ✅ 容易測試和 debug
- ✅ 遵循 LangGraph 最佳實踐

### ✅ 為什麼 datcom_tool_agent 用 state_schema？

`create_react_agent` 預設只用 `MessagesState`，需要明確指定：

```python
datcom_tool_agent = create_react_agent(
    state_schema=SupervisorState,  # ✅ 必須指定
    ...
)
```

否則 agent 看不到 `file_content` 欄位。

### ✅ 為什麼在 Prompt 中明確說明？

雖然 state 有 `file_content`，但 LLM 需要知道：
- 這個欄位存在
- 什麼時候使用
- 如何使用

在 prompt 中明確說明可以：
- ✅ 提高準確率
- ✅ 減少錯誤
- ✅ 讓行為可預測

## 🧪 測試方式

### 前提條件

1. **LLM API 運行中**
   ```bash
   # 確認 .env 中的 API endpoint 可用
   # OPENAI_API_BASE_URL=http://172.16.120.65:8089/v1
   ```

2. **msg.txt 存在**
   ```bash
   ls -la read_file_agent/data/msg.txt
   ```

3. **輸出目錄存在**
   ```bash
   mkdir -p datcom_tool_agent/output
   ```

### 執行測試

```bash
cd /home/c1140921/Operation_Phoenix
python3 -m supervisor_agent.test_datcom_workflow
```

### 預期輸出

```
╔══════════════════════════════════════════════════════════════════════════════╗
║               SUPERVISOR MULTI-AGENT DATCOM WORKFLOW TEST                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
🚀 Testing Multi-Agent Workflow: Read File → Generate DATCOM
================================================================================

📝 User Request:
請讀取 msg.txt 文件並根據內容產生 DATCOM 檔案

================================================================================
🔄 Running workflow...

================================================================================
📊 Workflow Results:
================================================================================

[Message 1] HumanMessage
----------------------------------------
請讀取 msg.txt 文件並根據內容產生 DATCOM 檔案

[Message 2] AIMessage
From: read_file_agent
----------------------------------------
📄 已讀取 msg.txt 文件內容：

## PC-9 飛機 DATCOM 配置
...

[Message 3] AIMessage
From: datcom_tool_agent
----------------------------------------
✅ Successfully wrote DATCOM file to: .../output/for005.dat

================================================================================
📋 Final State:
================================================================================

✅ file_content exists: 1234 characters
First 200 characters:
## PC-9 飛機 DATCOM 配置

## 飛行條件
NALPHA=6
ALSCHD= 1.0,2.0,3.0,4.0,5.0,6.0
...

================================================================================
✅ Test completed!
================================================================================

🎉 SUCCESS! DATCOM file created at: .../output/for005.dat

📄 File preview:
  CASEID PC-9
  $FLTCON NALPHA=6.0,ALSCHD=1.0,2.0,3.0,4.0,5.0,6.0,NMACH=1.0,MACH=0.5489,...$
  ...
```

## 🚨 可能的問題和解決方案

### 問題 1: datcom_tool_agent 看不到 file_content

**症狀**: Agent 說 "No file content found"

**原因**: state_schema 沒設定

**解決**:
```python
datcom_tool_agent = create_react_agent(
    state_schema=SupervisorState,  # ← 必須加這行
    ...
)
```

### 問題 2: Supervisor 不知道要先讀檔

**症狀**: 直接路由到 datcom_tool_agent，跳過 read_file_agent

**原因**: Supervisor prompt 不夠清楚

**解決**: 在 prompt 中加入明確的範例和指示

### 問題 3: LLM 解析失敗

**症狀**: 參數提取錯誤或缺失

**原因**: msg.txt 格式不清楚

**解決**:
- 使用結構化格式（如當前的 key=value 格式）
- 在 datcom_tool_agent prompt 中提供解析範例

### 問題 4: Pydantic 驗證失敗

**症狀**: "ValidationError: len(alschd) != nalpha"

**原因**: LLM 提取的參數數量不一致

**解決**:
- LLM 會看到錯誤訊息並自動重試
- 確保 msg.txt 中的數據一致

## 📚 相關文檔

- [supervisor_agent/README.md](../supervisor_agent/README.md) - Supervisor 架構
- [datcom_tool_agent/README.md](../datcom_tool_agent/README.md) - DATCOM Agent 使用指南
- [datcom_tool_agent/DESIGN.md](../datcom_tool_agent/DESIGN.md) - 設計文檔
- [AGENT.md](AGENT.md) - LangGraph 開發原則
- [GEMINI.md](GEMINI.md) - Linus Torvalds 人格設定

## 🎓 學到的經驗

### 1. State Schema 很重要

`create_react_agent` 預設只用 `MessagesState`，需要明確指定 `state_schema`。

### 2. Prompt 需要明確

即使 state 有欄位，也要在 prompt 中說明：
- 欄位的用途
- 什麼時候用
- 如何用

### 3. 測試很關鍵

多步驟工作流程容易出錯，需要完整的測試腳本來驗證。

### 4. 錯誤處理要完善

LLM 可能會：
- 漏掉參數
- 提取錯誤的值
- 格式不對

Pydantic 驗證可以捕捉這些錯誤，讓 LLM 有機會重試。

## 總結

✅ **成功實現多 Agent 協同工作流程**

**關鍵組件**:
1. SupervisorState（共享狀態）
2. read_file_agent（讀檔並存 state）
3. datcom_tool_agent（讀 state 並處理）
4. Supervisor（協調流程）

**遵循原則**:
- ✅ 明確的數據傳遞（state.file_content）
- ✅ 單一職責（每個 agent 做一件事）
- ✅ 可測試（完整的測試腳本）
- ✅ 錯誤處理（Pydantic 驗證）

**可用於生產環境** 🚀
