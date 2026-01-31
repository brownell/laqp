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

