"""
Louisiana QSO Party Configuration
All contest-specific settings and constants
"""
import os
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Contest timing (UTC)
CONTEST_START_DAY1 = "202-04-06 1400"
CONTEST_END_DAY1 = "2024-04-07 0200"
# LAQP is a single session contest (unlike TQP's two sessions)
CONTEST_START_DAY2 = None
CONTEST_END_DAY2 = None

# Time format
TIME_FORMAT = "%Y-%m-%d %H%M"
DATE_FORMAT = "%Y-%m-%d"

# Directory structure
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = DATA_DIR / 'logs'
OUTPUT_DIR = DATA_DIR / 'output'

# Log processing directories
INCOMING_LOGS = LOGS_DIR / 'incoming'
VALIDATED_LOGS = LOGS_DIR / 'validated'
PREPARED_LOGS = LOGS_DIR / 'prepared'
PROBLEM_LOGS = LOGS_DIR / 'problems'
PROBLEM_REPORTS = LOGS_DIR / 'reports'

# Reference data files
LA_PARISHES_FILE = DATA_DIR / 'LA_Parish_Abbrevs.txt'
WVE_ABBREVS_FILE = DATA_DIR / 'WVE_Abbrevs.txt'
CANADIAN_PROVINCES_FILE = DATA_DIR / 'Canadian_Provinces.txt'

# Scoring constants
PHONE_QSO_POINTS = 2
CW_DIGITAL_QSO_POINTS = 4

# Bonus points
N5LCC_BONUS = 100  # Bonus for working Louisiana Contest Club station
ROVER_PARISH_ACTIVATION_BONUS = 50  # Points per parish activated by rover

# Bands (no WARC bands per rules)
VALID_BANDS = [160, 80, 40, 20, 15, 10, 6, 2]

# Band frequency ranges (in kHz)
BAND_RANGES = {
    160: (1800, 2000),
    80: (3500, 4000),
    40: (7000, 7300),
    20: (14000, 14350),
    15: (21000, 21450),
    10: (28000, 29700),
    6: (50000, 54000),
    2: (144000, 148000)
}

# Modes
VALID_MODES = ['CW', 'PH', 'DG', 'RY', 'FM']
CW_DIGITAL_MODES = ['CW', 'DG', 'RY']
PHONE_MODES = ['PH', 'FM']

# Categories
# Location types
LOC_DX = 0
LOC_NON_LA = 1  # Non-Louisiana (US/VE)
LOC_LA_FIXED = 2
LOC_LA_ROVER = 3

LOCATION_NAMES = {
    LOC_DX: "DX",
    LOC_NON_LA: "Non-LA",
    LOC_LA_FIXED: "LA Fixed",
    LOC_LA_ROVER: "LA Rover"
}

# Mode categories (for scoring categories)
MODE_PHONE_ONLY = 0
MODE_CW_DIGITAL_ONLY = 1
MODE_MIXED = 2

MODE_CATEGORY_NAMES = {
    MODE_PHONE_ONLY: "Phone Only",
    MODE_CW_DIGITAL_ONLY: "CW/Digital Only",
    MODE_MIXED: "Mixed Mode"
}

# Power levels (stored but not used for categories per LA rules)
POWER_QRP = 0
POWER_LOW = 1
POWER_HIGH = 2

POWER_NAMES = {
    POWER_QRP: "QRP (≤5W)",
    POWER_LOW: "Low Power (≤100W)",
    POWER_HIGH: "High Power (≤1500W)"
}

# Overlay categories
OVERLAY_NONE = 0
OVERLAY_WIRES = 1
OVERLAY_TB_WIRES = 2
OVERLAY_POTA = 3

OVERLAY_NAMES = {
    OVERLAY_NONE: "None",
    OVERLAY_WIRES: "WIRES",
    OVERLAY_TB_WIRES: "TB-WIRES",
    OVERLAY_POTA: "POTA"
}

# Category construction
# LA categories: 3 mode categories × 2 station types (fixed/rover)
# Non-LA categories: 3 mode categories × 1 station type
# Each can have 3 power levels and 4 overlay options

def get_category_name(location, mode_category, is_rover=False, power=None, overlay=None):
    """
    Generate a human-readable category name.
    
    In LA rules:
    - Power doesn't affect category (unlike TX)
    - Number of operators doesn't affect category (unlike TX)
    - Overlay is a separate award category
    """
    parts = []
    
    # Location prefix
    if location == LOC_DX:
        parts.append("DX")
    elif location == LOC_NON_LA:
        parts.append("Non-LA")
    elif location == LOC_LA_FIXED or location == LOC_LA_ROVER:
        parts.append("LA")
        if is_rover:
            parts.append("Rover")
    
    # Mode category
    parts.append(MODE_CATEGORY_NAMES[mode_category])
    
    # Power (informational only, not a category divider in LA)
    if power is not None:
        parts.append(f"({POWER_NAMES[power]})")
    
    # Overlay (separate award category)
    if overlay and overlay != OVERLAY_NONE:
        parts.append(f"[{OVERLAY_NAMES[overlay]}]")
    
    return " ".join(parts)

# Canadian provinces recognized (13 per LA rules, no maritime regions)
CANADIAN_PROVINCES = {
    'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'
}

# US prefixes
US_PREFIXES = {
    "K", "N", "W", "AA", "AB", "AC", "AD", "AE", "AF", "AG", "AH", "AI", "AJ", "AK", "AL"
}

# Canadian prefixes
CANADIAN_PREFIXES = {
    "CF", "CG", "CH", "CI", "CJ", "CK", "CY", "CZ", 
    "VA", "VB", "VC", "VD", "VE", "VF", "VG", "VO", 
    "VX", "VY", "XJ", "XK", "XL", "XM", "XN", "XO"
}

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/laqp.db')

# Web application configuration
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change-this-in-production')
UPLOAD_FOLDER = INCOMING_LOGS
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'laqp_processor.log'

def ensure_directories():
    """Create all necessary directories if they don't exist."""
    dirs = [
        DATA_DIR,
        LOGS_DIR,
        INCOMING_LOGS,
        VALIDATED_LOGS,
        PREPARED_LOGS,
        PROBLEM_LOGS,
        PROBLEM_REPORTS,
        OUTPUT_DIR,
        OUTPUT_DIR / 'scores',
        OUTPUT_DIR / 'statistics'
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    # Test configuration
    ensure_directories()
    print("LAQP Configuration Test")
    print(f"Contest dates: {CONTEST_START_DAY1} to {CONTEST_END_DAY1}")
    print(f"Base directory: {BASE_DIR}")
    print(f"\nSample categories:")
    print(f"  {get_category_name(LOC_NON_LA, MODE_MIXED)}")
    print(f"  {get_category_name(LOC_LA_FIXED, MODE_PHONE_ONLY, power=POWER_LOW)}")
    print(f"  {get_category_name(LOC_LA_ROVER, MODE_CW_DIGITAL_ONLY, is_rover=True)}")
    print(f"  {get_category_name(LOC_LA_FIXED, MODE_MIXED, overlay=OVERLAY_WIRES)}")
