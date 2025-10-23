"""
純讀檔 Graph - 直接讀取文件並存到 state
不需要 LLM，只讀檔案
可以作為獨立 app 或 supervisor 的 subgraph 使用
"""
import os
import re
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from read_file_agent.utils.state import AgentState
from langchain_core.messages import AIMessage


def _parse_file_content(content: str) -> Dict[str, Any]:
    """
    解析檔案內容，提取結構化資料

    這個函數會嘗試識別檔案中的關鍵資訊：
    - DATCOM 參數（如果有）
    - 數值資料
    - 結構化區塊

    Returns:
        結構化的字典，包含解析出的資料
    """
    parsed = {
        "has_datcom_data": False,
        "sections": {},
        "key_values": {},
        "file_type": "unknown",
        "data_preview": content[:200] if content else ""
    }

    # 檢測是否包含 DATCOM 相關關鍵字
    datcom_keywords = ['NALPHA', 'MACH', 'FLTCON', 'SYNTHS', 'WGPLNF', 'BODY']
    if any(kw in content for kw in datcom_keywords):
        parsed["has_datcom_data"] = True
        parsed["file_type"] = "datcom_config"

    # 使用正則提取 key=value 對
    # 匹配格式：KEY= value 或 KEY=value
    key_value_pattern = r'([A-Z_]+)\s*=\s*([^\n]+)'
    matches = re.findall(key_value_pattern, content)

    for key, value in matches:
        parsed["key_values"][key] = value.strip()

    # 提取章節（基於 markdown 標題 ## ）
    section_pattern = r'##\s+([^\n]+)'
    sections = re.findall(section_pattern, content)

    if sections:
        parsed["sections"] = {
            "titles": sections,
            "count": len(sections)
        }

    # 統計資訊
    parsed["stats"] = {
        "total_chars": len(content),
        "total_lines": content.count('\n') + 1,
        "has_numbers": bool(re.search(r'\d+\.?\d*', content)),
        "has_sections": len(sections) > 0
    }

    return parsed

def read_file_node(state: AgentState) -> dict:
    """
    讀取 msg.txt 文件並存到 state
    這個 node 不使用 LLM，直接讀檔
    """
    # 計算文件路徑 - 正確路徑應該是 my_agent/data/msg.txt
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_file_dir, 'data')
    file_path = os.path.join(data_dir, 'msg.txt')

    print(f"\n📂 正在讀取文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✅ 成功讀取 {len(content)} 字元")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # 📝 解析檔案內容，提取結構化資料
        parsed_data = _parse_file_content(content)

        # 創建 AI 回應訊息（用於 supervisor 溝通）
        response = AIMessage(
            content=f"📄 已讀取 msg.txt 文件內容：\n\n{content}",
            name="read_file_agent"
        )

        # 更新 state - 包含 messages, file_content, 和 parsed_file_data
        return {
            "messages": [response],
            "file_content": content,
            "parsed_file_data": parsed_data  # 新增：結構化資料
        }
    
    except Exception as e:
        error_msg = f"錯誤: 無法讀取文件 - {str(e)}"
        print(f"❌ {error_msg}")

        error_response = AIMessage(
            content=error_msg,
            name="read_file_agent"
        )

        return {
            "messages": [error_response],
            "file_content": error_msg
        }

# 構建最簡單的 graph: START → read_file → END
graph_builder = StateGraph(AgentState)

# 添加讀檔節點
graph_builder.add_node("read_file", read_file_node)

# 設置流程: START → read_file → END
graph_builder.add_edge(START, "read_file")
graph_builder.add_edge("read_file", END)

# 編譯
graph = graph_builder.compile()

# 設定 graph 名稱，這樣可以被 supervisor 識別
graph.name = "read_file_agent"

# Export as app
app = graph
