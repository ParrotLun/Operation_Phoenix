"""
Interactive test script for supervisor multi-agent system
允許使用者即時輸入問題並查看 agent 回應
"""
from supervisor_agent.agent import app
import sys


def print_banner():
    """印出歡迎訊息"""
    print("\n" + "=" * 80)
    print("🤖 Supervisor Multi-Agent Interactive Test")
    print("=" * 80)
    print("\n可用功能：")
    print("  📂 read_file_agent: 讀取 msg.txt 文件")
    print("  🔧 tool_agent: 取得時間、計算、反轉字串")
    print("\n範例問題：")
    print("  - 請讀取 msg.txt")
    print("  - What's the current time?")
    print("  - Calculate 123 * 456")
    print("  - Reverse the string 'hello world'")
    print("\n輸入 'quit', 'exit', 或 'q' 離開")
    print("=" * 80 + "\n")


def format_response(result):
    """格式化並印出回應"""
    if result.get("messages"):
        final_message = result["messages"][-1]
        print("\n" + "─" * 80)
        print("🤖 Response:")
        print("─" * 80)
        print(final_message.content)
        print("─" * 80 + "\n")
    else:
        print("\n⚠️  No response received\n")


def interactive_loop():
    """主要互動迴圈"""
    print_banner()

    while True:
        try:
            # 取得使用者輸入
            user_input = input("👤 You: ").strip()

            # 檢查是否要離開
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break

            # 檢查是否為空輸入
            if not user_input:
                print("⚠️  Please enter a question\n")
                continue

            # 呼叫 supervisor agent
            print("\n⏳ Processing...")
            result = app.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            # 格式化並印出回應
            format_response(result)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()


def single_query_mode(query):
    """單次查詢模式（用於命令列參數）"""
    print(f"\n👤 Query: {query}\n")
    print("⏳ Processing...\n")

    try:
        result = app.invoke({
            "messages": [{"role": "user", "content": query}]
        })
        format_response(result)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 檢查是否有命令列參數
    if len(sys.argv) > 1:
        # 單次查詢模式
        query = " ".join(sys.argv[1:])
        single_query_mode(query)
    else:
        # 互動模式
        interactive_loop()
