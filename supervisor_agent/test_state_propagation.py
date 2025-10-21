"""
測試 state 在 supervisor 和 subgraph 之間的傳遞
驗證 file_content 是否從 read_file_agent 傳到 supervisor 的 state
"""
from supervisor_agent.agent import app


def test_state_propagation():
    """測試 state 是否正確傳遞"""
    print("\n" + "=" * 80)
    print("🔍 State Propagation Test - 檢查 file_content 是否傳遞")
    print("=" * 80)

    # 測試：讀取文件
    print("\n📝 執行：請讀取 msg.txt")
    print("-" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "請讀取 msg.txt"}]
    })

    # 檢查 state 內容
    print("\n🔎 檢查最終 state:")
    print("-" * 80)

    # 檢查 messages
    if result.get("messages"):
        print(f"✅ messages 欄位存在，共 {len(result['messages'])} 條訊息")
    else:
        print("❌ messages 欄位不存在")

    print()

    # 檢查 file_content (關鍵測試)
    if "file_content" in result:
        file_content = result["file_content"]
        if file_content:
            print(f"✅✅✅ file_content 欄位存在且有內容！")
            print(f"   類型: {type(file_content)}")
            print(f"   長度: {len(file_content)} 字元")
            print(f"   前 200 字元:\n   {file_content[:200]}...")
            print("\n🎉 成功！file_content 已從 read_file_agent 傳到 supervisor state！")
        else:
            print("⚠️  file_content 欄位存在但為空")
    else:
        print("❌ file_content 欄位不存在於 state 中")
        print("   這表示 SupervisorState 沒有正確使用，或 subgraph 沒有回傳 file_content")

    print()

    # 檢查其他欄位
    print("📋 State 中的所有欄位:")
    for key in result.keys():
        value_type = type(result[key]).__name__
        if key == "messages":
            print(f"   - {key}: {value_type} (length: {len(result[key])})")
        elif isinstance(result[key], str):
            print(f"   - {key}: {value_type} (length: {len(result[key])} chars)")
        else:
            print(f"   - {key}: {value_type}")

    print("\n" + "=" * 80)

    return result.get("file_content") is not None


if __name__ == "__main__":
    try:
        success = test_state_propagation()

        if success:
            print("\n✅ 測試成功！file_content 正確傳遞到 supervisor state")
        else:
            print("\n❌ 測試失敗！file_content 沒有傳遞到 supervisor state")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
