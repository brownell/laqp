"""
Louisiana QSO Party - Configuration
Updated with new output directory structure and categories
"""
from pathlib import Path
from datetime import date, time
import shutil

# ============================================================
# BASE PATHS
# ============================================================

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / 'config'

# ============================================================
# CONTEST INFORMATION
# ============================================================

CONTEST_NAME = "Louisiana QSO Party"
CONTEST_YEAR = 2026  # Update each year
SPONSOR_NAME = "Jefferson Amateur Radio Club"
SPONSOR_WEBSITE = "w5gad.org"

# Contest dates (update each year)
CONTEST_START_DAY1 = date(2024, 4, 6)  # April 6, 2024
CONTEST_END_DAY1 = date(2024, 4, 7)    # April 7, 2024

# Contest times (UTC)
CONTEST_START_TIME = time(14, 0)  # 14:00 UTC
CONTEST_END_TIME = time(2, 0)     # 02:00 UTC (next day)

# Date and time formats
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H%M"

# ============================================================
# LOG DIRECTORIES
# ============================================================

# Input logs
DATA_DIR = BASE_DIR / 'data'
INCOMING_LOGS = DATA_DIR / 'logs' / 'incoming'
VALIDATED_LOGS = DATA_DIR / 'logs' / 'validated'
PREPARED_LOGS = DATA_DIR / 'logs' / 'prepared'
PROBLEMS_LOGS = DATA_DIR / 'logs' / 'problems'

# Output directory structure (NEW)
DATA_OUTPUT_DIR = DATA_DIR / 'output'
INDIVIDUAL_RESULTS_DIR = DATA_OUTPUT_DIR / 'individual_results'

# Legacy directories (to be removed)
OLD_SCORES_DIR = DATA_DIR / 'output' / 'scores'
OLD_STATISTICS_DIR = DATA_DIR / 'output' / 'statistics'

# Keep for compatibility during transition
SCORES_DIR = OLD_SCORES_DIR
STATISTICS_DIR = OLD_STATISTICS_DIR

# ============================================================
# REFERENCE DATA FILES
# ============================================================

REFERENCE_DATA_DIR = DATA_DIR / 'reference_data'
LA_PARISHES_FILE = REFERENCE_DATA_DIR / 'la_parishes.txt'
WVE_ABBREVS_FILE = REFERENCE_DATA_DIR / 'wve_abbrevs.txt'

# ============================================================
# BAND AND MODE DEFINITIONS
# ============================================================

# need to convert freq in KHz to band
# Band frequency ranges (in kHz) - tuples of (min, max) for each band
BAND_RANGES = {
    160: (1800, 2000),      # 160m: 1.8 - 2.0 MHz
    80:  (3500, 4000),      # 80m:  3.5 - 4.0 MHz
    40:  (7000, 7300),      # 40m:  7.0 - 7.3 MHz
    20:  (14000, 14350),    # 20m:  14.0 - 14.35 MHz
    15:  (21000, 21450),    # 15m:  21.0 - 21.45 MHz
    10:  (28000, 29700),    # 10m:  28.0 - 29.7 MHz
    6:   (50000, 54000),    # 6m:   50.0 - 54.0 MHz
    2:   (144000, 148000),  # 2m:   144.0 - 148.0 MHz
}

def freq_to_band(freq_khz: int) -> int:
    """
    Convert frequency in kHz to band in meters.
    
    Args:
        freq_khz: Frequency in kHz
    
    Returns:
        Band in meters (e.g., 20, 40, 80) or None if not in a valid band
    """
    for band, (min_freq, max_freq) in BAND_RANGES.items():
        if min_freq <= freq_khz <= max_freq:
            return band
    return None

# Valid modes
VALID_MODES = ['CW', 'PH', 'RY', 'DIG', 'FM', 'SSB', 'LSB', 'USB', 'RTTY', 'FT8', 'FT4']

# Phone modes (for scoring)
PHONE_MODES = ['PH', 'FM', 'SSB', 'LSB', 'USB']

# CW/Digital modes (for scoring)
CW_DIGITAL_MODES = ['CW', 'RY', 'DIG', 'RTTY', 'FT8', 'FT4']

# ============================================================
# SCORING PARAMETERS
# ============================================================

