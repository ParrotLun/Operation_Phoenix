# Operation Phoenix - 系統架構文件

**文件版本**: 1.0
**最後更新**: 2025-10-22
**專案狀態**: ✅ 生產環境就緒 (Production Ready)

---

## 📋 目錄

1. [系統概述](#系統概述)
2. [核心架構](#核心架構)
3. [技術堆疊](#技術堆疊)
4. [模組說明](#模組說明)
5. [資料流程](#資料流程)
6. [部署架構](#部署架構)
7. [設計原則](#設計原則)
8. [測試策略](#測試策略)
9. [效能指標](#效能指標)
10. [已知限制與未來規劃](#已知限制與未來規劃)

---

## 系統概述

### 專案簡介

**Operation Phoenix** 是一個基於 LangGraph Supervisor 模式的多代理人（Multi-Agent）系統，專門用於：
- 讀取航空器配置檔案
- 使用 LLM 智能解析資料
- 自動生成 DATCOM（Digital Aerodynamic Data Compatibility）氣動力輸入檔案

### 核心功能

| 功能 | 說明 | 狀態 |
|------|------|------|
| **檔案讀取** | 讀取 msg.txt 航空器配置檔案 | ✅ 完成 |
| **智能解析** | 使用 LLM 解析多種格式的輸入資料 | ✅ 完成 |
| **DATCOM 生成** | 產生符合規範的 for005.dat 檔案 | ✅ 完成 |
| **多步驟協調** | Supervisor 協調多個 Agent 協同工作 | ✅ 完成 |
| **參數驗證** | Pydantic 模型驗證 57+ 個參數 | ✅ 完成 |
| **工具操作** | 時間查詢、計算、字串處理等 | ✅ 完成 |

### 系統特色

- ✅ **智能路由**: Supervisor 使用 LLM 自動判斷工作流程
- ✅ **狀態共享**: SupervisorState 在 agents 間共享資料
- ✅ **型別安全**: Pydantic v2 進行嚴格的參數驗證
- ✅ **彈性輸入**: 支援多種格式（Key=Value、DATCOM 原生、自然語言）
- ✅ **可擴展性**: 基於 prebuilt components，易於新增功能

---

## 核心架構

### 系統拓樸圖

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
│              "讀取 msg.txt 並產生 DATCOM 檔案"                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                              │
│  - LLM-based routing (使用 create_supervisor)                   │
│  - 分析用戶意圖                                                   │
│  - 管理 SupervisorState                                          │
│  - 協調多步驟工作流程                                             │
└───────┬─────────────────┬─────────────────┬─────────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐
│read_file_    │  │ tool_agent   │  │ datcom_tool_agent        │
│agent         │  │              │  │                          │
│              │  │              │  │ - LLM 解析               │
│讀取檔案       │  │時間/計算/    │  │ - 57個參數               │
│存入 state    │  │字串工具       │  │ - Pydantic 驗證          │
└──────┬───────┘  └──────┬───────┘  └──────┬───────────────────┘
       │                 │                 │
       │ file_content    │                 │ write_datcom_file
       │                 │                 │
       ▼                 ▼                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                     SupervisorState                               │
│  - messages: List[Message]                                        │
│  - file_content: Optional[str]  ← 共享資料區                      │
│  - next: Optional[str]                                            │
│  - remaining_steps: int                                           │
└──────────────────────────────────────────────────────────────────┘
```

### 架構層次

```
┌─────────────────────────────────────────┐
│       Application Layer (應用層)         │
│   - test_datcom_workflow.py              │
│   - interactive_test.py                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Coordination Layer (協調層)           │
│   - Supervisor Agent                     │
│   - SupervisorState                      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Agent Layer (代理層)                │
│   - read_file_agent                      │
│   - tool_agent                           │
│   - datcom_tool_agent                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Tool Layer (工具層)                 │
│   - read_msg_file()                      │
│   - write_datcom_file()                  │
│   - get_current_time()                   │
│   - calculate()                          │
│   - reverse_string()                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Data Layer (資料層)                 │
│   - Pydantic Models (FLTCON, SYNTHS...)  │
│   - DatcomGenerator                      │
│   - msg.txt (輸入)                       │
│   - for005.dat (輸出)                    │
└─────────────────────────────────────────┘
```

---

## 技術堆疊

### 核心框架

| 技術 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 主要開發語言 |
| **LangGraph** | ≥0.3.0 | Multi-agent 工作流程引擎 |
| **LangChain** | ≥0.3.0 | LLM 整合框架 |
| **langgraph-supervisor** | Latest | Supervisor pattern 預建組件 |
| **Pydantic** | ≥2.0 | 資料驗證與型別安全 |
| **python-dotenv** | Latest | 環境變數管理 |

### LLM 配置

```python
# 自訂 OpenAI 相容端點
OPENAI_API_BASE_URL = "http://172.16.120.65:8089/v1"
DEFAULT_LLM_MODEL = "openai/gpt-oss-20b"
```

**特殊處理**:
- 自訂 `CustomChatOpenAI` 類別移除 `parallel_tool_calls` 參數
- 適配非標準 OpenAI 端點

### 開發工具

- **pytest**: 單元測試與整合測試
- **Git**: 版本控制
- **LangGraph CLI**: 部署工具

---

## 模組說明

### 1. Supervisor Agent

**路徑**: `supervisor_agent/`

**職責**: 中央協調器，分析用戶請求並路由到適當的 agent

**核心檔案**:
```
supervisor_agent/
├── agent.py                    # 主要 supervisor 實作
├── utils/
│   └── state.py               # SupervisorState 定義
├── agents/
│   └── tool_agent.py          # 工具型 agent
├── test/
│   └── interactive_test.py    # 互動式測試工具
└── test_datcom_workflow.py    # 自動化測試
```

**關鍵實作**:

```python
# supervisor_agent/agent.py
supervisor = create_supervisor(
    agents=[read_file_agent, tool_agent, datcom_tool_agent],
    model=supervisor_model,
    state_schema=SupervisorState,
    parallel_tool_calls=False,
    prompt="""You are a supervisor managing three specialized agents:

    1. read_file_agent: File reading operations
    2. tool_agent: Utility tasks (time, calculations, strings)
    3. datcom_tool_agent: DATCOM file generation

    MULTI-STEP WORKFLOWS:
    - "讀取 msg.txt 並產生 DATCOM 檔案"
      → read_file_agent → datcom_tool_agent → FINISH
    """
)

app = supervisor.compile()
```

**SupervisorState**:

```python
# supervisor_agent/utils/state.py
class SupervisorState(MessagesState):
    file_content: Optional[str] = None  # Agent 間共享的檔案內容
    next: Optional[str] = None
    remaining_steps: int = 25
```

---

### 2. Read File Agent

**路徑**: `read_file_agent/`

**職責**: 讀取 `data/msg.txt` 並將內容存入 `state.file_content`

**核心檔案**:
```
read_file_agent/
├── agent.py              # 純讀檔 StateGraph
├── data/
│   └── msg.txt          # PC-9 航空器配置資料
├── utils/
│   └── state.py         # AgentState 定義
└── .env                 # 環境變數配置
```

**實作特點**:
- ✅ 不使用 LLM（純檔案 I/O）
- ✅ 直接回傳檔案內容到 state
- ✅ 可作為獨立 app 或 supervisor 的 subgraph

**核心邏輯**:

```python
def read_file_node(state: AgentState) -> dict:
    file_path = os.path.join(current_dir, 'data', 'msg.txt')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        "messages": [AIMessage(content=f"已讀取內容: {content}")],
        "file_content": content  # ← 存入 state
    }
```

---

### 3. DATCOM Tool Agent

**路徑**: `datcom_tool_agent/`

**職責**: 使用 LLM 解析航空器配置資料，生成 DATCOM 輸入檔案

**核心檔案**:
```
datcom_tool_agent/
├── agent.py              # LLM agent + write_datcom_file tool
├── data_model.py         # Pydantic models (6 cards)
├── run_generator.py      # DatcomGenerator 格式化引擎
├── output/
│   └── for005.dat       # 輸出的 DATCOM 檔案
└── DESIGN.md            # 設計文檔
```

#### 3.1 資料模型 (Pydantic)

**6 個主要卡片**:

| Card | 模型 | 參數數量 | 說明 |
|------|------|----------|------|
| Flight Conditions | `FLTCON` | 7 | 攻角、馬赫數、高度、重量 |
| Synthesis | `SYNTHS` | 10 | 重心、機翼/尾翼位置與安裝角 |
| Body Geometry | `BODY` | 7 | 機身幾何形狀 (最多20站位) |
| Wing Planform | `WGPLNF` | 10 | 主翼平面形狀 |
| H-Tail Planform | `HTPLNF` | 10 | 水平尾翼平面形狀 |
| V-Tail Planform | `VTPLNF` | 8 | 垂直尾翼平面形狀 |

**驗證規則範例**:

```python
class FLTCON(BaseModel):
    NALPHA: int = Field(..., le=20)  # 最多20個攻角
    ALSCHD: List[float]

    @field_validator('ALSCHD')
    @classmethod
    def check_alpha_count(cls, v, info):
        if len(v) != info.data['NALPHA']:
            raise ValueError(f"攻角數量 ({len(v)}) 必須等於 NALPHA")
        return v
```

#### 3.2 write_datcom_file Tool

**函數簽章** (57 個參數):

```python
@tool
def write_datcom_file(
    # Flight Conditions (7)
    nalpha: int, alschd: str, nmach: int, mach: str,
    nalt: int, alt: str, wt: float,

    # Synthesis (10)
    xcg: float, zcg: float, xw: float, zw: float, aliw: float,
    xh: float, zh: float, alih: float, xv: float, zv: float,

    # Body (7)
    nx: int, x_coords: str, r_coords: str, zu_coords: str,
    zl_coords: str, itype: int, method: int,

    # Wing (10)
    wing_naca: str, wing_chrdtp: float, wing_sspn: float,
    wing_sspne: float, wing_chrdr: float, wing_savsi: float,
    wing_chstat: float, wing_twista: float, wing_dhdadi: float,
    wing_type: int,

    # Horizontal Tail (10)
    htail_naca: str, htail_chrdtp: float, ...,

    # Vertical Tail (8)
    vtail_naca: str, vtail_chrdtp: float, ...,

    # Config
    case_id: str = "PC-9"
) -> str:
    # 1. 解析逗號分隔字串為列表
    # 2. 建立 Pydantic models
    # 3. 驗證資料
    # 4. 呼叫 DatcomGenerator
    # 5. 寫入 output/for005.dat
```

#### 3.3 DatcomGenerator

**格式化規則**:

```python
def _format_single_number(self, value: float) -> str:
    # 整數 → 1位小數: 6 → "6.0"
    if isinstance(value, int) or value == int(value):
        return f"{int(value)}.0"

    # 浮點數 → 最多4位小數，移除尾隨0
    # 0.5489 → "0.5489"
    # 1.6000 → "1.6"
    formatted = f"{value:.4f}".rstrip('0').rstrip('.')
    return formatted if '.' in formatted else f"{formatted}.0"
```

**輸出範例**:

```fortran
CASEID PC-9
$FLTCON NALPHA=6.0,ALSCHD=1.0,2.0,3.0,4.0,5.0,6.0,NMACH=1.0,MACH=0.5489,NALT=1.0,ALT=10000.0,WT=5180.0$
$SYNTHS XCG=11.3907,ZCG=0.0,XW=11.107,ZW=-1.6339,ALIW=1.0,XH=29.1178,ZH=0.794,ALIH=-2.0,XV=26.4633,ZV=1.3615$
$BODY NX=13.0,X=0.0,3.25,6.5,9.75,13.0,16.25,19.5,22.75,26.0,27.5625,29.125,30.6875,32.25,
     R=0.0,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.31,0.98,0.6533,0.3267,
     ZU=0.0,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.6339,1.31,0.98,0.6533,0.3267,
     ZL=0.0,-1.6339,-1.6339,-1.6339,-1.6339,-1.6339,-1.6339,-1.6339,-1.6339,-1.31,-0.98,-0.6533,-0.3267,
     ITYPE=1.0,METHOD=1.0$
$WGPLNF NACA-W-6-63-415,CHRDTP=2.6,SSPN=16.63,SSPNE=14.96,CHRDR=5.2,SAVSI=3.5,CHSTAT=0.0,TWISTA=-2.4,DHDADI=7.0,TYPE=1.0$
$HTPLNF NACA-H-4-0012,CHRDTP=2.85,SSPN=5.71,SSPNE=5.71,CHRDR=3.8,SAVSI=6.0,CHSTAT=0.0,TWISTA=0.0,DHDADI=0.0,TYPE=1.0$
$VTPLNF NACA-V-4-0008,CHRDTP=1.9,SSPN=3.25,SSPNE=3.25,CHRDR=4.1,SAVSI=25.0,CHSTAT=0.0,TYPE=1.0$
```

---

### 4. Tool Agent

**路徑**: `supervisor_agent/agents/tool_agent.py`

**職責**: 提供通用工具功能

**可用工具**:

```python
@tool
def get_current_time() -> str:
    """取得當前時間"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """安全計算數學表達式"""
    return str(eval(expression, {"__builtins__": {}}, {}))

@tool
def reverse_string(text: str) -> str:
    """反轉字串"""
    return text[::-1]
```

---

## 資料流程

### 完整工作流程圖

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. User Input                                                     │
│    "讀取 msg.txt 並產生 DATCOM 檔案"                               │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. Supervisor Analysis                                            │
│    - LLM 解析請求                                                 │
│    - 識別關鍵字: "讀取", "產生 DATCOM"                             │
│    - 判斷: 多步驟工作流程                                          │
│    - 決策: read_file_agent → datcom_tool_agent                   │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. Route to read_file_agent                                       │
│    Input:  state.messages = [HumanMessage("讀取...")]            │
│    Process: read_file_node()                                      │
│             - 開啟 data/msg.txt                                   │
│             - 讀取內容 (1234 bytes)                               │
│    Output: state.file_content = "## PC-9 飛機 DATCOM 配置\n..."  │
│           state.messages += [AIMessage("已讀取...")]              │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. Supervisor Continues                                           │
│    - 檢查 state.file_content: ✅ 存在                             │
│    - 判斷: 需要繼續執行 datcom_tool_agent                         │
│    - 決策: 不要 FINISH，路由到 datcom_tool_agent                  │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. Route to datcom_tool_agent                                     │
│    Input:  state.file_content (from step 3)                       │
│            state.messages (conversation history)                  │
│    Process:                                                        │
│      5.1 LLM 分析 file_content                                    │
│      5.2 解析航空器配置參數                                        │
│          - NALPHA=6                                               │
│          - ALSCHD=1.0,2.0,3.0,4.0,5.0,6.0                        │
│          - WING_NACA=6-63-415                                     │
│          - ... (共57個參數)                                       │
│      5.3 呼叫 write_datcom_file(nalpha=6, alschd="1.0,2.0,..."...) │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 6. write_datcom_file Tool Execution                               │
│    6.1 解析逗號分隔字串                                            │
│        "1.0,2.0,3.0" → [1.0, 2.0, 3.0]                           │
│    6.2 建立 Pydantic Models                                       │
│        flight_conditions = FLTCON(NALPHA=6, ALSCHD=[1.0,...])    │
│        synthesis = SYNTHS(XCG=11.3907, ...)                      │
│        body = BODY(NX=13, X=[0.0, 3.25,...])                     │
│        wing = WGPLNF(NACA_W="6-63-415", ...)                     │
│        htail = HTPLNF(...)                                        │
│        vtail = VTPLNF(...)                                        │
│    6.3 Pydantic 驗證                                              │
│        ✅ len(ALSCHD) == NALPHA                                   │
│        ✅ NALPHA ≤ 20                                             │
│        ✅ 所有必填欄位存在                                         │
│    6.4 建立完整輸入                                                │
│        datcom_input = DatcomInput(                                │
│            flight_conditions=...,                                 │
│            synthesis=..., body=..., wing=..., htail=..., vtail=...│
│        )                                                          │
│    6.5 呼叫 DatcomGenerator                                       │
│        generator.generate_file(datcom_input, "PC-9", output_path)│
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 7. DatcomGenerator Formatting                                     │
│    7.1 格式化數字                                                 │
│        6 → "6.0"                                                  │
│        0.5489 → "0.5489"                                          │
│        1.6000 → "1.6"                                             │
│    7.2 產生 Namelist 格式                                         │
│        $FLTCON NALPHA=6.0,ALSCHD=1.0,2.0,...$                    │
│    7.3 寫入檔案                                                   │
│        output/for005.dat                                          │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 8. Response to Supervisor                                         │
│    Tool Result:                                                   │
│    "✅ Successfully wrote DATCOM file to: .../output/for005.dat" │
│                                                                   │
│    state.messages += [AIMessage(content="✅ Successfully...")]   │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────────┐
│ 9. Supervisor Finishes                                            │
│    - 檢查所有任務完成                                              │
│    - 決策: FINISH                                                 │
│    - 回傳最終結果給用戶                                            │
└──────────────────────────────────────────────────────────────────┘
```

### 資料結構傳遞

**SupervisorState 演進**:

```python
# Initial State
{
    "messages": [
        HumanMessage(content="讀取 msg.txt 並產生 DATCOM 檔案")
    ],
    "file_content": None,
    "next": None,
    "remaining_steps": 25
}

# After read_file_agent
{
    "messages": [
        HumanMessage(content="讀取 msg.txt 並產生 DATCOM 檔案"),
        AIMessage(content="已讀取 msg.txt...", name="read_file_agent")
    ],
    "file_content": "## PC-9 飛機 DATCOM 配置\nNALPHA=6\n...",  # ← 新增
    "next": None,
    "remaining_steps": 24
}

# After datcom_tool_agent
{
    "messages": [
        HumanMessage(content="讀取 msg.txt 並產生 DATCOM 檔案"),
        AIMessage(content="已讀取 msg.txt...", name="read_file_agent"),
        AIMessage(content="✅ Successfully wrote...", name="datcom_tool_agent")
    ],
    "file_content": "## PC-9 飛機 DATCOM 配置\nNALPHA=6\n...",
    "next": "__end__",  # ← Supervisor 決定結束
    "remaining_steps": 23
}
```

---

## 部署架構

### 檔案系統佈局

```
/home/c1140921/Operation_Phoenix/
├── .git/                           # Git 版本控制
├── .gitignore
├── .claude/                        # Claude Code 配置
│   └── settings.local.json
│
├── doc/                            # 文檔目錄
│   ├── AGENT.md                   # LangGraph 開發原則
│   ├── GEMINI.md                  # Linus Torvalds 風格指南
│   ├── MULTI_AGENT_WORKFLOW.md    # 多 Agent 工作流程文檔
│   └── OPTIMIZATION_RESULTS.md    # 效能優化結果
│
├── supervisor_agent/              # 中央協調器
│   ├── agent.py                   # 主程式 (exports: app)
│   ├── langgraph.json            # LangGraph 部署配置
│   ├── requirements.txt
│   ├── utils/
│   │   └── state.py              # SupervisorState
│   ├── agents/
│   │   └── tool_agent.py         # 工具型 agent
│   ├── test/
│   │   └── interactive_test.py   # 互動式測試
│   ├── test_supervisor.py
│   ├── test_state_propagation.py
│   └── test_datcom_workflow.py   # ← 主要測試腳本
│
├── read_file_agent/               # 檔案讀取 Agent
│   ├── agent.py                   # 讀檔 StateGraph
│   ├── .env                       # 環境變數 (LLM API 配置)
│   ├── requirements.txt
│   ├── data/
│   │   └── msg.txt               # PC-9 配置資料
│   └── utils/
│       ├── state.py              # AgentState
│       └── tools.py
│
├── datcom_tool_agent/             # DATCOM 生成 Agent
│   ├── agent.py                   # LLM agent + tool
│   ├── data_model.py             # Pydantic models (6 cards)
│   ├── run_generator.py          # DatcomGenerator
│   ├── requirements.txt
│   ├── output/
│   │   └── for005.dat            # ← 產生的 DATCOM 檔案
│   ├── test_agent.py
│   ├── DESIGN.md
│   └── README.md
│
├── QUICK_START.md                 # 快速開始指南
├── SYSTEM_STATUS.md               # 系統狀態文檔
├── VERIFICATION_CHECKLIST.md      # 驗證檢查清單
└── SYSTEM_ARCHITECTURE.md         # ← 本文檔
```

### 環境配置

**`.env` 檔案** (位於 `read_file_agent/.env`):

```bash
# LLM API Configuration
OPENAI_API_BASE_URL=http://172.16.120.65:8089/v1
OPENAI_API_KEY=your-api-key-here
DEFAULT_LLM_MODEL=openai/gpt-oss-20b
```

### 依賴管理

**總體依賴**:

```txt
# Core LangGraph
langgraph>=0.3.0
langgraph-supervisor
langchain>=0.3.0
langchain-openai
langchain-core

# Data Validation
pydantic>=2.0.0

# Utilities
python-dotenv

# Testing
pytest>=7.0.0
```

### 部署到 LangGraph Cloud

```bash
# 進入 supervisor_agent 目錄
cd /home/c1140921/Operation_Phoenix/supervisor_agent

# 檢查 langgraph.json 配置
cat langgraph.json

# 部署
langgraph up
```

**langgraph.json**:

```json
{
  "dependencies": [".", "../read_file_agent", "../datcom_tool_agent"],
  "graphs": {
    "agent": "./agent.py:app"
  },
  "env": "../read_file_agent/.env"
}
```

---

## 設計原則

此系統嚴格遵循兩份核心設計文檔：

### AGENT.md - LangGraph 最佳實踐

| 原則 | 實作 | 說明 |
|------|------|------|
| **Deployment-First** | ✅ | 所有 agents 導出為 `app = graph.compile()` |
| **Prebuilt Components** | ✅ | 使用 `create_react_agent`, `create_supervisor` |
| **Simple State** | ✅ | 基於 `MessagesState`，僅添加必要欄位 |
| **Model Priority** | ✅ | 使用自訂 OpenAI 端點，彈性配置 |
| **No Checkpointer (預設)** | ✅ | Stateless 設計，除非明確需要 |

### GEMINI.md - Linus Torvalds 哲學

| 原則 | 實作 | 說明 |
|------|------|------|
| **Dumbest Clear Approach** | ✅ | 簡單明確的工具參數，不做"聰明"的隱式處理 |
| **No Special Cases** | ✅ | 統一的數字格式化規則，無例外 |
| **Zero Breakage** | ✅ | 獨立模組，可選擇性整合 |
| **Solve Root Cause** | ✅ | Pydantic 驗證解決參數錯誤根本問題 |
| **Explicit > Implicit** | ✅ | `state.file_content` 明確傳遞資料 |

### 核心設計決策

#### 1. 為何使用 `state.file_content`？

**選擇**: 明確的狀態欄位
**替代方案**: 僅透過 messages 傳遞

**理由**:
- ✅ 型別安全 (`Optional[str]`)
- ✅ 明確的資料契約
- ✅ 易於測試與除錯
- ✅ 避免從 messages 中搜尋解析內容

#### 2. 為何 Tool 有 57 個參數？

**選擇**: 明確的參數列表
**替代方案**: 接收單一 dict 或 JSON 字串

**理由**:
- ✅ IDE 自動補全
- ✅ 清晰的 API 介面
- ✅ 精準的錯誤訊息
- ✅ 符合 Pydantic "explicit over implicit" 哲學

#### 3. 為何 LLM 負責解析？

**選擇**: LLM + Tool 分離職責
**替代方案**: Tool 內部直接解析文字

**理由**:
- ✅ LLM 擅長理解多種格式（自然語言、結構化、半結構化）
- ✅ Tool 保持簡單，專注於驗證與寫檔
- ✅ Tool 可被其他程式直接呼叫（不依賴 LLM）
- ✅ 易於單元測試

---

## 測試策略

### 測試層級

```
┌───────────────────────────────────────┐
│  End-to-End Tests                     │
│  - test_datcom_workflow.py            │
│  - interactive_test.py                │
└───────────────┬───────────────────────┘
                │
┌───────────────▼───────────────────────┐
│  Integration Tests                    │
│  - test_supervisor.py                 │
│  - test_state_propagation.py          │
└───────────────┬───────────────────────┘
                │
┌───────────────▼───────────────────────┐
│  Unit Tests                           │
│  - test_agent.py (datcom_tool_agent)  │
│  - Pydantic validation tests          │
│  - DatcomGenerator tests              │
└───────────────────────────────────────┘
```

### 主要測試腳本

#### 1. test_datcom_workflow.py

**測試場景**:
- ✅ 多步驟工作流程 (讀檔 → 產生 DATCOM)
- ✅ 直接產生 (資料在 message 中)
- ✅ state.file_content 正確傳遞
- ✅ 輸出檔案驗證

**執行**:

```bash
cd /home/c1140921/Operation_Phoenix
python3 -m supervisor_agent.test_datcom_workflow
```

**預期輸出**:

```
╔══════════════════════════════════════════════════════════════╗
║        SUPERVISOR MULTI-AGENT DATCOM WORKFLOW TEST           ║
╚══════════════════════════════════════════════════════════════╝

✅ Test completed!
🎉 SUCCESS! DATCOM file created at: .../output/for005.dat
```

#### 2. interactive_test.py

**特點**:
- 互動式 CLI 測試工具
- Verbose 模式顯示詳細診斷
- 自動檢測 DATCOM 檔案生成

**執行**:

```bash
cd /home/c1140921/Operation_Phoenix
python3 -m supervisor_agent.test.interactive_test --verbose
```

### 測試資料

**msg.txt** (PC-9 航空器配置):

```
## PC-9 飛機 DATCOM 配置

## 飛行條件
NALPHA=6
ALSCHD= 1.0,2.0,3.0,4.0,5.0,6.0
NMACH= 1
MACH= 0.5489
NALT= 1
ALT= 10000
WT= 5180

## 重心與位置
XCG= 11.3907
ZCG= 0.0
XW= 11.107
ZW= -1.6339
ALIW= 1.0
...
```

### 驗證檢查清單

參考 [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md):

- ✅ 所有 agents 正確編譯
- ✅ Supervisor 路由決策正確
- ✅ State 在 agents 間正確傳遞
- ✅ Pydantic 驗證生效
- ✅ 輸出檔案格式正確
- ✅ LLM API 連線穩定

---

## 效能指標

### 執行時間

| 場景 | Messages | Transfers | 時間 | 狀態 |
|------|----------|-----------|------|------|
| **多步驟工作流程** | 12 | 2 | 5-8秒 | ✅ 可接受 |
| **直接產生** | 6 | 1 | 3-5秒 | ✅ 良好 |
| **單純讀檔** | 4 | 1 | 1-2秒 | ✅ 優秀 |

**註**: 時間取決於 LLM API 回應速度

### 訊息數量分析

**多步驟工作流程** ("讀取 msg.txt 並產生 DATCOM 檔案"):

```
訊息流:
1. HumanMessage (用戶請求)
2. Supervisor → read_file_agent (路由決策)
3. read_file_agent → Supervisor (完成讀檔)
4. Supervisor → datcom_tool_agent (繼續路由)
5. datcom_tool_agent → Tool (呼叫 write_datcom_file)
6. Tool → datcom_tool_agent (Tool 結果)
7. datcom_tool_agent → Supervisor (完成生成)
8. Supervisor → User (最終回應)
...
總計: 12 messages
```

### 優化歷史

**曾嘗試的優化** (已回退):

```python
# ❌ 這些優化會破壞多步驟工作流程
supervisor = create_supervisor(
    agents=[...],
    add_handoff_back_messages=False,  # ← 導致流程中斷
    output_mode='last_message'        # ← Supervisor 看不到完整歷史
)
```

**結果**: 從 12 messages 減少到 5 messages，但功能**損壞** ❌

**決策**: **正確性 > 效能**，維持預設配置

詳見 [doc/OPTIMIZATION_RESULTS.md](doc/OPTIMIZATION_RESULTS.md)

### 未來優化方向

如果 12 messages 成為瓶頸:

1. **專用複合 Agent** (~5-6 messages)
   - 創建 `read_and_generate_datcom_agent`
   - 適用於固定的高頻工作流程

2. **手動 StateGraph** (~4 messages)
   - 捨棄 Supervisor 彈性
   - 最大效能，但維護成本高

3. **更強的 LLM 模型**
   - 可能支援優化參數
   - 需測試，成本更高

---

## 已知限制與未來規劃

### 當前限制

| 限制 | 影響 | 緩解措施 |
|------|------|----------|
| **固定輸出路徑** | 總是寫入 `output/for005.dat` | 可接受，未來可參數化 |
| **LLM 依賴** | 需要外部 LLM API | 設計時已考慮，支援多種格式降低失敗率 |
| **單一檔案輸入** | 僅支援 `msg.txt` | 架構支援擴展，易於新增多檔案支援 |
| **12 messages/workflow** | 多步驟流程較多訊息交換 | 已驗證可接受，優先保證正確性 |

### 未來增強功能

#### 短期 (1-2 月)

- [ ] **自訂輸出路徑**: 允許用戶指定 output file 位置
- [ ] **批次處理**: 一次處理多個航空器配置
- [ ] **YAML/JSON 輸入**: 支援更多結構化格式
- [ ] **驗證報告**: 生成詳細的參數驗證報告

#### 中期 (3-6 月)

- [ ] **DATCOM 輸出解析**: 解析 for006.dat 輸出檔案
- [ ] **視覺化工具**: 航空器幾何視覺化
- [ ] **模板系統**: 常用航空器配置模板
- [ ] **Web UI**: 提供 Web 介面

#### 長期 (6+ 月)

- [ ] **Cloud Deployment**: 部署到 LangGraph Cloud
- [ ] **Multi-tenancy**: 支援多用戶
- [ ] **資料庫整合**: 持久化配置與結果
- [ ] **API Gateway**: REST/GraphQL API

### 擴展性設計

**新增 Agent 範例**:

```python
# 1. 創建新 agent
from langgraph.prebuilt import create_react_agent

validation_agent = create_react_agent(
    model=model,
    tools=[validate_aircraft_config],
    name="validation_agent"
)

# 2. 加入 Supervisor
supervisor = create_supervisor(
    agents=[
        read_file_agent,
        tool_agent,
        datcom_tool_agent,
        validation_agent  # ← 新增
    ],
    prompt="""... (更新 prompt 說明新 agent)"""
)
```

**新增 Tool 範例**:

```python
# 在對應的 agent 中添加
@tool
def parse_datcom_output(output_file: str) -> dict:
    """解析 DATCOM 輸出檔案 (for006.dat)"""
    # 實作...
    return results
```

---

## 附錄

### A. 相關文檔索引

| 文檔 | 路徑 | 說明 |
|------|------|------|
| **快速開始** | [QUICK_START.md](QUICK_START.md) | 快速上手指南 |
| **系統狀態** | [SYSTEM_STATUS.md](SYSTEM_STATUS.md) | 當前系統狀態與最新變更 |
| **驗證清單** | [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) | 系統驗證步驟 |
| **多 Agent 工作流程** | [doc/MULTI_AGENT_WORKFLOW.md](doc/MULTI_AGENT_WORKFLOW.md) | 詳細工作流程說明 |
| **優化結果** | [doc/OPTIMIZATION_RESULTS.md](doc/OPTIMIZATION_RESULTS.md) | 效能優化實驗結果 |
| **開發原則** | [doc/AGENT.md](doc/AGENT.md) | LangGraph 開發指南 |
| **風格指南** | [doc/GEMINI.md](doc/GEMINI.md) | Linus 風格編碼哲學 |
| **DATCOM Agent** | [datcom_tool_agent/README.md](datcom_tool_agent/README.md) | DATCOM Agent 使用說明 |
| **設計文檔** | [datcom_tool_agent/DESIGN.md](datcom_tool_agent/DESIGN.md) | DATCOM Agent 設計決策 |
| **Supervisor** | [supervisor_agent/README.md](supervisor_agent/README.md) | Supervisor 架構說明 |

### B. 常見問題 (FAQ)

#### Q1: 為什麼選擇 LangGraph 而非其他框架？

**A**:
- ✅ 原生支援 Multi-agent 架構
- ✅ Prebuilt components 減少樣板程式碼
- ✅ 易於部署到 LangGraph Cloud
- ✅ 強大的 State 管理機制
- ✅ 與 LangChain 生態系統整合

#### Q2: 可以不使用 LLM 嗎？

**A**: 部分可以。
- `read_file_agent`: 不使用 LLM（純檔案 I/O）✅
- `datcom_tool_agent`: 依賴 LLM 解析（但可直接呼叫 tool）⚠️
- `supervisor`: 依賴 LLM 路由決策 ❌

如果有固定的工作流程，可以創建不使用 Supervisor 的版本。

#### Q3: 如何新增對其他航空器的支援？

**A**: 僅需準備新的配置檔案。
1. 在 `read_file_agent/data/` 創建新檔案 (如 `f16.txt`)
2. 修改 `read_file_agent` 支援檔案名參數
3. LLM 會自動解析新格式

Pydantic models 已涵蓋標準 DATCOM 卡片，無需修改。

#### Q4: 系統如何處理錯誤？

**A**: 多層錯誤處理:
1. **Pydantic 驗證**: 捕捉參數錯誤，LLM 可看到錯誤訊息並重試
2. **Tool 異常處理**: `try-except` 回傳錯誤訊息
3. **LangGraph 重試**: Agent 可自動重試失敗的操作
4. **用戶可見**: 所有錯誤透過 messages 回報

#### Q5: 如何調整 LLM 模型？

**A**: 修改 `.env`:

```bash
# 使用不同的模型
DEFAULT_LLM_MODEL=gpt-4
OPENAI_API_BASE_URL=https://api.openai.com/v1

# 或使用其他相容端點
DEFAULT_LLM_MODEL=claude-3-opus-20240229
OPENAI_API_BASE_URL=https://your-claude-endpoint/v1
```

注意: 確保端點支援 Function Calling。

### C. 術語表

| 術語 | 說明 |
|------|------|
| **Agent** | 具有特定職責的智能體，可使用工具完成任務 |
| **Supervisor** | 協調多個 agents 的中央控制器 |
| **State** | agents 間共享的資料結構 |
| **Tool** | Agent 可呼叫的函數（如讀檔、計算） |
| **LLM** | Large Language Model（大型語言模型） |
| **DATCOM** | Digital Datcom，氣動力計算軟體 |
| **for005.dat** | DATCOM 輸入檔案 |
| **for006.dat** | DATCOM 輸出檔案 |
| **Pydantic** | Python 資料驗證庫 |
| **LangGraph** | 構建 agent 工作流程的框架 |
| **StateGraph** | LangGraph 中的狀態機 |
| **MessagesState** | LangGraph 預定義的訊息狀態類型 |

### D. 快速命令參考

```bash
# 測試系統
python3 -m supervisor_agent.test_datcom_workflow

# 互動式測試
python3 -m supervisor_agent.test.interactive_test --verbose

# 測試 DATCOM Agent
python3 -m datcom_tool_agent.test_agent

# 測試 Generator
cd datcom_tool_agent && python3 run_generator.py

# 檢查環境
cat read_file_agent/.env

# 檢查輸出
cat datcom_tool_agent/output/for005.dat

# 驗證 LLM API
curl http://172.16.120.65:8089/v1/models
```

---

## 總結

**Operation Phoenix** 是一個設計優雅、功能完整的多代理人系統，展現了以下特點：

✅ **架構清晰**: Supervisor pattern 協調三個專門化 agents
✅ **職責分離**: 每個 agent 和 tool 單一職責
✅ **型別安全**: Pydantic v2 嚴格驗證
✅ **易於擴展**: Prebuilt components + 清晰介面
✅ **生產就緒**: 完整測試 + 文檔
✅ **設計原則**: 遵循 AGENT.md 與 GEMINI.md 哲學

**核心成就**:
- 成功協調多 Agent 協同工作流程
- LLM 驅動的智能資料解析
- 嚴謹的參數驗證與錯誤處理
- 平衡彈性與效能

**適用場景**:
- 航空器配置管理
- DATCOM 輸入檔案自動化生成
- 多步驟資料處理工作流程
- LLM-powered 資料解析應用

---

**文檔維護**: 本文檔應隨系統演進持續更新
**問題回報**: 若發現錯誤或需要補充，請提交 Issue
**貢獻指南**: 歡迎提交 Pull Request 改進系統

**Status**: 🚀 Ready for Production Deployment
