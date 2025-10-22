# My Agent - 簡單文件讀取 Agent

## 架構說明

這是一個使用 `create_react_agent` 構建的最簡單 LangGraph Agent，功能是讀取 `data/msg.txt` 文件。

### 核心組件

- **State**: `AgentState` - 包含 messages 和 file_content
- **Tool**: `read_msg_file` - 讀取 msg.txt 文件
- **Agent**: 使用 `create_react_agent` 預構建組件
- **Model**: `openai/gpt-oss-20b` (自定義端點)

### 文件結構

```
my_agent/
├── agent.py          # 主要 agent (使用 create_react_agent)
├── data/
│   └── msg.txt       # 要讀取的文件
├── utils/
│   ├── nodes.py      # 模型配置
│   ├── state.py      # State 定義
│   └── tools.py      # 工具定義 (read_msg_file)
├── test_agent.py     # 測試腳本
└── requirements.txt  # 依賴
```

## 使用方法

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設置環境變量

確保 `.env` 文件包含：
```
OPENAI_API_BASE_URL=http://172.16.120.65:8089/v1
OPENAI_API_KEY=your-api-key
```

### 3. 運行測試

```bash
cd /home/c1140921/agent_Read
python -m my_agent.test_agent
```

### 4. 使用 Agent

```python
from my_agent.agent import app

result = app.invoke({
    "messages": [{"role": "user", "content": "請讀取 msg.txt 文件"}]
})

print(result["messages"][-1].content)
```

## 工作流程

```
用戶請求 → Agent (LLM) → 判斷需要工具 → 調用 read_msg_file → 讀取文件 → 返回內容 → Agent 整理回應
```

## 特點

✅ 使用 `create_react_agent` - 最簡單的架構  
✅ 自動處理工具調用循環  
✅ 讀取文件時自動印出內容  
✅ State 中保存文件內容  
✅ 使用自定義 OpenAI 端點

## 相比手動 StateGraph 的優勢

- 代碼量減少 60%+
- 不需要手動定義 `should_continue` 條件
- 不需要手動設置 edges
- 自動處理工具循環
- 更易維護
