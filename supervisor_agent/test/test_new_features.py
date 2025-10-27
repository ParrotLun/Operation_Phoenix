"""
測試新功能：
1. State 新欄位 (latest_datcom, parsed_file_data)
2. 對話記憶管理
"""
from supervisor_agent.agent import app
from supervisor_agent.utils.memory_manager import ConversationMemoryManager, SessionManager
from langchain_core.messages import HumanMessage


def test_latest_datcom_state():
    """測試 latest_datcom state 欄位"""
    print("\n" + "=" * 80)
    print("TEST 1: latest_datcom State 欄位")
    print("=" * 80)

    # 執行產生 DATCOM 的工作流程
    result = app.invoke({
        "messages": [HumanMessage(content="請讀取 msg.txt 並產生 DATCOM 檔案")]
    })

    # 檢查 latest_datcom
    if result.get("latest_datcom"):
        latest = result["latest_datcom"]
        print("\n✅ latest_datcom 已設定:")
        print(f"   Case ID: {latest['case_id']}")
        print(f"   Output: {latest['output_path']}")
        print(f"   Generated at: {latest['generated_at']}")
        print(f"   Wing NACA: {latest['parameters']['wing']['naca']}")
        print(f"   NALPHA: {latest['parameters']['flight_conditions']['nalpha']}")
    else:
        print("\n❌ latest_datcom 未設定")

    return result


def test_parsed_file_data():
    """測試 parsed_file_data state 欄位"""
    print("\n" + "=" * 80)
    print("TEST 2: parsed_file_data State 欄位")
    print("=" * 80)

    # 執行讀檔工作流程
    result = app.invoke({
        "messages": [HumanMessage(content="請讀取 msg.txt")]
    })

    # 檢查 parsed_file_data
    if result.get("parsed_file_data"):
        parsed = result["parsed_file_data"]
        print("\n✅ parsed_file_data 已設定:")
        print(f"   File type: {parsed['file_type']}")
        print(f"   Has DATCOM data: {parsed['has_datcom_data']}")
        print(f"   Sections: {parsed.get('sections', {}).get('count', 0)}")
        print(f"   Key values found: {len(parsed['key_values'])}")
        print(f"   Total chars: {parsed['stats']['total_chars']}")

        # 顯示一些 key values
        if parsed['key_values']:
            print("\n   Sample key-values:")
            for key, value in list(parsed['key_values'].items())[:5]:
                print(f"      {key} = {value}")
    else:
        print("\n❌ parsed_file_data 未設定")

    return result


def test_conversation_memory():
    """測試對話記憶管理"""
    print("\n" + "=" * 80)
    print("TEST 3: 對話記憶管理")
    print("=" * 80)

    memory_manager = ConversationMemoryManager(
        max_recent_messages=4,
        compression_threshold=10
    )

    # 模擬一個有很多訊息的 state
    from langchain_core.messages import AIMessage

    mock_messages = []
    for i in range(15):
        if i % 2 == 0:
            mock_messages.append(HumanMessage(content=f"User message {i}"))
        else:
            mock_messages.append(AIMessage(content=f"AI response {i}"))

    mock_state = {"messages": mock_messages}

    # 測試壓縮
    print("\n📊 原始訊息數:", len(mock_messages))

    optimized = memory_manager.prepare_context_for_llm(mock_state)
    print(f"✅ 壓縮後訊息數: {len(optimized)}")

    # 檢查是否有摘要
    if optimized and optimized[0].__class__.__name__ == "SystemMessage":
        print(f"✅ 包含摘要訊息 (長度: {len(optimized[0].content)} 字元)")

    # 測試關鍵資訊提取
    print("\n" + "-" * 80)
    print("測試關鍵資訊提取:")

    # 創建包含 DATCOM 資訊的訊息
    test_messages = [
        HumanMessage(content="請讀取 msg.txt 並產生 DATCOM 檔案"),
        AIMessage(content="已讀取 msg.txt，包含 949 字元"),
        AIMessage(content="✅ DATCOM 檔案已產生，NALPHA=6, for005.dat")
    ]

    key_info = memory_manager.extract_key_info_from_messages(test_messages)
    print(f"✅ DATCOM generated: {key_info['datcom_generated']}")
    print(f"✅ File read: {key_info['file_read']}")
    print(f"✅ Last user request: {key_info['last_user_request'][:50]}...")


def test_session_management():
    """測試 Session 管理"""
    print("\n" + "=" * 80)
    print("TEST 4: Session 管理")
    print("=" * 80)

    # 生成 session ID
    session_id = SessionManager.generate_session_id()
    print(f"\n✅ Generated session ID: {session_id}")

    # 測試 session 識別
    state1 = {"conversation_id": session_id}
    state2 = {"conversation_id": "different_session"}

    is_same = SessionManager.is_same_session(state1, session_id)
    print(f"✅ Same session check: {is_same}")

    is_different = SessionManager.is_same_session(state2, session_id)
    print(f"✅ Different session check: {is_different}")


def test_continuous_conversation():
    """測試連續對話"""
    print("\n" + "=" * 80)
    print("TEST 5: 連續對話模擬")
    print("=" * 80)

    memory_manager = ConversationMemoryManager()

    # 第一輪對話
    print("\n📝 第一輪對話:")
    session_id = SessionManager.generate_session_id()

    result1 = app.invoke({
        "messages": [HumanMessage(content="請讀取 msg.txt 並產生 DATCOM 檔案")],
        "conversation_id": session_id
    })

    print(f"   Session ID: {result1.get('conversation_id')}")
    print(f"   Messages: {len(result1.get('messages', []))}")
    print(f"   Latest DATCOM: {'✅' if result1.get('latest_datcom') else '❌'}")

    # 第二輪對話（同一個 session）
    print("\n📝 第二輪對話（連續）:")

    # 壓縮第一輪的訊息
    optimized_messages = memory_manager.prepare_context_for_llm(result1)

    result2 = app.invoke({
        "messages": optimized_messages + [HumanMessage(content="檔案裡有幾個章節？")],
        "conversation_id": session_id,
        "latest_datcom": result1.get("latest_datcom"),  # 保留 DATCOM 資訊
        "parsed_file_data": result1.get("parsed_file_data")  # 保留解析資料
    })

    print(f"   Session ID: {result2.get('conversation_id')}")
    print(f"   Messages: {len(result2.get('messages', []))}")
    print(f"   Has context: {memory_manager.has_conversation_context(result2)}")


def run_all_tests():
    """執行所有測試"""
    print("\n" + "🧪" * 40)
    print("開始測試新功能")
    print("🧪" * 40)

    try:
        # Test 1: latest_datcom
        result1 = test_latest_datcom_state()

        # Test 2: parsed_file_data
        result2 = test_parsed_file_data()

        # Test 3: Memory management
        test_conversation_memory()

        # Test 4: Session management
        test_session_management()

        # Test 5: Continuous conversation
        test_continuous_conversation()

        print("\n" + "=" * 80)
        print("✅ 所有測試完成")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
