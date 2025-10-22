# data_model.py
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

class FLTCON(BaseModel):
    """
    Flight Conditions Card
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    NALPHA: int = Field(
        ...,
        le=20,
        description="Number of angles of attack to be run, maximum of 20 (攻角數量)"
    )
    ALSCHD: List[float] = Field(
        ...,
        description="Values of angles of attack (攻角)"
    )
    NMACH: int = Field(
        ...,
        le=20,
        description="Number of mach number or velocities to be run, maximum of 20 (馬赫數組數)"
    )
    MACH: List[float] = Field(
        ...,
        description="Values of freestream mach number (馬赫數)"
    )
    NALT: int = Field(
        ...,
        le=20,
        description="Number of atmospheric conditions to be run, maximum of 20 (高度組數)"
    )
    ALT: List[float] = Field(
        ...,
        description="Values of geometric altitudes in feet (高度)"
    )
    WT: float = Field(
        ...,
        description="Vehicle weight (重量)"
    )

    # --- Validators ---
    @field_validator('ALSCHD')
    @classmethod
    def check_alpha_count(cls, v, info):
        if 'NALPHA' in info.data and len(v) != info.data['NALPHA']:
            raise ValueError(f"The number of angles of attack ({len(v)}) must match NALPHA ({info.data['NALPHA']})")
        return v

    @field_validator('MACH')
    @classmethod
    def check_mach_count(cls, v, info):
        if 'NMACH' in info.data and len(v) != info.data['NMACH']:
            raise ValueError(f"The number of Mach numbers ({len(v)}) must match NMACH ({info.data['NMACH']})")
        return v

    @field_validator('ALT')
    @classmethod
    def check_alt_count(cls, v, info):
        if 'NALT' in info.data and len(v) != info.data['NALT']:
            raise ValueError(f"The number of altitudes ({len(v)}) must match NALT ({info.data['NALT']})")
        return v
        

class SYNTHS(BaseModel):
    """
    Synthesis Card
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    XCG: float = Field(..., description="Longitudinal location of CG from nose in ft (X向重心位置)")
    ZCG: float = Field(10.0, description="Vertical location of CG relative to reference plane (Z向重心位置)")
    XW: float = Field(..., description="Longitudinal location of theoretical wing apex (X向主翼位置)")
    ZW: float = Field(..., description="Vertical location of theoretical wing apex relative to reference plane (Z向主翼位置)")
    ALIW: float = Field(..., description="Wing root chord incidence angle measured from reference plane (主翼安裝角)")
    XH: float = Field(..., description="Longitudinal location of theoretical horizontal tail apex (X向水平尾位置)")
    ZH: float = Field(..., description="Vertical location of theoretical horizontal tail apex relative to reference plane (Z向水平尾位置)")
    ALIH: float = Field(..., description="Horizontal tail root chord incidence angle measured from reference plane (水平尾安裝角)")
    XV: float = Field(..., description="Longitudinal location of theoretical vertical tail apex (X向垂尾位置)")
    ZV: float = Field(..., description="Vertical location of theoretical vertical tail apex (Z向垂尾位置)")


class WGPLNF(BaseModel):
    """
    Wing Planform Card
    """
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    CHRDTP: float = Field(..., description="Tip chord (翼尖弦長)")
    SSPN: float = Field(..., description="Semi-span theoretical panel from theoretical root chord (半翼展)")
    SSPNE: float = Field(..., description="Semi-span exposed panel (外露半翼展)")
    CHRDR: float = Field(..., description="Root chord (翼根弦長)")
    SAVSI: float = Field(..., description="Panel sweep angle (後掠角)")
    CHSTAT: float = Field(0.0, description="Reference chord station for inboard and outboard panel sweep angles, fraction of chord")
    TWISTA: float = Field(..., description="Twist angle, negative leading edge rotated down (扭轉角)")
    DHDADI: float = Field(..., description="Dihedral of panel (上反角)")
    TYPE: Literal[1] = Field(1.0, description="1 = straight tapered planform") # type: ignore
    NACA_W: str = Field(..., alias="NACA-W-", description="Airfoil (主翼剖面型號), e.g., 6-63-415")


