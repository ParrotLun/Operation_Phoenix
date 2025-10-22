# -*- coding: utf-8 -*-
import os
from pydantic import ValidationError

# 從 data_model.py 匯入我們定義好的資料模型
from datcom_tool_agent.data_model import (
    DatcomInput, FLTCON, SYNTHS, BODY,
    WGPLNF, HTPLNF, VTPLNF
)

# ==============================================================================
# DATCOM 檔案生成器
# 說明：這個類別負責將 Pydantic 物件轉換成 DATCOM 需要的文字格式。
# ==============================================================================

def _format_value_for_datcom(value):
    """輔助函式：將 Python 值格式化為 Fortran Namelist 格式

    格式規則：
    - 整數 → 一位小數 (例如 6 → 6.0)
    - 浮點數 → 最多四位小數，去除尾部零 (例如 0.5489 → 0.5489, 10000.0 → 10000.0)
    """
    if isinstance(value, list):
        # 列表中的每個數字都轉換為浮點數格式
        formatted_items = []
        for item in value:
            if isinstance(item, (int, float)):
                formatted_items.append(_format_single_number(item))
            else:
                formatted_items.append(str(item))
        return ",".join(formatted_items)
    if isinstance(value, (int, float)):
        return _format_single_number(value)
    return str(value)

def _format_single_number(num):
    """格式化單一數字：整數用一位小數，浮點數最多四位小數並去除尾部零"""
    # 檢查是否為整數值（即使是 float 類型）
    if isinstance(num, int) or (isinstance(num, float) and num == int(num)):
        return f"{float(num):.1f}"
    else:
        # 浮點數：最多四位小數，去除尾部零
        formatted = f"{num:.4f}".rstrip('0').rstrip('.')
        # 確保至少有一位小數
        if '.' not in formatted:
            formatted += '.0'
        return formatted

class DatcomGenerator:
    """接收一個 DatcomInput 物件，並產生格式化的 for005.dat 檔案"""

    def _write_namelist(self, file_handle, model, namelist_name: str, exclude_fields: set = None):
        """寫入一個標準的 NAMELIST 區塊（單行格式）"""
        if exclude_fields is None:
            exclude_fields = set()

        # 將 Pydantic 模型轉換為字典，並排除不需要的欄位
        data = model.model_dump(exclude=exclude_fields, exclude_none=True)
        if not data:
            return

        # 建立 key=value 對的列表
        pairs = []
        for key, value in data.items():
            pairs.append(f"{key.upper()}={_format_value_for_datcom(value)}")

        # 組合成單行：$NAMELIST key1=val1,key2=val2,...,keyN=valN$
        namelist_line = f"${namelist_name} {','.join(pairs)}$\n"
        file_handle.write(namelist_line)

    def generate_file(self, datcom_input: DatcomInput, case_id: str, filename: str = "for005.dat"):
        """產生完整的 for005.dat 檔案"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"CASEID {case_id}\n")

            # 依序寫入各個 Namelist 區塊
            self._write_namelist(f, datcom_input.flight_conditions, "FLTCON")
            self._write_namelist(f, datcom_input.synthesis, "SYNTHS")
            self._write_namelist(f, datcom_input.body, "BODY")

            # 處理翼型卡片 (需在對應的 Planform 卡片之前)
            f.write(f"NACA-W-{datcom_input.wing_planform.NACA_W}\n")
            self._write_namelist(f, datcom_input.wing_planform, "WGPLNF", exclude_fields={'NACA_W'})

            f.write(f"NACA-H-{datcom_input.horizontal_tail_planform.NACA_H}\n")
            self._write_namelist(f, datcom_input.horizontal_tail_planform, "HTPLNF", exclude_fields={'NACA_H'})

            f.write(f"NACA-V-{datcom_input.vertical_tail_planform.NACA_V}\n")
            self._write_namelist(f, datcom_input.vertical_tail_planform, "VTPLNF", exclude_fields={'NACA_V'})

            # 寫入結尾的指令
            f.write("DAMP\n")
            f.write("BUILD\n")

        print(f"✅ DATCOM 檔案 '{filename}' 已成功產生在 '{os.getcwd()}' 目錄下！")


# ==============================================================================
# 主程式執行區
# 說明：這是程式的進入點。您可以在這裡填寫飛機的參數。
# ==============================================================================

if __name__ == "__main__":
    try:
        # --- 步驟 1: 在此填寫您的飛機參數 ---
        # 根據您提供的範例資料來填充模型
        flight_conditions = FLTCON(
            NALPHA=6,
            ALSCHD=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            NMACH=1,
            MACH=[0.5489],
            NALT=1,
            ALT=[10000.0],
            WT=5180.0
        )

        synthesis = SYNTHS(
            XCG=11.3907, ZCG=0.0,
            XW=11.1070, ZW=-1.6339, ALIW=1.0,
            XH=29.1178, ZH=0.7940, ALIH=-2.0,
            XV=26.4633, ZV=1.3615
        )

        body = BODY(
            NX=9,
            X=[0.0, 2.2428, 2.5098, 8.4711, 14.4619, 16.8209, 20.4396, 2.97310e1, 3.14337e1],
            R=[0.0, 0.7710, 0.8990, 1.6010, 1.6010, 1.6010, 1.4797, 0.5906, 0.0000],
            ZU=[0.0, 0.8629, 0.9613, 1.7028, 3.6385, 3.5531, 2.4508, 1.3519, 1.3451],
            ZL=[0.0, -0.7546, -1.3123, -1.9727, -1.9783, -1.7487, -1.3615, -0.2625, 0.7054],
            ITYPE=2, METHOD=1
        )

        wing = WGPLNF(
            NACA_W="6-63-415",
            CHRDTP=3.7402, SSPN=16.6076, SSPNE=15.0131,
            CHRDR=6.2336, CHSTAT=0.0, SAVSI=4.0,
            TWISTA=-2.0, DHDADI=7.0, TYPE=1
        )

        h_tail = HTPLNF(
            NACA_H="4-0012",
            CHRDTP=2.1325, SSPN=6.0105, SSPNE=6.0105,
            CHRDR=4.2651, SAVSI=13.0, TWISTA=-2.0, DHDADI=7.0, CHSTAT=0.0, TYPE=1
        )
        
        v_tail = VTPLNF(
            NACA_V="4-0012",
            CHRDTP=2.3734, SSPN=5.3642, SSPNE=5.3642,
            CHRDR=4.6916, SAVSI=12.2, CHSTAT=0.0, TYPE=1
        )

        # --- 步驟 2: 將所有資料組合到一個 DatcomInput 物件中 ---
        pc9_input_data = DatcomInput(
            flight_conditions=flight_conditions,
            synthesis=synthesis,
            body=body,
            wing_planform=wing,
            horizontal_tail_planform=h_tail,
            vertical_tail_planform=v_tail,
        )

        # --- 步驟 3: 建立生成器並產生檔案 ---
        generator = DatcomGenerator()
        generator.generate_file(
            datcom_input=pc9_input_data,
            case_id="PC-9",
            filename="for005.dat"
        )

    except ValidationError as e:
        print("❌ 資料驗證失敗！請檢查您的輸入參數。")
        print(e)
