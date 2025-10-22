# 工作流程視覺化圖表

## 🎨 完整 Message 流程圖

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPERATION PHOENIX WORKFLOW                           │
│                  "請讀取 msg.txt 並產生 DATCOM 檔案"                         │
└─────────────────────────────────────────────────────────────────────────────┘

👤 User
  │
  │ #1: HumanMessage
  │ "請讀取 msg.txt 並產生 DATCOM 檔案"
  │
  ▼
┌─────────────────────────┐
│   SUPERVISOR            │  state.file_content = None
│   (分析請求)            │
└─────────────────────────┘
  │
  │ #2: AIMessage + Tool Call
  │ transfer_to_read_file_agent()
  │ 💭 "需要先讀檔案，然後產生 DATCOM"
  │
  ▼
┌─────────────────────────┐
│   SYSTEM                │  #3: ToolMessage
│   (執行路由)            │  "Successfully transferred"
└─────────────────────────┘
  │
  │ 控制權轉移
  │
  ▼
┌─────────────────────────┐
│   READ_FILE_AGENT       │  state.file_content = None
│   (讀取檔案)            │
└─────────────────────────┘
  │
  │ #4: AIMessage + Tool Call
  │ read_file("msg.txt")
  │ 📄 讀取 949 字元
  │
  │ 🔑 STATE UPDATE: state.file_content = "## PC-9 飛機..."
  │
  ▼
┌─────────────────────────┐
│   READ_FILE_AGENT       │  state.file_content = "## PC-9..."
│   (完成，準備返回)      │
└─────────────────────────┘
  │
  │ #5: AIMessage + Tool Call
  │ transfer_back_to_supervisor()
  │ "Transferring back to supervisor"
  │
  ▼
┌─────────────────────────┐
│   SYSTEM                │  #6: ToolMessage
│   (執行返回)            │  "Successfully transferred back"
└─────────────────────────┘
  │
  │ 控制權返回
  │
  ▼
┌─────────────────────────┐
│   SUPERVISOR            │  state.file_content = "## PC-9..." ✅
│   (再次分析)            │
└─────────────────────────┘
  │
  │ #7: AIMessage + Tool Call
  │ transfer_to_datcom_tool_agent()
  │ 💭 "檔案已讀取，現在產生 DATCOM"
  │ 💭 "state.file_content 有資料了"
  │
  ▼
┌─────────────────────────┐
│   SYSTEM                │  #8: ToolMessage
│   (執行第二次路由)      │  "Successfully transferred"
└─────────────────────────┘
  │
  │ 控制權轉移
  │
  ▼
┌─────────────────────────┐
│   DATCOM_TOOL_AGENT     │  state.file_content = "## PC-9..." ✅
│   (產生 DATCOM)         │  🔍 LLM 檢查 state.file_content
└─────────────────────────┘
  │
  │ #9: AIMessage + Tool Call
  │ write_datcom_file(
  │   nalpha=6,
  │   alschd="1.0,2.0,3.0,4.0,5.0,6.0",
  │   nmach=1,
  │   ... 57 parameters ...
  │ )
  │ 📝 產生 for005.dat
  │
  ▼
┌─────────────────────────┐
│   DATCOM_TOOL_AGENT     │
│   (完成，準備返回)      │
└─────────────────────────┘
  │
  │ #10: AIMessage + Tool Call
  │ transfer_back_to_supervisor()
  │ "Transferring back to supervisor"
  │
  ▼
┌─────────────────────────┐
│   SYSTEM                │  #11: ToolMessage
│   (執行第二次返回)      │  "Successfully transferred back"
└─────────────────────────┘
  │
  │ 控制權再次返回
  │
  ▼
┌─────────────────────────┐
│   SUPERVISOR            │
│   (確認完成)            │
└─────────────────────────┘
  │
  │ #12: AIMessage
  │ "✅ 已完成！for005.dat 已生成..."
  │
  ▼
👤 User
   (收到回應)
