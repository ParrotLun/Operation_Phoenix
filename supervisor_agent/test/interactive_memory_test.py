"""
Interactive test script with MEMORY support
測試對話記憶和連續性功能
"""
from supervisor_agent.agent import app
from supervisor_agent.utils.memory_manager import ConversationMemoryManager, SessionManager
from langchain_core.messages import HumanMessage
import sys
import time
import os
import json


def print_banner():
    """印出歡迎訊息"""
    print("\n" + "=" * 80)
    print("🤖 Supervisor Multi-Agent Interactive Test (WITH MEMORY 🧠)")
    print("=" * 80)
    print("\n新功能：")
    print("  🧠 對話記憶：會記住之前的對話內容")
    print("  🔗 Session 管理：追蹤對話連續性")
    print("  💾 State 追蹤：顯示 latest_datcom 和 parsed_file_data")
    print("\n可用功能：")
    print("  📂 read_file_agent: 讀取 msg.txt 文件")
    print("  ✈️  datcom_tool_agent: 產生 DATCOM 輸入檔案 (for005.dat)")
    print("\n範例問題（測試記憶）：")
    print("  1️⃣  請讀取 msg.txt")
    print("  2️⃣  剛才讀取的檔案有什麼內容？（會使用記憶）")
    print("  3️⃣  請產生 DATCOM 檔案")
    print("  4️⃣  剛才產生的 DATCOM 檔案路徑是什麼？（會使用記憶）")
    print("\n特殊命令：")
    print("  'memory' - 顯示目前的記憶狀態")
    print("  'state' - 顯示目前的 state 內容")
    print("  'clear' - 清除記憶，開始新對話")
    print("  'quit', 'exit', 'q' - 離開")
    print("=" * 80 + "\n")


def format_state_info(state):
    """格式化並顯示 state 資訊"""
    print("\n" + "─" * 80)
    print("📦 State 資訊:")
    print("─" * 80)

    # 顯示 messages 數量
    msg_count = len(state.get('messages', []))
    print(f"  💬 Messages: {msg_count} 條")

    # 顯示 conversation_id
    conv_id = state.get('conversation_id', 'None')
    print(f"  🔑 Session ID: {conv_id}")

    # 顯示 file_content
    file_content = state.get('file_content')
    if file_content:
        print(f"  📄 File Content: {len(file_content)} 字元")
    else:
        print(f"  📄 File Content: None")

    # 顯示 parsed_file_data
    parsed = state.get('parsed_file_data')
    if parsed:
        print(f"  🔍 Parsed File Data:")
        print(f"      - File Type: {parsed.get('file_type', 'unknown')}")
        print(f"      - Has DATCOM: {parsed.get('has_datcom_data', False)}")
        print(f"      - Key Values: {len(parsed.get('key_values', {}))} 個")
    else:
        print(f"  🔍 Parsed File Data: None")

    # 顯示 latest_datcom
    datcom = state.get('latest_datcom')
    if datcom:
        print(f"  ✈️  Latest DATCOM:")
        print(f"      - Case ID: {datcom.get('case_id', 'N/A')}")
        print(f"      - Output: {datcom.get('output_path', 'N/A')}")
        print(f"      - Generated: {datcom.get('generated_at', 'N/A')}")
    else:
        print(f"  ✈️  Latest DATCOM: None")

    # 顯示 conversation_history_summary
    summary = state.get('conversation_history_summary')
    if summary:
        print(f"  📝 History Summary: {len(summary)} 字元")
        print(f"      {summary[:100]}..." if len(summary) > 100 else f"      {summary}")
    else:
        print(f"  📝 History Summary: None")

    print("─" * 80)


def format_memory_info(memory_manager, state):
    """顯示記憶管理資訊"""
    print("\n" + "─" * 80)
    print("🧠 記憶管理資訊:")
    print("─" * 80)

    messages = state.get('messages', [])
    print(f"  總訊息數: {len(messages)}")
    print(f"  保留最近: {memory_manager.max_recent_messages} 條")
    print(f"  壓縮閾值: {memory_manager.compression_threshold} 條")

    if len(messages) > memory_manager.compression_threshold:
        print(f"  ✅ 會進行壓縮（訊息數 > 閾值）")
        recent, summary = memory_manager.compress_messages(messages)
        print(f"  壓縮後訊息數: {len(recent)}")
        print(f"  摘要長度: {len(summary)} 字元")

        # 估算 token 節省
        original_tokens = len(messages) * 100  # 粗略估計
        compressed_tokens = len(recent) * 100 + len(summary)
        saved_percent = (1 - compressed_tokens / original_tokens) * 100
        print(f"  估計 token 節省: ~{saved_percent:.1f}%")
    else:
        print(f"  ⏸️  尚未壓縮（訊息數 ≤ 閾值）")

    # 顯示關鍵資訊
    key_info = memory_manager.extract_key_info_from_messages(messages)
    print(f"\n  關鍵資訊:")
    for key, value in key_info.items():
        print(f"    - {key}: {value}")

    print("─" * 80)


