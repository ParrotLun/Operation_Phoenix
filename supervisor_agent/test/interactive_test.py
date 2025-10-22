"""
Interactive test script for supervisor multi-agent system
允許使用者即時輸入問題並查看 agent 回應
"""
from supervisor_agent.agent import app
import sys
import time
import os


def print_banner():
    """印出歡迎訊息"""
    print("\n" + "=" * 80)
    print("🤖 Supervisor Multi-Agent Interactive Test")
    print("=" * 80)
    print("\n可用功能：")
    print("  📂 read_file_agent: 讀取 msg.txt 文件")
    print("  🔧 tool_agent: 取得時間、計算、反轉字串")
    print("  ✈️  datcom_tool_agent: 產生 DATCOM 輸入檔案 (for005.dat)")
    print("\n範例問題：")
    print("  - 請讀取 msg.txt")
    print("  - What's the current time?")
    print("  - Calculate 123 * 456")
    print("  - 請讀取 msg.txt 並產生 DATCOM 檔案")
    print("  - Generate DATCOM input file for PC-9")
    print("\n輸入 'quit', 'exit', 或 'q' 離開")
    print("=" * 80 + "\n")


def format_response(result, verbose=False, elapsed_time=None):
    """格式化並印出回應，包含診斷資訊"""

    # 顯示診斷資訊
    print("\n" + "─" * 80)
    print("📊 診斷資訊:")
    print("─" * 80)
    print(f"  Messages 數量: {len(result.get('messages', []))}")

    if elapsed_time:
        print(f"  執行時間: {elapsed_time:.2f} 秒")

    # 檢查 file_content
    if 'file_content' in result and result['file_content']:
        print(f"  file_content: {len(result['file_content'])} 字元")

    # 檢查是否產生 DATCOM 檔案
    datcom_file = "datcom_tool_agent/output/for005.dat"
    if os.path.exists(datcom_file):
        mtime = os.path.getmtime(datcom_file)
        age = time.time() - mtime
        if age < 10:  # 10 秒內修改
            file_size = os.path.getsize(datcom_file)
            print(f"  ✅ DATCOM 檔案已產生: {datcom_file} ({file_size} bytes)")

    # 詳細模式：顯示所有 messages
    if verbose and result.get("messages"):
        print("\n  📝 Message 流程:")
        for i, msg in enumerate(result["messages"], 1):
            msg_type = type(msg).__name__
            agent_name = getattr(msg, 'name', 'N/A')
            print(f"    {i}. {msg_type:20s} from: {agent_name}")

    # 顯示最終回應
    if result.get("messages"):
        final_message = result["messages"][-1]
        print("\n" + "─" * 80)
        print("🤖 Response:")
        print("─" * 80)

        # 檢查 content 是否為空
        if hasattr(final_message, 'content') and final_message.content:
            print(final_message.content)
        else:
            print("⚠️  Supervisor 沒有產生最終回應")
            print("ℹ️  可能原因：工作流程未完成或只執行了部分步驟")
            print("ℹ️  建議：查看上方的 Message 流程了解詳情")

        print("─" * 80 + "\n")
    else:
        print("\n⚠️  No response received\n")


def interactive_loop():
    """主要互動迴圈"""
    print_banner()

    # 詢問是否啟用詳細模式
    verbose_input = input("是否啟用詳細模式? (y/n, 預設 n): ").strip().lower()
    verbose = verbose_input in ['y', 'yes']

    if verbose:
        print("✅ 詳細模式已啟用（將顯示所有 messages）\n")
    else:
        print("ℹ️  標準模式（如需詳細資訊，請重新啟動並選擇 'y'）\n")

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
            start_time = time.time()

            result = app.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            elapsed = time.time() - start_time

            # 格式化並印出回應
            format_response(result, verbose=verbose, elapsed_time=elapsed)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()


def single_query_mode(query, verbose=False):
    """單次查詢模式（用於命令列參數）"""
    print("\n" + "=" * 80)
    print("🤖 Supervisor Multi-Agent Single Query Mode")
    print("=" * 80)
    print(f"\n👤 Query: {query}\n")
    print("⏳ Processing...\n")

    try:
        start_time = time.time()

        result = app.invoke({
            "messages": [{"role": "user", "content": query}]
        })

        elapsed = time.time() - start_time

        format_response(result, verbose=verbose, elapsed_time=elapsed)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 檢查是否有命令列參數
    if len(sys.argv) > 1:
        # 檢查是否有 --verbose 或 -v 旗標
        verbose = '--verbose' in sys.argv or '-v' in sys.argv

        # 過濾掉旗標，取得實際查詢
        query_parts = [arg for arg in sys.argv[1:] if arg not in ['--verbose', '-v']]

        if query_parts:
            # 單次查詢模式
            query = " ".join(query_parts)
            single_query_mode(query, verbose=verbose)
        else:
            print("❌ 錯誤: 請提供查詢內容")
            print("用法: python3 -m supervisor_agent.test.interactive_test [--verbose|-v] <query>")
            print("範例: python3 -m supervisor_agent.test.interactive_test --verbose '請讀取 msg.txt 並產生 DATCOM 檔案'")
    else:
        # 互動模式
        interactive_loop()
