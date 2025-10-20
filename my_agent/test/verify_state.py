"""
驗證 state 是否正確寫入
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from my_agent.agent import app

def verify_state():
    """驗證 state 內容"""
    print("=" * 60)
    print("🔍 驗證 State 寫入")
    print("=" * 60)
    
    # 調用 graph
    result = app.invoke({"messages": []}) # type: ignore
    
    # 檢查 state 結構
    print("\n📊 State 結構:")
    print(f"  - keys: {list(result.keys())}")
    print(f"  - messages: {len(result['messages'])} 條")
    print(f"  - file_content 是否存在: {'✅' if 'file_content' in result else '❌'}")
    
    # 檢查 file_content
    if 'file_content' in result and result['file_content']:
        content = result['file_content']
        print(f"\n✅ file_content 已寫入!")
        print(f"  - 類型: {type(content)}")
        print(f"  - 長度: {len(content)} 字元")
        print(f"  - 前 100 字: {content[:100]}...")
        
        # 驗證是否為空
        if content.strip():
            print("\n✅ 內容非空，寫入成功！")
        else:
            print("\n❌ 內容為空！")
    else:
        print("\n❌ file_content 不存在或為空！")
    
    # 返回完整 state 供檢查
    return result

if __name__ == "__main__":
    state = verify_state()
    
    print("\n" + "=" * 60)
    print("📋 完整 State 內容:")
    print("=" * 60)
    import json
    print(json.dumps({
        "messages_count": len(state.get("messages", [])),
        "file_content_length": len(state.get("file_content", "")),
        "file_content_preview": state.get("file_content", "")
    }, indent=2, ensure_ascii=False))