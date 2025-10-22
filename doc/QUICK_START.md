# Quick Start - Multi-Agent DATCOM Workflow

## ✅ 你現在可以做什麼

### 場景 1: 讀取檔案並產生 DATCOM

```python
from supervisor_agent.agent import app

result = app.invoke({
    "messages": [{
        "role": "user",
        "content": "請讀取 msg.txt 並產生 DATCOM 檔案"
    }]
})

# 結果:
# 1. read_file_agent 讀取 read_file_agent/data/msg.txt
# 2. 內容存入 state.file_content
# 3. datcom_tool_agent 讀取 state.file_content
# 4. LLM 解析並提取 57 個參數
# 5. 產生 datcom_tool_agent/output/for005.dat
```

### 場景 2: 直接產生（數據在訊息中）

```python
result = app.invoke({
    "messages": [{
        "role": "user",
        "content": """
        產生 DATCOM 檔案:
        - 攻角: 1.0, 2.0, 3.0, 4.0, 5.0, 6.0
        - 馬赫數: 0.5489
        - 高度: 10000 ft
        ...
        """
    }]
})

# 結果:
# 1. datcom_tool_agent 直接處理
# 2. LLM 從訊息中提取參數
# 3. 產生 output/for005.dat
```

## 🚀 快速測試

### 1. 準備測試數據

msg.txt 已經準備好在 `read_file_agent/data/msg.txt`，包含 PC-9 飛機配置。

### 2. 執行測試

```bash
cd /home/c1140921/Operation_Phoenix

# 測試完整工作流程（需要 LLM API）
python3 -m supervisor_agent.test_datcom_workflow

# 查看產生的檔案
cat datcom_tool_agent/output/for005.dat
```

### 3. 預期結果

```
CASEID PC-9
$FLTCON NALPHA=6.0,ALSCHD=1.0,2.0,3.0,4.0,5.0,6.0,NMACH=1.0,MACH=0.5489,NALT=1.0,ALT=10000.0,WT=5180.0$
$SYNTHS XCG=11.3907,ZCG=0.0,XW=11.107,ZW=-1.6339,ALIW=1.0,XH=29.1178,ZH=0.794,ALIH=-2.0,XV=26.4633,ZV=1.3615$
...
```

## 📁 檔案結構

```
Operation_Phoenix/
├── supervisor_agent/           # Supervisor 協調器
│   ├── agent.py               # 主程式（整合 3 個 agents）
│   ├── test_datcom_workflow.py  # 測試腳本 ← 執行這個
│   └── utils/state.py         # SupervisorState 定義
│
├── read_file_agent/           # 讀檔 Agent
│   ├── agent.py              # 讀取 msg.txt
│   └── data/msg.txt          # 測試數據 ← PC-9 配置
│
├── datcom_tool_agent/         # DATCOM 產生 Agent
│   ├── agent.py              # LLM 解析 + 寫檔 tool
│   ├── data_model.py         # Pydantic models (6 cards)
│   ├── run_generator.py      # 格式化引擎
│   └── output/               # 輸出目錄
│       └── for005.dat        # 產生的 DATCOM 檔案 ✅
│
└── doc/
    └── MULTI_AGENT_WORKFLOW.md  # 完整文檔
```

## 🔑 關鍵修改

### 1. datcom_tool_agent 現在可以讀取 state.file_content

**修改**: `datcom_tool_agent/agent.py`

```python
from supervisor_agent.utils.state import SupervisorState

datcom_tool_agent = create_react_agent(
    state_schema=SupervisorState,  # ✅ 加入這行
    prompt="""
    1. Check if there is file content in state.file_content
    2. If exists, use that as primary source
    ...
    """,
    ...
)
```

### 2. Supervisor 知道協調多步驟流程

**修改**: `supervisor_agent/agent.py`

```python
prompt="""
MULTI-STEP WORKFLOWS:
When user requests to "read file AND generate DATCOM":
1. First route to read_file_agent
2. Then route to datcom_tool_agent
   - Will automatically access state.file_content

Examples:
- "讀取 msg.txt 並產生 DATCOM 檔案" → read_file_agent THEN datcom_tool_agent
"""
```

## 🎯 工作流程

```
用戶: "讀取 msg.txt 並產生 DATCOM 檔案"
    ↓
Supervisor 分析請求
    ↓
路由到 read_file_agent
    ↓
讀取 msg.txt → state.file_content ✅
    ↓
Supervisor 繼續
    ↓
路由到 datcom_tool_agent
    ↓
讀取 state.file_content ✅
    ↓
LLM 解析 → 提取 57 個參數
    ↓
呼叫 write_datcom_file tool
    ↓
Pydantic 驗證 ✅
    ↓
DatcomGenerator 格式化
    ↓
output/for005.dat ✅
```

## 📊 支援的輸入格式

datcom_tool_agent 可以解析多種格式：

### 格式 1: Key=Value (目前 msg.txt 使用)

```
NALPHA=6
ALSCHD= 1.0,2.0,3.0,4.0,5.0,6.0
NMACH= 1
MACH= 0.5489
...
```

### 格式 2: DATCOM 原始格式

```
$FLTCON NALPHA=6.0,
        ALSCHD= 1.0,2.0,3.0,4.0,5.0,6.0,
        NMACH= 1.0,
        MACH= 0.5489,
...
$
```

### 格式 3: 自然語言描述

```
PC-9 飛機配置：
- 攻角從 1 度到 6 度，共 6 個點
- 馬赫數為 0.5489（1 組）
- 高度 10000 英尺（1 組）
...
```

LLM 會自動識別並提取參數！

## 🐛 常見問題

### Q: LLM API 連線失敗？

**A**: 檢查 `.env` 檔案：
```bash
cat read_file_agent/.env
# OPENAI_API_BASE_URL=http://172.16.120.65:8089/v1
# 確認這個 URL 是否可訪問
```

### Q: msg.txt 不存在？

**A**: 檔案已經在 `read_file_agent/data/msg.txt`，如果需要修改：
```bash
nano read_file_agent/data/msg.txt
```

### Q: 輸出檔案在哪裡？

**A**: `datcom_tool_agent/output/for005.dat`

### Q: 如何修改輸出格式？

**A**: 編輯 `datcom_tool_agent/run_generator.py` 中的 `_format_single_number()` 函數

### Q: 如何添加新的 DATCOM 卡片？

**A**:
1. 在 `data_model.py` 添加 Pydantic model
2. 在 `write_datcom_file` tool 添加參數
3. 在 `DatcomGenerator` 添加格式化邏輯

## 📚 更多資訊

- **完整文檔**: [doc/MULTI_AGENT_WORKFLOW.md](doc/MULTI_AGENT_WORKFLOW.md)
- **DATCOM Agent**: [datcom_tool_agent/README.md](datcom_tool_agent/README.md)
- **設計文檔**: [datcom_tool_agent/DESIGN.md](datcom_tool_agent/DESIGN.md)
- **Supervisor**: [supervisor_agent/README.md](supervisor_agent/README.md)

## 🎉 總結

你現在有一個完整的多 Agent 系統，可以：

✅ **讀取檔案** (read_file_agent)
✅ **解析配置** (datcom_tool_agent + LLM)
✅ **產生 DATCOM 檔案** (write_datcom_file tool)
✅ **智能路由** (supervisor)
✅ **State 共享** (SupervisorState.file_content)

**遵循原則**:
- ✅ AGENT.md (Deployment-First, Prebuilt Components)
- ✅ GEMINI.md (Dumbest Clear Approach, No Special Cases)

**可用於生產環境！** 🚀
