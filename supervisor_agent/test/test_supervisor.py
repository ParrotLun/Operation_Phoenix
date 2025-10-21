"""
Test script for supervisor multi-agent system
"""
from supervisor_agent.agent import app


def test_read_file():
    """Test routing to read_file_agent"""
    print("\n" + "=" * 80)
    print("TEST 1: Read File Request")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "請讀取 msg.txt 文件"}]
    })

    print("\n📋 Final Response:")
    if result.get("messages"):
        final_message = result["messages"][-1]
        print(final_message.content)
    else:
        print("No response received")


def test_tool_agent():
    """Test routing to tool_agent"""
    print("\n" + "=" * 80)
    print("TEST 2: Tool Agent - Current Time")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "What's the current time?"}]
    })

    print("\n📋 Final Response:")
    if result.get("messages"):
        final_message = result["messages"][-1]
        print(final_message.content)
    else:
        print("No response received")


def test_calculation():
    """Test tool_agent calculation"""
    print("\n" + "=" * 80)
    print("TEST 3: Tool Agent - Calculation")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": "Calculate 123 * 456"}]
    })

    print("\n📋 Final Response:")
    if result.get("messages"):
        final_message = result["messages"][-1]
        print(final_message.content)
    else:
        print("No response received")


if __name__ == "__main__":
    print("\n🚀 Starting Supervisor Multi-Agent System Tests\n")

    try:
        test_read_file()
        test_tool_agent()
        test_calculation()

        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
