# DATCOM Tool Agent

**LLM 驅動的 DATCOM 檔案產生器 Agent**

## 📋 設計概念

基於 [AGENT.md](../doc/AGENT.md) 和 [GEMINI.md](../doc/GEMINI.md) 的原則設計：

### 【Core Judgment】✅ Worth doing

**設計哲學：**
- **職責分離**: LLM 負責解析，Tool 負責寫檔
- **簡單明確**: 一個 tool (`write_datcom_file`)，一個職責（寫 DATCOM 檔案）
- **Pydantic 驗證**: 所有數據經過嚴格的型別檢查
- **智能格式化**: 整數用 `1.0`，浮點數最多四位小數

## 🏗️ 架構

```
User Request (DATCOM 數據)
    ↓
Supervisor → datcom_tool_agent (LLM-driven)
    ↓
LLM 解析文字內容
    ↓
填充 Pydantic Models (FLTCON, SYNTHS, BODY, WGPLNF, HTPLNF, VTPLNF)
    ↓
調用 write_datcom_file tool
    ↓
DatcomGenerator 格式化輸出
    ↓
datcom_tool_agent/output/for005.dat ✅
```

## 📁 檔案結構

```
datcom_tool_agent/
├── agent.py              # LLM agent + write_datcom_file tool
├── data_model.py         # Pydantic models (6 cards)
├── run_generator.py      # DatcomGenerator (formatting logic)
├── output/               # 輸出目錄
│   └── for005.dat        # 生成的 DATCOM 檔案
├── test_agent.py         # Agent 測試腳本
├── QII.md               # 範例資料（PC-9）
└── README.md            # 本文檔
```

## 🎯 核心元件

### 1. **write_datcom_file** Tool

**職責**: 純粹的檔案寫入工具

**特點**:
- ✅ 接收 57 個參數（涵蓋所有 DATCOM 卡片）
- ✅ 驗證數據（透過 Pydantic）
- ✅ 寫入 `output/for005.dat`
- ✅ 簡單、無副作用、可測試

**範例呼叫**:
```python
write_datcom_file(
    nalpha=6,
    alschd="1.0,2.0,3.0,4.0,5.0,6.0",
    nmach=1,
    mach="0.5489",
    # ... 其他參數
)
```

### 2. **datcom_tool_agent** (LLM Agent)

**職責**: 解析用戶輸入 → 呼叫 tool

**特點**:
- ✅ 使用 `create_react_agent`（prebuilt component）
- ✅ LLM 負責智能解析（支援多種輸入格式）
- ✅ 自動映射數據到正確的 tool 參數

**支援的輸入格式**:
- 結構化 Markdown（如 QII.md）
- DATCOM 原始格式
- JSON/YAML
- 自然語言描述

### 3. **DatcomGenerator** (格式化引擎)

**職責**: Pydantic 物件 → DATCOM 文字格式

**格式規則**:
```python
整數值 (6, 1, 2) → 一位小數 (6.0, 1.0, 2.0)
浮點數 (0.5489)  → 保留實際小數位數（最多四位）
整數浮點數 (10000.0) → 一位小數 (10000.0)
```

**輸出範例**:
```fortran
CASEID PC-9
$FLTCON NALPHA=6.0,ALSCHD=1.0,2.0,3.0,4.0,5.0,6.0,NMACH=1.0,MACH=0.5489,NALT=1.0,ALT=10000.0,WT=5180.0$
$SYNTHS XCG=11.3907,ZCG=0.0,XW=11.107,ZW=-1.6339,ALIW=1.0,...$
...
```

## 🔧 使用方式

### 方式 1: 獨立使用

```python
from datcom_tool_agent.agent import app

result = app.invoke({
    "messages": [{
        "role": "user",
        "content": """
        請產生 PC-9 的 DATCOM 檔案：
        - 攻角: 1.0 到 6.0 度（6個點）
        - 馬赫數: 0.5489
        - 高度: 10000 ft
        ...
        """
    }]
})

print(result["messages"][-1].content)
# ✅ Successfully wrote DATCOM file to: .../output/for005.dat
```

### 方式 2: 透過 Supervisor

```python
from supervisor_agent.agent import app

result = app.invoke({
    "messages": [{
        "role": "user",
        "content": "請讀取 msg.txt 並產生 DATCOM 檔案"
    }]
})
```

**Supervisor 會自動**:
1. 路由給 `read_file_agent` 讀取 msg.txt
2. 路由給 `datcom_tool_agent` 產生 for005.dat

## 📊 Pydantic Models

### FLTCON (Flight Conditions)
- `NALPHA`: 攻角數量 (≤20)
- `ALSCHD`: 攻角值列表
- `NMACH`: 馬赫數組數 (≤20)
- `MACH`: 馬赫數列表
- `NALT`: 高度組數 (≤20)
- `ALT`: 高度列表
- `WT`: 重量