class HTPLNF(BaseModel):
    """
    Horizontal Tail Planform Card
    """
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    CHRDTP: float = Field(..., description="Tip chord (翼尖弦長)")
    SSPN: float = Field(..., description="Semi-span theoretical panel from theoretical root chord (半翼展)")
    SSPNE: float = Field(..., description="Semi-span exposed panel (外露半翼展)")
    CHRDR: float = Field(..., description="Root chord (翼根弦長)")
    SAVSI: float = Field(..., description="Panel sweep angle (後掠角)")
    CHSTAT: float = Field(0.0, description="Reference chord station for inboard and outboard panel sweep angles, fraction of chord")
    TWISTA: float = Field(..., description="Twist angle, negative leading edge rotated down (扭轉角)")
    DHDADI: float = Field(..., description="Dihedral of panel (上反角)")
    TYPE: Literal[1] = Field(1.0, description="1 = straight tapered planform") # type: ignore
    NACA_H: str = Field(..., alias="NACA-H-", description="Airfoil (水平尾翼剖面型號), e.g., 4-0012")
        

class VTPLNF(BaseModel):
    """
    Vertical Tail Planform Card
    """
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    CHRDTP: float = Field(..., description="Tip chord (翼尖弦長)")
    SSPN: float = Field(..., description="Semi-span theoretical panel from theoretical root chord (半翼展)")
    SSPNE: float = Field(..., description="Semi-span exposed panel (外露半翼展)")
    CHRDR: float = Field(..., description="Root chord (翼根弦長)")
    SAVSI: float = Field(..., description="Panel sweep angle (後掠角)")
    CHSTAT: float = Field(0.0, description="Reference chord station for inboard and outboard panel sweep angles, fraction of chord")
    TYPE: Literal[1] = Field(1.0, description="1 = straight tapered planform") # type: ignore
    NACA_V: str = Field(..., alias="NACA-V-", description="Airfoil (垂直尾翼剖面型號), e.g., 4-0008")


class BODY(BaseModel):
    """
    Body Geometry Card - Revised to match DATCOM's parallel list structure.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    NX: int = Field(
        ...,
        le=20,
        description="Number of longitudinal body station at which data is specified, maximum of 20 (機身切幾個站位)"
    )
    X: List[float] = Field(
        ...,
        description="Longitudinal distance measured from arbitrary location (依序站位之 X 位置)"
    )
    R: List[float] = Field(
        ...,
        description="Planform half width at station Xi (依序佔位之半徑)"
    )
    ZU: List[float] = Field(
        ...,
        description="Z coordinate at upper body surface at station Xi (依序基準點向上距離)"
    )
    ZL: List[float] = Field(
        ...,
        description="Z coordinate at lower body surface at station Xi (依序基準點向下距離)"
    )
    ITYPE: Literal[1, 2] = Field(
        ...,
        description="1 = straight wing, 2 = swept wing (判斷是否為後掠翼)"
    )
    METHOD: Literal[1, 2] = Field(
        1,
        description="Calculation method, 1=Default, 2=Jorgensen"
    )

    # --- Validators ---
    @field_validator('X', 'R', 'ZU', 'ZL')
    @classmethod
    def check_station_data_count(cls, v: List[float], info):
        """
        Validates that the length of each geometry list (X, R, ZU, ZL) matches NX.
        """
        if 'NX' in info.data and len(v) != info.data['NX']:
            raise ValueError(
                f"The number of entries in the geometry list ({len(v)}) "
                f"must match NX ({info.data['NX']})"
            )
        return v


class DatcomInput(BaseModel):
    """
    Main model for a complete DATCOM input file.
    """
    flight_conditions: FLTCON
    synthesis: SYNTHS
    wing_planform: WGPLNF
    horizontal_tail_planform: HTPLNF
    vertical_tail_planform: VTPLNF
    body: BODY