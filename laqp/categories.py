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
    OVERLAY_NONE, OVERLAY_WIRES, OVERLAY_TB_WIRES, OVERLAY_POTA
)

# Category definitions: (short_name, full_name)
CATEGORIES = {
    # NON-LA Categories
    'nl_ph_qp': 'NON-LA - Phone Only - QRP',
    'nl_ph_lo': 'NON-LA - Phone Only - Low Power',
    'nl_ph_hi': 'NON-LA - Phone Only - High Power',
    'nl_ph_ol': 'NON-LA - Phone Only - Overlay',
    'nl_cw_qp': 'NON-LA - CW Only - QRP',
    'nl_cw_lo': 'NON-LA - CW Only - Low Power',
    'nl_cw_hi': 'NON-LA - CW Only - High Power',
    'nl_cw_ol': 'NON-LA - CW Only - Overlay',
    'nl_mx_qp': 'NON-LA - Mixed - QRP',
    'nl_mx_lo': 'NON-LA - Mixed - Low Power',
    'nl_mx_hi': 'NON-LA - Mixed - High Power',
    'nl_mx_ol': 'NON-LA - Mixed - Overlay',
    
    # LA Fixed Categories
    'lf_ph_qp': 'LA Fixed - Phone Only - QRP',
    'lf_ph_lo': 'LA Fixed - Phone Only - Low Power',
    'lf_ph_hi': 'LA Fixed - Phone Only - High Power',
    'lf_ph_ol': 'LA Fixed - Phone Only - Overlay',
    'lf_cw_qp': 'LA Fixed - CW Only - QRP',
    'lf_cw_lo': 'LA Fixed - CW Only - Low Power',
    'lf_cw_hi': 'LA Fixed - CW Only - High Power',
    'lf_cw_ol': 'LA Fixed - CW Only - Overlay',
    'lf_mx_qp': 'LA Fixed - Mixed - QRP',
    'lf_mx_lo': 'LA Fixed - Mixed - Low Power',
    'lf_mx_hi': 'LA Fixed - Mixed - High Power',
    'lf_mx_ol': 'LA Fixed - Mixed - Overlay',
    
    # LA Rover Categories
    'lr_ph_qp': 'LA Rover - Phone Only - QRP',
    'lr_ph_lo': 'LA Rover - Phone Only - Low Power',
    'lr_ph_hi': 'LA Rover - Phone Only - High Power',
    'lr_ph_ol': 'LA Rover - Phone Only - Overlay',
    'lr_cw_qp': 'LA Rover - CW Only - QRP',
    'lr_cw_lo': 'LA Rover - CW Only - Low Power',
    'lr_cw_hi': 'LA Rover - CW Only - High Power',
    'lr_cw_ol': 'LA Rover - CW Only - Overlay',
    'lr_mx_qp': 'LA Rover - Mixed - QRP',
    'lr_mx_lo': 'LA Rover - Mixed - Low Power',
    'lr_mx_hi': 'LA Rover - Mixed - High Power',
    'lr_mx_ol': 'LA Rover - Mixed - Overlay',
}

# Overlay types
OVERLAYS = {
    'WIRES': 'Wires Only',
    'TB-WIRES': 'Tribander + Wires',
    'POTA': 'Parks on the Air',
}


def get_category_short_name(location_type: int, mode_category: int, power_level: int, overlay: int) -> str:
    """
    Determine the short category name from contest attributes.
    
    Args:
        location_type: LOC_DX(0), LOC_NON_LA(1), LOC_LA_FIXED(2), LOC_LA_ROVER(3)
        mode_category: MODE_PHONE_ONLY(0), MODE_CW_DIGITAL_ONLY(1), MODE_MIXED(2)
        power_level: POWER_QRP(0), POWER_LOW(1), POWER_HIGH(2)
        overlay: OVERLAY_NONE(0), OVERLAY_WIRES(1), OVERLAY_TB_WIRES(2), OVERLAY_POTA(3)
    
    Returns:
        Short category name (e.g., 'nl_ph_lo', 'lf_mx_qp')
    """
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
    
    # Power suffix (overlay uses 'ol')
    if overlay > 0:  # Has overlay
        power = 'ol'
    elif power_level == 0:  # QRP
        power = 'qp'
    elif power_level == 1:  # Low
        power = 'lo'
    else:  # High
        power = 'hi'
    
    return f"{loc}_{mode}_{power}"


def get_base_category(location_type: int, mode_category: int, power_level: int) -> str:
    """
    Get the base category (non-overlay) for a log.
    
    This is used when a log has an overlay - it goes in both the
    base category AND the overlay category.
    """
    # Same as get_category_short_name but always ignores overlay
    if location_type in [0, 1]:
        loc = 'nl'
    elif location_type == 2:
        loc = 'lf'
    else:
        loc = 'lr'
    
    if mode_category == 0:
        mode = 'ph'
    elif mode_category == 1:
        mode = 'cw'
    else:
        mode = 'mx'
    
    if power_level == 0:
        power = 'qp'
    elif power_level == 1:
        power = 'lo'
    else:
        power = 'hi'
    
    return f"{loc}_{mode}_{power}"


def get_overlay_name(overlay: int) -> str:
    """Get the text name of an overlay category."""
    overlay_map = {
        0: None,
        1: 'WIRES',
        2: 'TB-WIRES',
        3: 'POTA',
    }
    return overlay_map.get(overlay)