def format_response(result, verbose=False, elapsed_time=None):
    """格式化並印出回應"""
    print("\n" + "─" * 80)
    print("📊 執行資訊:")
    print("─" * 80)

    if elapsed_time:
        print(f"  ⏱️  執行時間: {elapsed_time:.2f} 秒")

    # 檢查是否產生 DATCOM 檔案
    datcom_file = "datcom_tool_agent/output/for005.dat"
    if os.path.exists(datcom_file):
        mtime = os.path.getmtime(datcom_file)
        age = time.time() - mtime
        if age < 10:  # 10 秒內修改
            file_size = os.path.getsize(datcom_file)
            print(f"  ✅ DATCOM 檔案已產生: {file_size} bytes")

    # 顯示最終回應
    if result.get("messages"):
        final_message = result["messages"][-1]
        print("\n" + "─" * 80)
        print("🤖 回應:")
        print("─" * 80)

        if hasattr(final_message, 'content') and final_message.content:
            print(final_message.content)
        else:
            print("⚠️  沒有最終回應")

        print("─" * 80)


def interactive_loop():
    """主要互動迴圈（支援記憶）"""
    print_banner()

    # 初始化記憶管理器
    memory_manager = ConversationMemoryManager(
        max_recent_messages=4,
        compression_threshold=8  # 超過 8 條訊息就開始壓縮
    )

    # 產生 session ID
    session_id = SessionManager.generate_session_id()
    print(f"🔑 Session ID: {session_id}\n")

    # 初始化 state（空的）
    current_state = None

    # 詢問是否啟用詳細模式
    verbose_input = input("是否啟用詳細模式? (y/n, 預設 n): ").strip().lower()
    verbose = verbose_input in ['y', 'yes']

    if verbose:
        print("✅ 詳細模式已啟用\n")
    else:
        print("ℹ️  標準模式\n")

    turn_count = 0

    while True:
        try:
            # 取得使用者輸入
            user_input = input("👤 You: ").strip()

            # 檢查特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break

            if user_input.lower() == 'memory':
                if current_state:
                    format_memory_info(memory_manager, current_state)
                else:
                    print("\n⚠️  尚無記憶（還沒有對話）\n")
                continue

            if user_input.lower() == 'state':
                if current_state:
                    format_state_info(current_state)
                else:
                    print("\n⚠️  尚無 state（還沒有對話）\n")
                continue

            if user_input.lower() == 'clear':
                current_state = None
                session_id = SessionManager.generate_session_id()
                turn_count = 0
                print(f"\n🔄 已清除記憶，開始新對話")
                print(f"🔑 新 Session ID: {session_id}\n")
                continue

            if not user_input:
                print("⚠️  請輸入問題\n")
                continue

            # 準備輸入 state
            turn_count += 1
            print(f"\n⏳ 處理中... (第 {turn_count} 輪對話)")
            start_time = time.time()

            if current_state is None:
                # 第一次對話
                input_state = {
                    "messages": [HumanMessage(content=user_input)],
                    "conversation_id": session_id
                }
                print("  🆕 第一次對話（無記憶）")
            else:
                # 連續對話 - 使用記憶管理
                messages = current_state.get("messages", [])

                # 準備優化的 context
                optimized_messages = memory_manager.prepare_context_for_llm(current_state)

                # 加入新的使用者訊息
                optimized_messages.append(HumanMessage(content=user_input))

                # 建立輸入 state，保留重要欄位
                input_state = {
                    "messages": optimized_messages,
                    "conversation_id": session_id,
                    "file_content": current_state.get("file_content"),
                    "parsed_file_data": current_state.get("parsed_file_data"),
                    "latest_datcom": current_state.get("latest_datcom"),
                }

                # 顯示記憶壓縮資訊
                if len(messages) > memory_manager.compression_threshold:
                    saved = len(messages) - len(optimized_messages) + 1  # +1 因為還會加新訊息
                    print(f"  🧠 使用記憶壓縮（節省 {saved} 條訊息）")
                else:
                    print(f"  🧠 使用完整歷史（{len(messages)} 條訊息）")

            # 呼叫 supervisor agent
            result = app.invoke(input_state)

            elapsed = time.time() - start_time

            # 更新 current_state
            current_state = result

            # 顯示回應
            format_response(result, verbose=verbose, elapsed_time=elapsed)

            # 顯示 state 資訊（verbose 模式）
            if verbose:
                format_state_info(current_state)

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    interactive_loop()
