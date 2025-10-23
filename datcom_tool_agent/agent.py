"""
DATCOM Tool Agent - LLM-driven parsing + simple file writing tool
職責：解析文字內容 → 填充 Pydantic models → 呼叫 tool 寫檔
"""
import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

# 導入 Pydantic models 和 generator
from datcom_tool_agent.data_model import (
    DatcomInput, FLTCON, SYNTHS, BODY,
    WGPLNF, HTPLNF, VTPLNF
)
from datcom_tool_agent.run_generator import DatcomGenerator

# Import SupervisorState for state sharing
from supervisor_agent.utils.state import SupervisorState

# Load environment from read_file_agent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "read_file_agent", ".env")
load_dotenv(env_path)


@tool
def write_datcom_file(
    # Flight Conditions
    nalpha: int,
    alschd: str,  # comma-separated values
    nmach: int,
    mach: str,
    nalt: int,
    alt: str,
    wt: float,
    # Synthesis
    xcg: float,
    zcg: float,
    xw: float,
    zw: float,
    aliw: float,
    xh: float,
    zh: float,
    alih: float,
    xv: float,
    zv: float,
    # Body
    nx: int,
    x_coords: str,
    r_coords: str,
    zu_coords: str,
    zl_coords: str,
    itype: int,
    method: int,
    # Wing Planform
    wing_naca: str,
    wing_chrdtp: float,
    wing_sspn: float,
    wing_sspne: float,
    wing_chrdr: float,
    wing_savsi: float,
    wing_chstat: float,
    wing_twista: float,
    wing_dhdadi: float,
    wing_type: int,
    # Horizontal Tail
    htail_naca: str,
    htail_chrdtp: float,
    htail_sspn: float,
    htail_sspne: float,
    htail_chrdr: float,
    htail_savsi: float,
    htail_chstat: float,
    htail_twista: float,
    htail_dhdadi: float,
    htail_type: int,
    # Vertical Tail
    vtail_naca: str,
    vtail_chrdtp: float,
    vtail_sspn: float,
    vtail_sspne: float,
    vtail_chrdr: float,
    vtail_savsi: float,
    vtail_chstat: float,
    vtail_type: int,
    # Output config
    case_id: str = "PC-9"
) -> str:
    """
    Write DATCOM input file (for005.dat) to output directory.

    This tool takes all required DATCOM parameters and generates a properly formatted
    for005.dat file in the datcom_tool_agent/output/ directory.

    Args:
        Flight Conditions (FLTCON):
            nalpha: Number of angles of attack (max 20)
            alschd: Angles of attack values, comma-separated (e.g., "1.0,2.0,3.0")
            nmach: Number of mach numbers (max 20)
            mach: Mach number values, comma-separated
            nalt: Number of altitudes (max 20)
            alt: Altitude values in feet, comma-separated
            wt: Vehicle weight

        Synthesis (SYNTHS):
            xcg, zcg: CG location (x, z)
            xw, zw: Wing apex location (x, z)
            aliw: Wing incidence angle
            xh, zh: Horizontal tail apex location (x, z)
            alih: Horizontal tail incidence angle
            xv, zv: Vertical tail apex location (x, z)

        Body (BODY):
            nx: Number of body stations (max 20)
            x_coords: X coordinates, comma-separated
            r_coords: Radius values, comma-separated
            zu_coords: Upper Z coordinates, comma-separated
            zl_coords: Lower Z coordinates, comma-separated
            itype: 1=straight wing, 2=swept wing
            method: Calculation method (1=Default, 2=Jorgensen)

        Wing Planform (WGPLNF):
            wing_naca: NACA airfoil (e.g., "6-63-415")
            wing_chrdtp: Tip chord
            wing_sspn: Semi-span theoretical
            wing_sspne: Semi-span exposed
            wing_chrdr: Root chord
            wing_savsi: Sweep angle
            wing_chstat: Reference chord station
            wing_twista: Twist angle
            wing_dhdadi: Dihedral angle
            wing_type: 1=straight tapered planform

        Horizontal Tail (HTPLNF):
            htail_naca: NACA airfoil (e.g., "4-0012")
            htail_chrdtp: Tip chord
            htail_sspn: Semi-span theoretical
            htail_sspne: Semi-span exposed
            htail_chrdr: Root chord
            htail_savsi: Sweep angle
            htail_chstat: Reference chord station
            htail_twista: Twist angle
            htail_dhdadi: Dihedral angle
            htail_type: 1=straight tapered planform

        Vertical Tail (VTPLNF):
            vtail_naca: NACA airfoil (e.g., "4-0012")
            vtail_chrdtp: Tip chord
            vtail_sspn: Semi-span theoretical
            vtail_sspne: Semi-span exposed
            vtail_chrdr: Root chord
            vtail_savsi: Sweep angle
            vtail_chstat: Reference chord station
            vtail_type: 1=straight tapered planform

        case_id: Case identifier (default: "PC-9")

    Returns:
        Success message with output file path
    """
    try:
        # Parse comma-separated strings to lists
        def parse_floats(s: str):
            return [float(x.strip()) for x in s.split(',')]

        # Build Pydantic models
        flight_conditions = FLTCON(
            NALPHA=nalpha,
            ALSCHD=parse_floats(alschd),
            NMACH=nmach,
            MACH=parse_floats(mach),
            NALT=nalt,
            ALT=parse_floats(alt),
            WT=wt
        )

        synthesis = SYNTHS(
            XCG=xcg, ZCG=zcg,
            XW=xw, ZW=zw, ALIW=aliw,
            XH=xh, ZH=zh, ALIH=alih,
            XV=xv, ZV=zv
        )

        body = BODY(
            NX=nx,
            X=parse_floats(x_coords),
            R=parse_floats(r_coords),
            ZU=parse_floats(zu_coords),
            ZL=parse_floats(zl_coords),
            ITYPE=itype,
            METHOD=method
        )

        wing = WGPLNF(
            NACA_W=wing_naca,
            CHRDTP=wing_chrdtp,
            SSPN=wing_sspn,
            SSPNE=wing_sspne,
            CHRDR=wing_chrdr,
            SAVSI=wing_savsi,
            CHSTAT=wing_chstat,
            TWISTA=wing_twista,
            DHDADI=wing_dhdadi,
            TYPE=wing_type
        )

        htail = HTPLNF(
            NACA_H=htail_naca,
            CHRDTP=htail_chrdtp,
            SSPN=htail_sspn,
            SSPNE=htail_sspne,
            CHRDR=htail_chrdr,
            SAVSI=htail_savsi,
            CHSTAT=htail_chstat,
            TWISTA=htail_twista,
            DHDADI=htail_dhdadi,
            TYPE=htail_type
        )

        vtail = VTPLNF(
            NACA_V=vtail_naca,
            CHRDTP=vtail_chrdtp,
            SSPN=vtail_sspn,
            SSPNE=vtail_sspne,
            CHRDR=vtail_chrdr,
            SAVSI=vtail_savsi,
            CHSTAT=vtail_chstat,
            TYPE=vtail_type
        )

        # Create complete input
        datcom_input = DatcomInput(
            flight_conditions=flight_conditions,
            synthesis=synthesis,
            body=body,
            wing_planform=wing,
            horizontal_tail_planform=htail,
            vertical_tail_planform=vtail
        )

        # Generate file in output directory
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "for005.dat")

        generator = DatcomGenerator()
        generator.generate_file(datcom_input, case_id, output_path)

        # 📝 準備 DATCOM 資料結構（用於 state.latest_datcom）
        datcom_summary = {
            "case_id": case_id,
            "output_path": output_path,
            "generated_at": __import__('datetime').datetime.now().isoformat(),
            "parameters": {
                "flight_conditions": {
                    "nalpha": nalpha,
                    "alschd": alschd,
                    "nmach": nmach,
                    "mach": mach,
                    "nalt": nalt,
                    "alt": alt,
                    "wt": wt
                },
                "wing": {
                    "naca": wing_naca,
                    "chrdtp": wing_chrdtp,
                    "sspn": wing_sspn,
                    "chrdr": wing_chrdr
                },
                "htail": {
                    "naca": htail_naca,
                    "chrdtp": htail_chrdtp,
                    "sspn": htail_sspn
                },
                "vtail": {
                    "naca": vtail_naca,
                    "chrdtp": vtail_chrdtp,
                    "sspn": vtail_sspn
                }
            }
        }

        # 🔄 這裡的 return 包含更新 state 的資料
        # LangGraph 的 tool 可以返回 dict 來更新 state
        return {
            "messages": [f"✅ Successfully wrote DATCOM file to: {output_path}"],
            "latest_datcom": datcom_summary  # 更新 state.latest_datcom
        }

    except Exception as e:
        return f"❌ Error writing DATCOM file: {str(e)}"


