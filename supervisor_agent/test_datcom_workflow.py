"""
Test script for end-to-end workflow:
read_file_agent → datcom_tool_agent via supervisor
"""
from supervisor_agent.agent import app

def test_read_and_generate_datcom():
    """
    Test the complete workflow:
    1. User asks to read msg.txt and generate DATCOM
    2. Supervisor routes to read_file_agent first
    3. read_file_agent stores content in state.file_content
    4. Supervisor routes to datcom_tool_agent
    5. datcom_tool_agent reads state.file_content and generates for005.dat
    """
    print("=" * 80)
    print("🚀 Testing Multi-Agent Workflow: Read File → Generate DATCOM")
    print("=" * 80)

    user_request = "請讀取 msg.txt 文件並根據內容產生 DATCOM 檔案"

    print(f"\n📝 User Request:\n{user_request}\n")
    print("=" * 80)
    print("🔄 Running workflow...\n")

    result = app.invoke({
        "messages": [{"role": "user", "content": user_request}]
    })

    print("=" * 80)
    print("📊 Workflow Results:")
    print("=" * 80)

    # Print all messages
    for i, msg in enumerate(result["messages"], 1):
        if hasattr(msg, "content") and msg.content:
            msg_type = msg.__class__.__name__
            agent_name = getattr(msg, "name", "unknown")
            print(f"\n[Message {i}] {msg_type}")
            if agent_name and agent_name != "unknown":
                print(f"From: {agent_name}")
            print("-" * 40)
            print(msg.content)

    # Print state
    print("\n" + "=" * 80)
    print("📋 Final State:")
    print("=" * 80)

    if "file_content" in result:
        print(f"\n✅ file_content exists: {len(result['file_content'])} characters")
        print("First 200 characters:")
        print(result["file_content"][:200] + "...")
    else:
        print("\n⚠️  No file_content in state")

    print("\n" + "=" * 80)
    print("✅ Test completed!")
    print("=" * 80)

    # Check if output file was created
    import os
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "datcom_tool_agent", "output", "for005.dat"
    )

    if os.path.exists(output_path):
        print(f"\n🎉 SUCCESS! DATCOM file created at: {output_path}")
        print("\n📄 File preview:")
        with open(output_path, 'r') as f:
            lines = f.readlines()[:5]
            for line in lines:
                print(f"  {line.rstrip()}")
    else:
        print(f"\n⚠️  Output file not found at: {output_path}")


def test_direct_datcom_generation():
    """
    Test direct DATCOM generation (without reading file first)
    """
    print("\n\n")
    print("=" * 80)
    print("🚀 Testing Direct DATCOM Generation (no file reading)")
    print("=" * 80)

    user_request = """請產生 PC-9 的 DATCOM 檔案：

飛行條件:
- 攻角: 1.0, 2.0, 3.0, 4.0, 5.0, 6.0 度 (共6個)
- 馬赫數: 0.5489 (1組)
- 高度: 10000 ft (1組)
- 重量: 5180.0

合成參數:
XCG=11.3907, ZCG=0.0, XW=11.1070, ZW=-1.6339, ALIW=1.0
XH=29.1178, ZH=0.7940, ALIH=-2.0, XV=26.4633, ZV=1.3615

機身: NX=9
X= 0.0, 2.2428, 2.5098, 8.4711, 14.4619, 16.8209, 20.4396, 29.7310, 31.4337
R= 0.0, 0.7710, 0.8990, 1.6010, 1.6010, 1.6010, 1.4797, 0.5906, 0.0
ZU= 0.0, 0.8629, 0.9613, 1.7028, 3.6385, 3.5531, 2.4508, 1.3519, 1.3451
ZL= 0.0, -0.7546, -1.3123, -1.9727, -1.9783, -1.7487, -1.3615, -0.2625, 0.7054
ITYPE=2, METHOD=1

主翼: NACA 6-63-415
CHRDTP=3.7402, SSPN=16.6076, SSPNE=15.0131, CHRDR=6.2336
SAVSI=4.0, CHSTAT=0.0, TWISTA=-2.0, DHDADI=7.0, TYPE=1

水平尾翼: NACA 4-0012
CHRDTP=2.1325, SSPN=6.0105, SSPNE=6.0105, CHRDR=4.2651
SAVSI=13.0, CHSTAT=0.0, TWISTA=-2.0, DHDADI=7.0, TYPE=1

垂直尾翼: NACA 4-0012
CHRDTP=2.3734, SSPN=5.3642, SSPNE=5.3642, CHRDR=4.6916
SAVSI=12.2, CHSTAT=0.0, TYPE=1
"""

    print(f"\n📝 User Request (with inline data)")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": user_request}]
    })

    print("\n📊 Final Response:")
    print("=" * 80)
    final_msg = result["messages"][-1]
    print(final_msg.content)

    print("\n✅ Test completed!")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "SUPERVISOR MULTI-AGENT DATCOM WORKFLOW TEST" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")

    # Test 1: Read file then generate DATCOM
    test_read_and_generate_datcom()

    # Test 2: Direct generation (optional - comment out if LLM is slow)
    # test_direct_datcom_generation()
