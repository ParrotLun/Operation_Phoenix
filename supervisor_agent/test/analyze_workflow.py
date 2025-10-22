"""
Workflow Analysis Tool
分析 supervisor 多步驟工作流程，顯示每個 message 的詳細資訊和 state 傳遞
"""
from supervisor_agent.agent import app
import json


def analyze_workflow(user_query: str):
    """
    分析完整的工作流程，顯示：
    1. 每個 message 的類型、來源、內容
    2. State 的變化（特別是 file_content）
    3. Transfer 的路由決策
    """
    print("=" * 100)
    print("🔍 WORKFLOW ANALYSIS")
    print("=" * 100)
    print(f"\n👤 User Query: {user_query}\n")
    print("⏳ Running workflow...\n")

    # 執行工作流程
    result = app.invoke({
        "messages": [{"role": "user", "content": user_query}]
    })

    messages = result.get("messages", [])
    print("=" * 100)
    print(f"📊 總共有 {len(messages)} 個 Messages")
    print("=" * 100)

    # 分析每個 message
    for i, msg in enumerate(messages, 1):
        print(f"\n{'─' * 100}")
        print(f"Message #{i}: {type(msg).__name__}")
        print(f"{'─' * 100}")

        # 顯示來源
        if hasattr(msg, 'name') and msg.name:
            print(f"📤 From: {msg.name}")
        else:
            print(f"📤 From: User/System")

        # 顯示內容
        if hasattr(msg, 'content') and msg.content:
            content = msg.content
            if len(content) > 300:
                print(f"📝 Content (前 300 字元):\n{content[:300]}...")
            else:
                print(f"📝 Content:\n{content}")

        # 如果是 ToolMessage，顯示 tool call 資訊
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"\n🔧 Tool Calls:")
            for tc in msg.tool_calls:
                print(f"   - Tool: {tc.get('name', 'N/A')}")
                if 'args' in tc and tc['args']:
                    args_str = json.dumps(tc['args'], indent=4, ensure_ascii=False)
                    if len(args_str) > 200:
                        print(f"   - Args (前 200 字元): {args_str[:200]}...")
                    else:
                        print(f"   - Args: {args_str}")

        # 分析這個 message 的意義
        print(f"\n💡 分析:")
        if i == 1:
            print("   → 使用者的原始請求")
        elif "supervisor" in str(getattr(msg, 'name', '')):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_name = msg.tool_calls[0].get('name', '')
                if 'read_file' in tool_name:
                    print("   → Supervisor 決定路由到 read_file_agent")
                elif 'datcom' in tool_name:
                    print("   → Supervisor 決定路由到 datcom_tool_agent")
                elif 'tool_agent' in tool_name:
                    print("   → Supervisor 決定路由到 tool_agent")
                else:
                    print(f"   → Supervisor 呼叫工具: {tool_name}")
            else:
                print("   → Supervisor 的最終回應給使用者")
        elif "transfer_to" in str(getattr(msg, 'name', '')):
            print("   → 執行 transfer (路由到目標 agent)")
        elif "read_file_agent" in str(getattr(msg, 'name', '')):
            if "Transferring back" in str(getattr(msg, 'content', '')):
                print("   → read_file_agent 完成工作，準備返回 supervisor")
                print("   → 此時 state.file_content 已被設定")
            else:
                print("   → read_file_agent 執行讀檔並輸出結果")
        elif "datcom_tool_agent" in str(getattr(msg, 'name', '')):
            if "Transferring back" in str(getattr(msg, 'content', '')):
                print("   → datcom_tool_agent 完成工作，準備返回 supervisor")
            else:
                print("   → datcom_tool_agent 執行 DATCOM 檔案產生")
                print("   → 可以從 state.file_content 讀取資料")
        elif "transfer_back" in str(getattr(msg, 'name', '')):
            print("   → 執行 transfer back (返回 supervisor)")

    # 顯示最終 state
    print(f"\n{'=' * 100}")
    print("📦 Final State")
    print(f"{'=' * 100}")
    if 'file_content' in result and result['file_content']:
        print(f"✅ file_content: {len(result['file_content'])} 字元")
        print(f"   (前 100 字元): {result['file_content'][:100]}...")
    else:
        print("❌ file_content: None")

    # 總結工作流程
    print(f"\n{'=' * 100}")
    print("🎯 WORKFLOW SUMMARY")
    print(f"{'=' * 100}")
    print("\n完整流程:")
    print("1. 👤 User → Supervisor (Message #1-2)")
    print("   使用者發出請求: '讀取檔案並產生 DATCOM'")
    print()
    print("2. 🔀 Supervisor → read_file_agent (Message #3-6)")
    print("   - Message #2: Supervisor 決定路由到 read_file_agent")
    print("   - Message #3: 執行 transfer_to_read_file_agent")
    print("   - Message #4: read_file_agent 讀取 msg.txt")
    print("   - Message #5: read_file_agent 說 'Transferring back'")
    print("   - Message #6: 執行 transfer_back_to_supervisor")
    print("   ✅ State 更新: file_content 被設定")
    print()
    print("3. 🔀 Supervisor → datcom_tool_agent (Message #7-11)")
    print("   - Message #7: Supervisor 決定路由到 datcom_tool_agent")
    print("   - Message #8: 執行 transfer_to_datcom_tool_agent")
    print("   - Message #9: datcom_tool_agent 從 state.file_content 讀取資料並產生檔案")
    print("   - Message #10: datcom_tool_agent 說 'Transferring back'")
    print("   - Message #11: 執行 transfer_back_to_supervisor")
    print()
    print("4. ✅ Supervisor → User (Message #12)")
    print("   - Message #12: Supervisor 回應使用者 '已完成'")
    print()
    print("=" * 100)
    print("為什麼需要 12 個 messages?")
    print("=" * 100)
    print("""
因為使用了 LangGraph 的 Supervisor Pattern，每次 agent 切換都需要：
1. Supervisor 決定要路由到哪個 agent (AIMessage with tool_call)
2. 執行 transfer tool (ToolMessage)
3. Agent 執行任務 (AIMessage)
4. Agent 說要返回 (AIMessage 'Transferring back')
5. 執行 transfer_back tool (ToolMessage)
6. 回到 Supervisor

這個流程執行了 2 次（read_file_agent + datcom_tool_agent），所以：
- User request: 1 message
- First routing (read_file): 5 messages (決定 → transfer → 執行 → transfer back → 返回)
- Second routing (datcom): 5 messages (決定 → transfer → 執行 → transfer back → 返回)
- Final response: 1 message
= 總共 12 messages

這是 LangGraph Supervisor 預設的行為，確保：
✅ 每次路由都有明確的記錄
✅ State 正確傳遞
✅ 工作流程可追蹤
✅ 錯誤處理完整
    """)

    print("\n" + "=" * 100)
    print("🔍 STATE 傳遞機制")
    print("=" * 100)
    print("""
State 如何在 agents 之間傳遞:

1. SupervisorState 定義:
   class SupervisorState(MessagesState):
       file_content: Optional[str] = None

2. read_file_agent 讀檔後:
   return {"file_content": content}  # 更新 state.file_content

3. Supervisor 維護 state:
   - 所有 agents 共享同一個 SupervisorState
   - read_file_agent 的輸出會更新 state.file_content

4. datcom_tool_agent 讀取:
   - Agent prompt 提示: "Check state.file_content"
   - LLM 看到 state.file_content 有內容
   - 使用 file_content 的資料來產生 DATCOM 檔案

關鍵設定:
✅ supervisor_agent/agent.py:
   supervisor = create_supervisor(
       agents=[...],
       state_schema=SupervisorState  # 所有 agents 共享此 state
   )

✅ datcom_tool_agent/agent.py:
   datcom_tool_agent = create_react_agent(
       state_schema=SupervisorState  # 必須使用相同的 state schema
   )
    """)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "can you read the file then write it to datcom file"

    analyze_workflow(query)
