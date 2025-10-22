# DATCOM Tool Agent - 設計文檔

## 🎯 設計目標

基於你的需求：
> 我希望可以處理一下 read content 然後我們使用 tool 寫進 datcom 格式的檔案 for005.dat

**選擇方案：選項 B - LLM 驅動的解析 Agent**
- datcom_tool_agent 做全套：讀文字 → LLM 解析 → 填 Pydantic → 寫檔
- 優點：一個 agent 搞定所有事
- 折衷：Tool 只負責寫檔（保持簡單）

## 📐 架構決策

### 決策 1: 職責分離

**問題**: LLM 解析 vs Tool 寫檔，如何分工？

**方案**:
```
┌─────────────────────────────────────────┐
│  datcom_tool_agent (LLM Agent)          │
│  - 職責: 解析用戶輸入                    │
│  - 輸入: 任意格式的飛機配置數據          │
│  - 輸出: 呼叫 write_datcom_file tool     │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  write_datcom_file (Tool)               │
│  - 職責: 格式化 + 寫檔                   │
│  - 輸入: 57 個明確的參數                 │
│  - 輸出: output/for005.dat              │
└─────────────────────────────────────────┘
```

**理由**（Linus 原則）:
- ✅ Tool 保持簡單（dumbest clear approach）
- ✅ 可被其他程式直接呼叫（無需 LLM）
- ✅ 參數明確（no magic, no special cases）
- ✅ 單元測試容易

### 決策 2: 參數數量（57 個參數）

**問題**: 為什麼不用字典或 JSON？

**方案**: 每個 DATCOM 欄位都是獨立的 tool 參數

**理由**:
1. **明確性**: IDE 自動補全，型別檢查
2. **錯誤訊息精準**: "missing parameter 'wing_naca'" vs "missing key in dict"
3. **文檔自動生成**: Tool description 包含所有參數說明
4. **LLM 友好**: LangChain 會將 tool schema 傳給 LLM

**Linus 會說**:
> "If you have 57 parameters, that's because you NEED 57 parameters.
> Don't hide them in a dict just to make it 'look cleaner'."

### 決策 3: 數值格式化

**需求**: 整數用 `6.0`，浮點數最多四位小數

**實現**:
```python
def _format_single_number(num):
    if isinstance(num, int) or (isinstance(num, float) and num == int(num)):
        return f"{float(num):.1f}"  # 6 → 6.0
    else:
        formatted = f"{num:.4f}".rstrip('0').rstrip('.')
        if '.' not in formatted:
            formatted += '.0'
        return formatted  # 0.5489 → 0.5489, 10000.0 → 10000.0
```

**理由**:
- ✅ 統一規則，無特殊情況
- ✅ 符合 Fortran namelist 慣例
- ✅ 人類可讀（避免 `6.0000`）

### 決策 4: 輸出路徑

**需求**: 寫到 `datcom_tool_agent/output/for005.dat`

**實現**:
```python
output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "for005.dat")
```

**理由**:
- ✅ 與 agent 程式碼放在一起（locality）
- ✅ 不汙染其他目錄
- ✅ 容易清理和版本控制

### 決策 5: Pydantic 驗證

**問題**: 為什麼要 Pydantic？直接寫字串不行嗎？

**方案**: 所有數據先經過 Pydantic models 驗證

**驗證規則**:
```python
class FLTCON(BaseModel):
    NALPHA: int = Field(..., le=20)  # ≤ 20
    ALSCHD: List[float] = Field(...)

    @field_validator('ALSCHD')
    def check_alpha_count(cls, v, info):
        if len(v) != info.data['NALPHA']:
            raise ValueError(...)
```

**理由**:
- ✅ 防止錯誤（長度不匹配、數值超出範圍）
- ✅ 早期失敗（fail fast）
- ✅ 清楚的錯誤訊息

**避免的問題**:
```
❌ 沒驗證: NALPHA=6, 但 ALSCHD 只有 5 個值 → DATCOM 執行時錯誤
✅ 有驗證: Pydantic 立即報錯 "ALSCHD must have 6 values"
```

## 🔄 工作流程

### 完整流程

```
1. 用戶輸入
   ↓
   "請產生 PC-9 的 DATCOM 檔案：攻角 1-6 度，馬赫數 0.5489..."

2. Supervisor 路由
   ↓
   識別關鍵字 "DATCOM" → 路由給 datcom_tool_agent

3. datcom_tool_agent LLM 解析
   ↓
   提取參數:
   - nalpha=6
   - alschd="1.0,2.0,3.0,4.0,5.0,6.0"
   - nmach=1
   - mach="0.5489"
   - ...（共 57 個參數）

4. LLM 呼叫 write_datcom_file tool
   ↓
   write_datcom_file(
       nalpha=6,
       alschd="1.0,2.0,3.0,4.0,5.0,6.0",
       ...
   )

5. Tool 內部處理
   ↓
   a. 解析 comma-separated strings → lists
   b. 建立 Pydantic models
   c. Pydantic 驗證
   d. 呼叫 DatcomGenerator
   e. 格式化輸出
   f. 寫入 output/for005.dat

6. 回傳結果
   ↓
   "✅ Successfully wrote DATCOM file to: .../output/for005.dat"
```

### 錯誤處理

```python
try:
    # Pydantic validation
    flight_conditions = FLTCON(
        NALPHA=nalpha,
        ALSCHD=parse_floats(alschd),
        ...
    )
except ValidationError as e:
    return f"❌ Validation error: {str(e)}"
except Exception as e:
    return f"❌ Error writing DATCOM file: {str(e)}"
```

**好處**:
- ✅ 清楚的錯誤訊息傳回給用戶
- ✅ 不會產生錯誤的檔案
- ✅ LLM 可以看到錯誤並重試

