#!/usr/bin/env python3
"""
快速測試純讀檔 Graph
"""
import sys
import os

# 設置正確的路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("=" * 60)
print("測試純讀檔 Graph")
print("=" * 60)

# 導入 agent
from my_agent.agent import app

print("\n🚀 執行 Graph...\n")

# 調用 graph
result = app.invoke({"messages": []}) # type: ignore

print("\n" + "=" * 60)
print("結果:")
print("=" * 60)

if "file_content" in result:
    content = result["file_content"]
    print(f"✅ file_content 長度: {len(content)} 字元")
    print(f"\n前 300 字元:")    
    print(content[:300])
    print("...")
else:
    print("❌ file_content 不存在")

print("\n" + "=" * 60)