```

## 📊 State 變化時間線

```
Message #  │ Location           │ Action                 │ state.file_content
───────────┼────────────────────┼────────────────────────┼─────────────────────────
#1         │ User → System      │ 發送請求               │ None
#2         │ Supervisor         │ 決定路由到 read_file   │ None
#3         │ System             │ 執行 transfer          │ None
#4         │ read_file_agent    │ 讀取 msg.txt           │ None → "## PC-9..." ✅
#5         │ read_file_agent    │ 準備返回               │ "## PC-9..."
#6         │ System             │ 執行 transfer_back     │ "## PC-9..." ✅ 已設定
#7         │ Supervisor         │ 決定路由到 datcom      │ "## PC-9..." ✅ 可見
#8         │ System             │ 執行 transfer          │ "## PC-9..."
#9         │ datcom_tool_agent  │ 讀取 state 並產生檔案  │ "## PC-9..." ✅ LLM 讀取
#10        │ datcom_tool_agent  │ 準備返回               │ "## PC-9..."
#11        │ System             │ 執行 transfer_back     │ "## PC-9..."
#12        │ Supervisor         │ 回應使用者             │ "## PC-9..."
```

## 🔄 資料流向圖

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                           │
└─────────────────────────────────────────────────────────────────────┘

User Input
    │
    │ "請讀取 msg.txt 並產生 DATCOM 檔案"
    │
    ▼
┌───────────────────────────────────────────────────────────────────┐
│  SUPERVISOR (create_supervisor)                                   │
│  - state_schema=SupervisorState                                   │
│  - 維護共享 state                                                 │
└───────────────────────────────────────────────────────────────────┘
    │
    ├─── Route 1: read_file_agent ─────────────────┐
    │                                               │
    ▼                                               │
┌───────────────────────────────────────────┐      │
│  READ_FILE_AGENT                          │      │
│  - graph (from read_file_agent/agent.py)  │      │
│  - 使用 SupervisorState                   │      │
└───────────────────────────────────────────┘      │
    │                                               │
    │ read_file("msg.txt")                          │
    │      │                                        │
    │      ├─ 讀取檔案系統                          │
    │      │  /read_file_agent/data/msg.txt        │
    │      │                                        │
    │      ▼                                        │
    │  content = """                                │
    │  ## PC-9 飛機 DATCOM 配置                     │
    │  NALPHA=6                                     │
    │  ...                                          │
    │  """                                          │
    │                                               │
    │ return {"file_content": content}              │
    │      │                                        │
    │      ▼                                        │
    │  ┌─────────────────────────────────────┐     │
    │  │  SUPERVISOR STATE UPDATE            │     │
    │  │  state.file_content = content       │◄────┘
    │  └─────────────────────────────────────┘
    │
    │
    ├─── Route 2: datcom_tool_agent ──────────────┐
    │                                              │
    ▼                                              │
┌───────────────────────────────────────────┐     │
│  DATCOM_TOOL_AGENT                        │     │
│  - create_react_agent                     │     │
│  - state_schema=SupervisorState ✅        │     │
│  - prompt 提示檢查 state.file_content     │     │
└───────────────────────────────────────────┘     │
    │                                              │
    │ LLM 讀取 state.file_content                  │
    │      │                                       │
    │      ▼                                       │
    │  content = state.file_content  ◄─────────────┘
    │  = "## PC-9 飛機 DATCOM 配置..."
    │
    │ LLM 解析 content
    │      │
    │      ├─ 提取 nalpha=6
    │      ├─ 提取 alschd="1.0,2.0,3.0,4.0,5.0,6.0"
    │      ├─ 提取 nmach=1
    │      ├─ ... (共 57 個參數)
    │      │
    │      ▼
    │  write_datcom_file(
    │    nalpha=6,
    │    alschd="1.0,2.0,3.0,4.0,5.0,6.0",
    │    nmach=1,
    │    ...
    │  )
    │      │
    │      ▼
    │  ┌─────────────────────────────────────┐
    │  │  DATCOM GENERATOR                   │
    │  │  (run_generator.py)                 │
    │  │  - 格式化數字                       │
    │  │  - 產生 namelist 格式               │
    │  └─────────────────────────────────────┘
    │      │
    │      ▼
    │  寫入檔案系統
    │  /datcom_tool_agent/output/for005.dat
    │
    ▼
Response to User
"✅ 已完成！for005.dat 已生成..."
```

## 🔑 關鍵技術點圖解

### 1. State Schema 共享

```
┌──────────────────────────────────────────────────────────────┐
│  SupervisorState (supervisor_agent/utils/state.py)           │
│  ───────────────────────────────────────────────────────     │
│  class SupervisorState(MessagesState):                       │
│      file_content: Optional[str] = None  ← 共享欄位          │
│      next: Optional[str] = None                              │
│      remaining_steps: int = 25                               │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ 所有 agents 使用相同的 state schema
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  SUPERVISOR   │  │ READ_FILE     │  │ DATCOM_TOOL   │
│               │  │ AGENT         │  │ AGENT         │
│ state_schema= │  │ (uses         │  │ state_schema= │
│ Supervisor    │  │  supervisor   │  │ Supervisor    │
│ State         │  │  state)       │  │ State ✅      │
└───────────────┘  └───────────────┘  └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                     共享的 State 實例
                  state.file_content = "..."
```