# QSO Points
PHONE_QSO_POINTS = 2
CW_DIGITAL_QSO_POINTS = 4

# Bonus points
N5LCC_BONUS = 100  # Bonus for working N5LCC (Louisiana Contest Club)
ROVER_PARISH_BONUS = 50  # Bonus per parish activated (rovers only)

# ============================================================
# CATEGORY DEFINITIONS
# ============================================================

# Location types
LOC_DX = 0           # DX (outside North America)
LOC_NON_LA = 1       # Non-Louisiana (US/Canada, not LA)
LOC_LA_FIXED = 2     # Louisiana Fixed station
LOC_LA_ROVER = 3     # Louisiana Rover/Mobile

# Mode categories
MODE_PHONE_ONLY = 0
MODE_CW_DIGITAL_ONLY = 1
MODE_MIXED = 2

# Power levels
POWER_QRP = 0    # 5W or less
POWER_LOW = 1    # 100W or less
POWER_HIGH = 2   # 1500W or less

# Overlay categories
OVERLAY_NONE = 0
OVERLAY_WIRES = 1        # Wires only antennas
OVERLAY_TB_WIRES = 2     # Tribander + wires
OVERLAY_POTA = 3         # Parks on the Air

# ============================================================
# US AND CANADIAN PREFIXES
# ============================================================

US_PREFIXES = [
    'K', 'W', 'N', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK',
    'KA', 'KB', 'KC', 'KD', 'KE', 'KF', 'KG', 'KH', 'KI', 'KJ', 'KK', 'KL', 'KM', 'KN', 'KO', 'KP', 'KQ', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ',
    'NA', 'NB', 'NC', 'ND', 'NE', 'NF', 'NG', 'NH', 'NI', 'NJ', 'NK', 'NL', 'NM', 'NN', 'NO', 'NP', 'NQ', 'NR', 'NS', 'NT', 'NU', 'NV', 'NW', 'NX', 'NY', 'NZ',
    'WA', 'WB', 'WC', 'WD', 'WE', 'WF', 'WG', 'WH', 'WI', 'WJ', 'WK', 'WL', 'WM', 'WN', 'WO', 'WP', 'WQ', 'WR', 'WS', 'WT', 'WU', 'WV', 'WW', 'WX', 'WY', 'WZ'
]

CANADIAN_PREFIXES = [
    'VA', 'VE', 'VY', 'VO', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CY', 'CZ',
    'XJ', 'XK', 'XL', 'XM', 'XN', 'XO'
]

# ============================================================
# FLASK WEB APPLICATION
# ============================================================

FLASK_SECRET_KEY = 'change-this-in-production-use-secrets'
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# ============================================================
# REPORT TEXT
# ============================================================

REPORT_TXT = """
The Louisiana QSO Party is an annual amateur radio contest held on the first 
weekend of April. Participants make contacts with Louisiana stations and earn 
points based on QSO count and multipliers (parishes, states, provinces, and DX).

Awards are given in multiple categories based on location (Non-Louisiana, 
Louisiana Fixed, Louisiana Rover), mode (Phone, CW/Digital, Mixed), and power 
level (QRP, Low, High). Additional overlay categories recognize special 
operating conditions (Wires Only, Tribander+Wires, POTA).

Thank you to all participants for making this year's Louisiana QSO Party a success!
"""

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_FILE = BASE_DIR / 'data' / 'laqp.db'
DATABASE_URI = f'sqlite:///{DATABASE_FILE}'

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def ensure_initial_directories():
    """Ensure all required directories exist"""
    initial_directories = [
        # Log directories
        VALIDATED_LOGS,
        PREPARED_LOGS,
        PROBLEMS_LOGS,
        
        # Output directories (NEW structure)
        DATA_OUTPUT_DIR,
        INDIVIDUAL_RESULTS_DIR
    ]
    
    for directory in initial_directories:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def get_contest_year():
    """Get the current contest year"""
    return CONTEST_YEAR


def get_contest_name():
    """Get the full contest name with year"""
    return f"{CONTEST_NAME} {CONTEST_YEAR}"


# Ensure directories exist on import
ensure_initial_directories()

def get_category_name(location_type, mode_category, is_rover, power_level, overlay):
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
