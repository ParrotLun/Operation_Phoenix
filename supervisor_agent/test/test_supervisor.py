"""
Test script for basic supervisor functionality
Tests the three agents: read_file_agent, tool_agent, datcom_tool_agent
"""
from supervisor_agent.agent import app


def test_read_file():
    """Test 1: Read file using read_file_agent"""
    print("\n" + "=" * 80)
    print("TEST 1: Read File Request")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "請讀取 msg.txt 文件"}]
    })

    print(f"\n✅ Test 1 completed")
    print("Final response:")
    final_msg = result["messages"][-1]
    print(final_msg.content[:200] + "...")


def test_tool_agent_time():
    """Test 2: Tool agent - current time"""
    print("\n" + "=" * 80)
    print("TEST 2: Tool Agent - Current Time")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "What's the current time?"}]
    })

    print(f"\n✅ Test 2 completed")
    print("Final response:")
    final_msg = result["messages"][-1]
    print(final_msg.content)


def test_tool_agent_calculation():
    """Test 3: Tool agent - calculation"""
    print("\n" + "=" * 80)
    print("TEST 3: Tool Agent - Calculation")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "Calculate 123 * 456"}]
    })

    print(f"\n✅ Test 3 completed")
    print("Final response:")
    final_msg = result["messages"][-1]
    print(final_msg.content)


def test_datcom_workflow():
    """Test 4: Multi-agent workflow - read file and generate DATCOM"""
    print("\n" + "=" * 80)
    print("TEST 4: Multi-Agent Workflow - Read File → Generate DATCOM")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "請讀取 msg.txt 文件並根據內容產生 DATCOM 檔案"}]
    })

    print(f"\n✅ Test 4 completed")
    print(f"Total messages: {len(result['messages'])}")
    print("Final response:")
    final_msg = result["messages"][-1]
    print(final_msg.content)

    # Check if file_content exists in state
    if "file_content" in result:
        print(f"\n✅ file_content exists: {len(result['file_content'])} characters")
    else:
        print("\n⚠️  No file_content in state")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SUPERVISOR AGENT TEST SUITE" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")

    # Run all tests
    try:
        test_read_file()
        test_tool_agent_time()
        test_tool_agent_calculation()
        test_datcom_workflow()

        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
