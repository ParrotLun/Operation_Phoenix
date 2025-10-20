"""
純讀檔 Graph - 直接讀取文件並存到 state
不需要 LLM，只讀檔案
"""
import os
from langgraph.graph import StateGraph, START, END
from my_agent.utils.state import AgentState

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
        
        # 更新 state
        return {
            "file_content": content
        }
    
    except Exception as e:
        error_msg = f"錯誤: 無法讀取文件 - {str(e)}"
        print(f"❌ {error_msg}")
        return {
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
app = graph