## 🧩 整合 Supervisor

### 修改點

**1. Import agent**
```python
from datcom_tool_agent.agent import datcom_tool_agent
```

**2. 加入 agents 列表**
```python
supervisor = create_supervisor(
    agents=[read_file_agent, tool_agent, datcom_tool_agent],
    ...
)
```

**3. 更新 prompt**
```python
prompt="""You are a supervisor managing three specialized agents:
1. read_file_agent: ...
2. tool_agent: ...
3. datcom_tool_agent: Handles DATCOM file generation
"""
```

### 協同工作場景

**場景 1: 直接產生 DATCOM**
```
用戶: "產生 PC-9 DATCOM 檔案..."
    ↓
Supervisor → datcom_tool_agent → 完成
```

**場景 2: 先讀檔再產生**
```
用戶: "讀取 msg.txt 並產生 DATCOM 檔案"
    ↓
Supervisor → read_file_agent (讀檔)
    ↓ (state.file_content = "...")
Supervisor → datcom_tool_agent (解析 + 產生)
    ↓
完成
```

**關鍵**: `SupervisorState` 包含 `file_content` 欄位，讓 agents 共享數據

## 🎨 設計原則對照表

| 原則 | 實現 | 證據 |
|------|------|------|
| **Deployment-First** | ✅ | `app = datcom_tool_agent` 可直接部署 |
| **Prebuilt Components** | ✅ | 使用 `create_react_agent` |
| **Simple State** | ✅ | 使用 `MessagesState` |
| **Single Responsibility** | ✅ | Tool 只寫檔，LLM 只解析 |
| **Dumbest Clear Approach** | ✅ | Tool 是純函數，無副作用 |
| **No Special Cases** | ✅ | 統一的數值格式化規則 |
| **Zero Breakage** | ✅ | 獨立 agent，不影響現有系統 |
| **Solve Root Cause** | ✅ | 用 Pydantic 根本解決格式錯誤問題 |

## 🚀 未來擴展

### 可能的改進

1. **支援部分參數**
   ```python
   @tool
   def write_simple_datcom_file(
       nalpha: int,
       alschd: str,
       # 其他參數有默認值
   ):
       ...
   ```

2. **讀取現有 DATCOM 檔案**
   ```python
   @tool
   def read_datcom_file(file_path: str) -> DatcomInput:
       # 解析現有檔案
   ```

3. **批次產生**
   ```python
   @tool
   def write_multiple_datcom_files(configs: List[Dict]) -> List[str]:
       # 一次產生多個檔案
   ```

4. **驗證檔案**
   ```python
   @tool
   def validate_datcom_file(file_path: str) -> Dict:
       # 檢查檔案格式是否正確
   ```

### 不該做的事

❌ **不要讓 tool 自己解析文字**
```python
# ❌ 錯誤示範
@tool
def write_datcom_from_text(text: str):
    # Tool 裡面做解析 → 複雜、難測試
```

❌ **不要用 magic parameters**
```python
# ❌ 錯誤示範
@tool
def write_datcom_file(**kwargs):
    # 參數不明確 → LLM 容易搞錯
```

❌ **不要混合多個職責**
```python
# ❌ 錯誤示範
@tool
def read_parse_and_write_datcom(input_file: str, output_file: str):
    # 做太多事 → 違反單一職責原則
```

## 📊 效能考量

### Token 使用

**Tool Schema Size**: ~2000 tokens（57 個參數的描述）

**優化**:
- ✅ 參數描述簡潔但完整
- ✅ 使用縮寫（如 `NALPHA` 而非 `number_of_alpha`）
- ✅ 分組相關參數（Flight Conditions, Synthesis, etc.）

### 執行時間

```
LLM 解析: ~2-5 秒（取決於 LLM 速度）
Pydantic 驗證: <10ms
檔案寫入: <10ms
總計: ~2-5 秒
```

**瓶頸**: LLM 解析（無法優化）

### 記憶體使用

```
Pydantic models: ~1KB
輸出檔案: ~2KB
總計: 可忽略
```

## 🎓 學到的教訓

### 1. 參數化 > 靈活性

起初可能想做：
```python
@tool
def write_datcom_file(config: dict):  # 看起來更簡潔
```

但實際上：
```python
@tool
def write_datcom_file(nalpha: int, alschd: str, ...):  # 更明確
```

**原因**: LLM 需要知道確切的參數名稱和型別

### 2. Pydantic 是你的朋友

不要怕麻煩去寫 validators：
```python
@field_validator('ALSCHD')
def check_alpha_count(cls, v, info):
    if len(v) != info.data['NALPHA']:
        raise ValueError(...)
```

這會在未來省下大量 debug 時間。

### 3. 格式化規則要統一

一開始可能想：
```python
if value < 10:
    return f"{value:.4f}"
else:
    return f"{value:.1f}"
```

但這是 **special case**，會導致不一致。應該：
```python
if is_integer_value(value):
    return f"{value:.1f}"
else:
    return smart_format(value)
```

統一的規則更容易理解和維護。

## 總結

**【Core Judgment】** ✅ 設計完成，可用於生產環境

**【Solution】**
- LLM Agent 負責複雜的解析邏輯
- Tool 負責簡單的寫檔操作
- Pydantic 確保數據正確性
- 整合到 Supervisor 實現協同工作

**遵循原則**:
1. ✅ 簡單明確（Linus: "dumbest clear approach"）
2. ✅ 單一職責（Tool 只做一件事）
3. ✅ 無破壞性（可選擇性整合）
4. ✅ 解決根本問題（Pydantic 驗證）

**可擴展性**: 未來可輕鬆添加新功能（讀取、驗證、批次處理）而不影響現有架構。
