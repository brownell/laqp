"""
Louisiana QSO Party - Category Definitions

Defines all 36 contest categories based on:
- Location: NON-LA, LA Fixed, LA Rover
- Mode: Phone Only, CW Only, Mixed
- Power: QRP, Low, High, Overlay

Each category has a short name (for files/variables) and full name (for display).
"""
import sys
from pathlib import Path

# Import constants from config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import (
    LOC_DX, LOC_NON_LA, LOC_LA_FIXED, LOC_LA_ROVER,
    MODE_PHONE_ONLY, MODE_CW_DIGITAL_ONLY, MODE_MIXED,
    POWER_QRP, POWER_LOW, POWER_HIGH,
    OVERLAY_NONE, OVERLAY_WIRES, OVERLAY_TB_WIRES, OVERLAY_POTA,
    CATEGORIES, OVERLAYS
)

def get_category_names(location_type, mode_category, power_level):
    """Get category name - compatibility function"""
    # Location prefix
    if location_type in [0, 1]:  # DX or NON-LA
        loc = 'nl'
    elif location_type == 2:  # LA Fixed
        loc = 'lf'
    else:  # LA Rover
        loc = 'lr'
    
    # Mode suffix
    if mode_category == 0:  # Phone only
        mode = 'ph'
    elif mode_category == 1:  # CW/Digital only
        mode = 'cw'
    else:  # Mixed
        mode = 'mx'
    
    # Power suffix 
    if power_level == 0:  # QRP
        power = 'qp'
    elif power_level == 1:  # Low
        power = 'lo'
    else:  # High
        power = 'hi'
    
    return {'short': f"{loc}_{mode}_{power}", 'full': CATEGORIES[f"{loc}_{mode}_{power}"]}

def get_overlay_name(overlay: int) -> str:
    """Get the text name of an overlay category."""
    overlay_map = {
        0: None,
        1: 'WIRES',
        2: 'TB-WIRES',
        3: 'POTA',
    }
    return overlay_map.get(overlay)
