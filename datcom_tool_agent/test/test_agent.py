"""
Test script for datcom_tool_agent
Tests the LLM-driven parsing and file writing
"""
from datcom_tool_agent.agent import app

# Test with structured DATCOM-like text
test_input = """
請根據以下 PC-9 飛機數據產生 DATCOM 輸入檔：

## 飛行條件 (FLTCON)
- 攻角數量: 6
- 攻角值: 1.0, 2.0, 3.0, 4.0, 5.0, 6.0
- 馬赫數組數: 1
- 馬赫數: 0.5489
- 高度組數: 1
- 高度: 10000.0 ft
- 重量: 5180.0

## 合成參數 (SYNTHS)
- XCG=11.3907, ZCG=0.0
- XW=11.1070, ZW=-1.6339, ALIW=1.0
- XH=29.1178, ZH=0.7940, ALIH=-2.0
- XV=26.4633, ZV=1.3615

## 機身外形 (BODY)
- NX=9
- X= 0.0, 2.2428, 2.5098, 8.4711, 14.4619, 16.8209, 20.4396, 29.7310, 31.4337
- R= 0.0, 0.7710, 0.8990, 1.6010, 1.6010, 1.6010, 1.4797, 0.5906, 0.0000
- ZU= 0.0, 0.8629, 0.9613, 1.7028, 3.6385, 3.5531, 2.4508, 1.3519, 1.3451
- ZL= 0.0, -0.7546, -1.3123, -1.9727, -1.9783, -1.7487, -1.3615, -0.2625, 0.7054
- ITYPE=2, METHOD=1

## 主翼 (WGPLNF)
- NACA: 6-63-415
- CHRDTP=3.7402, SSPN=16.6076, SSPNE=15.0131
- CHRDR=6.2336, SAVSI=4.0, CHSTAT=0.0
- TWISTA=-2.0, DHDADI=7.0, TYPE=1

## 水平尾翼 (HTPLNF)
- NACA: 4-0012
- CHRDTP=2.1325, SSPN=6.0105, SSPNE=6.0105
- CHRDR=4.2651, SAVSI=13.0, CHSTAT=0.0
- TWISTA=-2.0, DHDADI=7.0, TYPE=1

## 垂直尾翼 (VTPLNF)
- NACA: 4-0012
- CHRDTP=2.3734, SSPN=5.3642, SSPNE=5.3642
- CHRDR=4.6916, SAVSI=12.2, CHSTAT=0.0
- TYPE=1
"""

if __name__ == "__main__":
    print("🚀 Testing DATCOM Tool Agent...")
    print("=" * 80)

    result = app.invoke({
        "messages": [{"role": "user", "content": test_input}]
    })

    print("\n" + "=" * 80)
    print("📝 Agent Response:")
    print("=" * 80)

    # Print all messages
    for msg in result["messages"]:
        if hasattr(msg, "content") and msg.content:
            print(f"\n[{msg.__class__.__name__}]")
            print(msg.content)

    print("\n" + "=" * 80)
    print("✅ Test completed!")