# Custom ChatOpenAI that doesn't send parallel_tool_calls parameter
class CustomChatOpenAI(ChatOpenAI):
    """Custom ChatOpenAI that doesn't send parallel_tool_calls parameter"""

    def bind_tools(self, tools, **kwargs):
        kwargs.pop("parallel_tool_calls", None)
        return super().bind_tools(tools, **kwargs)


# Initialize model
model = CustomChatOpenAI(
    model=os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-oss-20b"),
    temperature=0,
    base_url=os.getenv("OPENAI_API_BASE_URL", "http://172.16.120.65:8087/v1"),
    api_key=os.getenv("OPENAI_API_KEY")  # type: ignore
)

# Create datcom_tool_agent using prebuilt component
datcom_tool_agent = create_react_agent(
    model=model,
    tools=[write_datcom_file],
    state_schema=SupervisorState,  # ✅ Use SupervisorState to access file_content
    prompt="""You are a DATCOM file generation specialist.

Your job is to:
1. Check if there is file content in state.file_content (from read_file_agent)
2. If file_content exists, use that as the primary source for data extraction
3. If no file_content, analyze the user's message for aircraft configuration data
4. Extract all required parameters for DATCOM input file
5. Call the write_datcom_file tool with all extracted parameters

The input data might be in various formats (structured text, markdown, raw DATCOM format, etc.).
Parse it carefully and map each value to the correct tool parameter.

IMPORTANT - Data Source Priority:
- FIRST check state.file_content - if it contains data, use it for extraction
- SECOND check user's message if no file_content available
- The data source tells you where to find the aircraft configuration

IMPORTANT - Parameter Formatting:
- For list parameters (alschd, mach, alt, x_coords, r_coords, zu_coords, zl_coords),
  provide them as comma-separated strings (e.g., "1.0,2.0,3.0")
- Ensure all required parameters are provided
- Double-check that list lengths match their corresponding count parameters
  (e.g., len(alschd) == nalpha)
""",
    name="datcom_tool_agent"
)

# Export as app
app = datcom_tool_agent