### 2. Transfer 機制

```
Agent 完成任務後的返回流程：

┌─────────────────────────┐
│  Agent (e.g., read_file)│
│  完成任務                │
└─────────────────────────┘
         │
         │ 決定要返回 Supervisor
         │
         ▼
┌─────────────────────────┐
│  AIMessage              │
│  Content:               │
│  "Transferring back"    │
│                         │
│  Tool Call:             │
│  transfer_back_to_      │
│  supervisor()           │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SYSTEM                 │
│  執行 tool call         │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  ToolMessage            │
│  "Successfully          │
│   transferred back"     │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SUPERVISOR             │
│  控制權返回             │
│  繼續決策               │
└─────────────────────────┘
```

### 3. LLM 如何讀取 State

```
datcom_tool_agent 執行時：

┌─────────────────────────────────────────────────────────┐
│ LangGraph Context                                       │
│                                                         │
│ messages = [                                            │
│   HumanMessage("請讀取..."),                            │
│   ...                                                   │
│ ]                                                       │
│                                                         │
│ state = {                                               │
│   "messages": [...],                                    │
│   "file_content": "## PC-9 飛機..."  ← LLM 可以看到    │
│ }                                                       │
└─────────────────────────────────────────────────────────┘
                      │
                      │ 傳給 LLM
                      ▼
┌─────────────────────────────────────────────────────────┐
│ LLM (gpt-oss-20b)                                       │
│                                                         │
│ System Prompt:                                          │
│ "You are a DATCOM file generation specialist.          │
│  Check if there is file content in state.file_content" │
│                                                         │
│ LLM 思考過程:                                           │
│ 1. 檢查 prompt → "Check state.file_content"            │
│ 2. 查看 context → state.file_content = "## PC-9..."    │
│ 3. 有資料！使用這個來提取參數                          │
│ 4. 解析 "NALPHA=6" → nalpha=6                          │
│ 5. 解析 "ALSCHD=..." → alschd="1.0,2.0,..."            │
│ 6. ... 提取所有 57 個參數                               │
│ 7. 呼叫 write_datcom_file(nalpha=6, ...)               │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ Tool Execution                                          │
│ write_datcom_file(...57 parameters...)                 │
└─────────────────────────────────────────────────────────┘
```

## 📈 效能比較

### 當前架構 (12 Messages) ✅

```
優點:
✅ 功能完整 - 所有步驟都執行
✅ 狀態清楚 - 每個 transfer 都有記錄
✅ 可追蹤性 - 完整的 message history
✅ 錯誤處理 - 每步可獨立處理錯誤
✅ 靈活性高 - Supervisor 可智能路由

缺點:
⚠️ Messages 較多 (12 個)
⚠️ 執行時間 ~5-8 秒

適用: ✅ 生產環境
```

### 優化架構 (5 Messages with add_handoff_back_messages=False) ❌

```
優點:
✅ Messages 較少 (5 個)
✅ 執行更快

缺點:
❌ 多步驟工作流程中斷
❌ 只執行第一步 (read_file)
❌ 不執行第二步 (datcom)
❌ 無法產生 DATCOM 檔案

適用: ❌ 不適用（功能損壞）
```

### 專用 Agent (5-6 Messages) 🤔

```
優點:
✅ 更快
✅ 功能完整

缺點:
⚠️ 失去靈活性
⚠️ 只能處理固定流程
⚠️ 需要額外維護

適用: 🤔 特定場景（高頻固定流程）
```

## 🎯 總結

### 12 個 Messages = 2 次完整的 Agent 路由

```
User → Supervisor → read_file_agent → Supervisor → datcom_tool_agent → User
 1         2-6             7-11                      12
```

### State 傳遞的核心

```
read_file_agent 設定 → state.file_content → datcom_tool_agent 讀取
                              ↑
                        共享的 State
                     (SupervisorState)
```

### 關鍵設定檢查清單

- ✅ `supervisor` 設定 `state_schema=SupervisorState`
- ✅ `datcom_tool_agent` 設定 `state_schema=SupervisorState`
- ✅ `datcom_tool_agent` prompt 提示 "Check state.file_content"
- ✅ `read_file_agent` 返回 `{"file_content": content}`

---

**相關文件**:
- [WORKFLOW_EXPLAINED.md](WORKFLOW_EXPLAINED.md) - 詳細文字說明
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - 系統狀態
- [OPTIMIZATION_RESULTS.md](OPTIMIZATION_RESULTS.md) - 優化測試結果
