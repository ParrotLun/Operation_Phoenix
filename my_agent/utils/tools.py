from langchain_core.tools import tool
import os

@tool
def read_msg_file() -> str:
    """Read the content from my_agent/data/msg.txt file."""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "msg.txt")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"\n=== 讀取到的內容 ===\n{content}\n===================\n")
        return content
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        print(error_msg)
        return error_msg

tools = [read_msg_file]