### SYNTHS (Synthesis)
- `XCG`, `ZCG`: 重心位置
- `XW`, `ZW`, `ALIW`: 主翼位置與安裝角
- `XH`, `ZH`, `ALIH`: 水平尾翼位置與安裝角
- `XV`, `ZV`: 垂直尾翼位置

### BODY (Body Geometry)
- `NX`: 機身站位數 (≤20)
- `X`, `R`, `ZU`, `ZL`: 機身幾何數據
- `ITYPE`: 1=直翼, 2=後掠翼
- `METHOD`: 計算方法

### WGPLNF (Wing Planform)
- `NACA_W`: 翼型（如 "6-63-415"）
- `CHRDTP`, `CHRDR`: 翼尖/翼根弦長
- `SSPN`, `SSPNE`: 半翼展
- `SAVSI`: 後掠角
- `TWISTA`: 扭轉角
- `DHDADI`: 上反角

### HTPLNF (Horizontal Tail)
- 同 WGPLNF 結構

### VTPLNF (Vertical Tail)
- 同 WGPLNF 結構（無 TWISTA, DHDADI）

## 🧪 測試

```bash
# 測試 agent（需要 LLM API）
cd /home/c1140921/Operation_Phoenix
python3 -m datcom_tool_agent.test_agent

# 測試 generator（不需要 LLM）
cd datcom_tool_agent
python3 run_generator.py
```

## 🚀 部署

### LangGraph Cloud

```bash
cd datcom_tool_agent
langgraph up
```

### 本地部署

```python
from datcom_tool_agent.agent import app

# app 已經是編譯好的 CompiledGraph
```

## 🎨 設計原則遵循

### ✅ AGENT.md 原則

1. **Deployment-First**: `app = datcom_tool_agent`（可直接部署）
2. **Prebuilt Components**: 使用 `create_react_agent`
3. **Simple State**: 使用 `MessagesState`
4. **Single Responsibility**: Tool 只負責寫檔，LLM 負責解析

### ✅ GEMINI.md 原則（Linus 風格）

1. **Dumbest Clear Approach**: Tool 參數化，不做聰明事
2. **No Special Cases**: 所有數值統一格式化規則
3. **Zero Breakage**: 獨立 agent，不影響現有系統
4. **Solve Root Cause**:
   - 問題：DATCOM 格式複雜、易錯
   - 解法：Pydantic 驗證 + 自動格式化

## 🔄 工作流程範例

```
用戶: "請根據 QII.md 產生 DATCOM 檔案"
    ↓
Supervisor: 識別為 DATCOM 任務 → 路由給 datcom_tool_agent
    ↓
datcom_tool_agent LLM: 解析 QII.md 內容
    ↓
提取參數:
  - nalpha=6
  - alschd="1.0,2.0,3.0,4.0,5.0,6.0"
  - wing_naca="6-63-415"
  - ...
    ↓
呼叫 write_datcom_file tool
    ↓
Pydantic 驗證: ✅ 通過
    ↓
DatcomGenerator 格式化
    ↓
寫入 output/for005.dat
    ↓
回傳: "✅ Successfully wrote DATCOM file to: .../output/for005.dat"
```

## 🐛 常見問題

### Q: 為什麼不讓 tool 直接接收文字內容？

**A**: 遵循 Linus 原則 - **tool 應該簡單且專注**。
- Tool 職責：格式化 + 寫檔
- LLM 職責：解析 + 理解

這樣 tool 可以：
- ✅ 被其他程式直接呼叫（不需要 LLM）
- ✅ 單元測試
- ✅ 參數清晰可見

### Q: 為什麼用這麼多參數（57個）？

**A**: **明確性 > 便利性**。
- ✅ 每個參數都有明確的型別和說明
- ✅ IDE 自動補全
- ✅ 錯誤訊息精準
- ✅ 符合 Pydantic 哲學

### Q: 能否支援部分參數？

**A**: 目前所有參數都是必填。未來可以：
1. 為某些參數添加默認值
2. 創建多個 tool 變體（如 `write_simple_datcom_file`）

## 📝 環境需求

```txt
langchain>=0.3.0
langchain-openai
langgraph>=0.3.0
langgraph-supervisor
pydantic>=2.0
python-dotenv
```

## 🎓 參考文獻

- [AGENT.md](../doc/AGENT.md) - LangGraph 開發原則
- [GEMINI.md](../doc/GEMINI.md) - Linus Torvalds 人格設定
- [QII.md](QII.md) - PC-9 範例數據
- [supervisor_agent/README.md](../supervisor_agent/README.md) - Supervisor 架構

---

**【Core Judgment】** ✅ 設計完成

**【Solution】**
1. ✅ 簡化數據結構（Pydantic + 單一 tool）
2. ✅ 消除特殊情況（統一格式化規則）
3. ✅ 最直白的方案（LLM 解析 + Tool 寫檔）
4. ✅ 零破壞（獨立 agent，可選擇性整合）
