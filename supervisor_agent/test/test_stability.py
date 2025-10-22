"""
穩定性測試 - 測試不同的請求方式
驗證多步驟工作流程的穩定性
"""
from supervisor_agent.agent import app


def test_query(query: str, expected_agents: int = 2):
    """測試單一查詢"""
    print(f"\n{'='*80}")
    print(f"測試查詢: {query}")
    print(f"{'='*80}")

    result = app.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    messages = result["messages"]
    total_messages = len(messages)

    # 分析 agent 路由
    agent_transfers = []
    for msg in messages:
        if hasattr(msg, 'name') and 'transfer_to_' in str(msg.name):
            agent_name = msg.name.replace('transfer_to_', '')
            agent_transfers.append(agent_name)

    # 檢查最終回應
    final_msg = messages[-1]
    has_response = hasattr(final_msg, 'content') and bool(final_msg.content)

    # 顯示結果
    print(f"\n📊 結果:")
    print(f"  Messages: {total_messages}")
    print(f"  Agent 執行順序: {' → '.join(agent_transfers) if agent_transfers else 'None'}")
    print(f"  執行的 agents 數量: {len(agent_transfers)}")
    print(f"  最終回應: {'✅ 有' if has_response else '❌ 無'}")

    # 判定成功/失敗
    if len(agent_transfers) == expected_agents and has_response:
        print(f"\n✅ 測試通過 - 成功執行 {expected_agents} 個 agents")
        return True
    else:
        print(f"\n❌ 測試失敗 - 預期 {expected_agents} 個 agents，實際 {len(agent_transfers)}")
        if not has_response:
            print(f"   且最終回應為空")
        return False


def main():
    """主測試函數"""
    print("\n" + "="*80)
    print("🧪 Supervisor Multi-Agent Stability Test")
    print("="*80)
    print("\n測試不同的請求方式，驗證多步驟工作流程的穩定性")

    test_cases = [
        # (query, expected_agents, description)
        ("請讀取 msg.txt 並產生 DATCOM 檔案", 2, "中文 - 明確的兩步驟請求"),
        ("Read msg.txt and generate a DATCOM input file", 2, "英文 - 明確的兩步驟請求"),
        ("can you read the file then write it to datcom file", 2, "英文 - 非正式的兩步驟請求"),
        ("讀取檔案然後產生 DATCOM", 2, "中文 - 簡短的兩步驟請求"),
        ("請讀取 msg.txt", 1, "中文 - 單步驟請求（只讀檔）"),
    ]

    results = []

    for i, (query, expected, description) in enumerate(test_cases, 1):
        print(f"\n\n{'#'*80}")
        print(f"# 測試案例 {i}/{len(test_cases)}: {description}")
        print(f"{'#'*80}")

        success = test_query(query, expected_agents=expected)
        results.append({
            "query": query,
            "expected": expected,
            "success": success,
            "description": description
        })

    # 總結
    print(f"\n\n{'='*80}")
    print("📋 測試總結")
    print(f"{'='*80}\n")

    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed

    for i, r in enumerate(results, 1):
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        print(f"{i}. {status} - {r['description']}")
        print(f"   Query: \"{r['query']}\"")
        print(f"   Expected agents: {r['expected']}")
        print()

    print(f"{'='*80}")
    print(f"總計: {total} 個測試")
    print(f"✅ 通過: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"成功率: {passed/total*100:.1f}%")
    print(f"{'='*80}\n")

    if failed > 0:
        print("⚠️  有測試失敗！")
        print("\n建議:")
        print("1. 使用中文請求（更穩定）")
        print("2. 使用明確的動詞（'讀取'、'產生'、'generate'）")
        print("3. 如果英文請求不穩定，檢查 supervisor prompt 是否需要更多英文範例")
    else:
        print("🎉 所有測試通過！系統運作穩定。")


if __name__ == "__main__":
    main()
