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
CONTEST_YEAR = 2024  # Update each year
SPONSOR_NAME = "Jefferson Amateur Radio Club"
SPONSOR_WEBSITE = "w5gad.org"

# Contest dates (update each year)
CONTEST_START_DAY1 = date(int(CONTEST_YEAR), 4, 6)  # April 6, 2024
CONTEST_END_DAY1 = date(int(CONTEST_YEAR), 4, 7)    # April 7, 2024

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
INCOMING_LOGS = BASE_DIR / 'batch_input'
HTML_RESULTS = BASE_DIR / 'batch_results'

# ============================================================
# REFERENCE DATA FILES
# ============================================================

DATA_DIR = BASE_DIR / 'data'
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
OUTSIDE_LA = "NL"  # Non-Louisiana
LA_FIXED = 'LF'   # Louisiana Fixed
LA_ROVER = 'LR'   # Louisiana Rover

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
# US AND CANADIAN PREFIXES and Provinces
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

PROVINCES = ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']

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
Good luck and 73,
The Jefferson Amateur Radio Club
"""

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_FILE = DATA_DIR / 'database' / 'laqp.db'
DATABASE_URI = f'sqlite:///{DATABASE_FILE}'



# ============================================================
# LEADERBOARDS
# ============================================================

FINAL_REPORT_TXT = "this is the introductory text for the final report"
STATES_SUBSTRING = "SUBSTRING(callsign, 1, 2) IN ('AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','KA','KB','KC','KD','KE','KF','KG','KH','KI','KJ','KK','KL','KM','KN','KO','KP','KQ','KR','KS','KT','KU','KV','KW','KX','KY','KZ','NA','NB','NC','ND','NE','NF','NG','NH','NI','NJ','NK','NL','NM','NN','NO','NP','NQ','NR','NS','NT','NU','NV','NW','NX','NY','NZ','WA','WB','WC','WD','WE','WF','WG','WH','WI','WJ','WK','WL','WM','WN','WO','WP','WQ','WR','WS','WT','WU','WV','WW','WX','WY','WZ')"
PROVINCES_SUBSTRING = "SUBSTRING(callsign, 1, 2) IN ('VA', 'VE', 'VY', 'VO', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CY', 'CZ','XJ', 'XK', 'XL', 'XM', 'XN', 'XO')"
LEADERBOARDS = [
    [
        {'section_title': 'Top Level Categories - Louisiana Stations', 'show':[['callsign', 'CallSign'], ['final_score', 'Total Score'], ['overlay','Overlay'], ['mode_category','Mode'], ['num_n5lcc_contacts', 'N5LCC Contacts']]},
        {'title': 'LFQ', 'ands':[['location_type', 'LA-FIXED'], ['power_level', 'QRP']]},
        {'title': 'LFL', 'ands':[['location_type', 'LA-FIXED'], ['power_level', 'LOW']]},
        {'title': 'LFH', 'ands':[['location_type', 'LA-FIXED'], ['power_level', 'HIGH']]},
        {'title': 'LFC', 'ands':[['location_type', 'LA-FIXED'], ['mode_category', 'CW/Digital']]},
        {'title': 'LFS', 'ands':[['location_type', 'LA-FIXED'], ['mode_category', 'SSB']]},
        {'title': 'LFM', 'ands':[['location_type', 'LA-FIXED'], ['mode_category', 'MIXED']]},
        {'title': 'LRQ', 'ands':[['location_type', 'LA-ROVER'], ['power_level', 'QRP']]},
        {'title': 'LRL', 'ands':[['location_type', 'LA-ROVER'], ['power_level', 'LOW']]},
        {'title': 'LRH HIGH Power', 'ands':[['location_type', 'LA-ROVER'], ['power_level', 'HIGH']]},
        {'title': 'LA Rover CW or Digital Modes', 'ands':[['location_type', 'LA-ROVER'], ['mode_category', 'CW/Digital']]},
        {'title': 'LRS', 'ands':[['location_type', 'LA-ROVER'], ['mode_category', 'SSB']]},
        {'title': 'LRM', 'ands':[['location_type', 'LA-ROVER'], ['mode_category', 'MIXED']]}
    ],
    [
        {'section_title': 'Top Level Categories Non-Louisiana Stations', 'show':[['callsign', 'CallSign'], ['final_score', 'Total Score'], ['mode_category','Mode'], ['num_n5lcc_contacts', 'N5LCC Contacts']]},
        {'title': 'NQ', 'ands':[['location_type', 'NON-LA'], ['power_level', 'QRP']]},
        {'title': 'NL', 'ands':[['location_type', 'NON-LA'], ['power_level', 'LOW']]},
        {'title': 'NH', 'ands':[['location_type', 'NON-LA'], ['power_level', 'HIGH']]},
        {'title': 'NC', 'ands':[['location_type', 'NON-LA'], ['mode_category', 'CW/Digital']]},
        {'title': 'NS', 'ands':[['location_type', 'NON-LA'], ['mode_category', 'SSB']]},
        {'title': 'NM', 'ands':[['location_type', 'NON-LA'], ['mode_category', 'MIXED']]}
    ],
    [
        {'section_title': 'Top Level Categories - Stations in Canadian Provinces', 'show':[['callsign', 'CallSign'], ['final_score', 'Total Score'], ['mode_category','Mode'], ['parishes_worked', 'Parishes Worked'], ['num_n5lcc_contacts', 'N5LCC Contacts']]},
        {'title': 'CQ', 'ands':[[PROVINCES_SUBSTRING], ['power_level', 'QRP']]},
        {'title': 'CL', 'ands':[[PROVINCES_SUBSTRING], ['power_level', 'LOW']]},
        {'title': 'CH', 'ands':[[PROVINCES_SUBSTRING], ['power_level', 'HIGH']]},
        {'title': 'CC', 'ands':[[PROVINCES_SUBSTRING], ['mode_category', 'CW/Digital']]},
        {'title': 'CS', 'ands':[[PROVINCES_SUBSTRING], ['mode_category', 'SSB']]},
        {'title': 'CM', 'ands':[[PROVINCES_SUBSTRING], ['mode_category', 'MIXED']]},
    ],
    [
        {'section_title': 'Top Level Categories - Stations in US States', 'show':[['callsign', 'CallSign'], ['final_score', 'Total Score'], ['mode_category','Mode'], ['parishes_worked', 'Parishes Worked'], ['num_n5lcc_contacts', 'N5LCC Contacts']]},
        {'title': 'SQ', 'ands':[["(SUBSTRING(callsign, 1, 1) IN ('K', 'W', 'N')) OR (SUBSTRING(callsign, 1, 2) IN ())"], ['power_level', 'QRP']]},
        {'title': 'SL', 'ands':[[STATES_SUBSTRING], ['power_level', 'LOW']]},
        {'title': 'SH', 'ands':[[STATES_SUBSTRING], ['power_level', 'HIGH']]},
        {'title': 'SC', 'ands':[[STATES_SUBSTRING], ['mode_category', 'CW/Digital']]},
        {'title': 'SS', 'ands':[[STATES_SUBSTRING], ['mode_category', 'SSB']]},
        {'title': 'SM', 'ands':[[STATES_SUBSTRING], ['mode_category', 'MIXED']]}
    ]  
]

RANKINGS = {
    'LFQ': 'Louisiana - Fixed QRP Power',
    'LFL': 'Louisiana - Fixed LOW Power',
    'LFH': 'Louisiana - Fixed HIGH Power',
    'LFC': 'Louisiana - Fixed CW or Digital Modes',
    'LFS': 'Louisiana - Fixed SSB (phone) Mode',
    'LFM': 'Louisiana - Fixed MIXED Modes (SSB, CW, Digital',
    'LRQ': 'Louisiana - Rover QRP Power',
    'LRL': 'Louisiana - Rover LOW Power',
    'LRH': 'Louisiana - Rover HIGH Power',
    'LRC': 'Louisiana - Rover CW or Digital Modes',
    'LRS': 'Louisiana - Rover SSB (phone) Mode',
    'LRM': 'Louisiana - Rover MIXED Modes (SSB, CW, Digital',
    'NQ': 'Non Louisiana - QRP Power',
    'NL': 'Non Louisiana - LOW Power',
    'NH': 'Non Louisiana - HIGH Power',
    'NC': 'Non Louisiana - CW or Digital Modes',
    'NS': 'Non Louisiana - SSB (phone) Mode',
    'NM': 'Non Louisiana - MIXED Modes (SSB, CW, Digital',
    'CQ': 'Canadian Provinces -  QRP Power',
    'CL': 'Canadian Provinces -  LOW Power',
    'CH': 'Canadian Provinces -  HIGH Power',
    'CC': 'Canadian Provinces -  CW or Digital Modes',
    'SB': 'Canadian Provinces -  SSB (phone) Mode',
    'CM': 'Canadian Provinces -  MIXED Modes (SSB, CW, Digital',
    'SQ': 'States - QRP Power',
    'SL': 'States - LOW Power',
    'SH': 'States - HIGH Power',
    'SC': 'States - CW or Digital Modes',
    'SS': 'States - SSB (phone) Mode',
    'SM': 'States - MIXED Modes (SSB, CW, Digital',
}



# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_contest_year():
    """Get the current contest year"""
    return CONTEST_YEAR


def get_contest_name():
    """Get the full contest name with year"""
    return f"{CONTEST_NAME} {CONTEST_YEAR}"

# Category definitions: (short_name, full_name)
CATEGORIES = {
    # NON-LA Categories
    'nl_ph_qp': 'NON-LA - Phone Only - QRP',
    'nl_ph_lo': 'NON-LA - Phone Only - Low Power',
    'nl_ph_hi': 'NON-LA - Phone Only - High Power',
    'nl_cw_qp': 'NON-LA - CW Only - QRP',
    'nl_cw_lo': 'NON-LA - CW Only - Low Power',
    'nl_cw_hi': 'NON-LA - CW Only - High Power',
    'nl_mx_qp': 'NON-LA - Mixed - QRP',
    'nl_mx_lo': 'NON-LA - Mixed - Low Power',
    'nl_mx_hi': 'NON-LA - Mixed - High Power',
    
    # LA Fixed Categories
    'lf_ph_qp': 'LA Fixed - Phone Only - QRP',
    'lf_ph_lo': 'LA Fixed - Phone Only - Low Power',
    'lf_ph_hi': 'LA Fixed - Phone Only - High Power',
    'lf_cw_qp': 'LA Fixed - CW Only - QRP',
    'lf_cw_lo': 'LA Fixed - CW Only - Low Power',
    'lf_cw_hi': 'LA Fixed - CW Only - High Power',
    'lf_mx_qp': 'LA Fixed - Mixed - QRP',
    'lf_mx_lo': 'LA Fixed - Mixed - Low Power',
    'lf_mx_hi': 'LA Fixed - Mixed - High Power',
    
    # LA Rover Categories
    'lr_ph_qp': 'LA Rover - Phone Only - QRP',
    'lr_ph_lo': 'LA Rover - Phone Only - Low Power',
    'lr_ph_hi': 'LA Rover - Phone Only - High Power',
    'lr_cw_qp': 'LA Rover - CW Only - QRP',
    'lr_cw_lo': 'LA Rover - CW Only - Low Power',
    'lr_cw_hi': 'LA Rover - CW Only - High Power',
    'lr_mx_qp': 'LA Rover - Mixed - QRP',
    'lr_mx_lo': 'LA Rover - Mixed - Low Power',
    'lr_mx_hi': 'LA Rover - Mixed - High Power',
}

# Overlay types
OVERLAYS = {
    'WIRES': 'Wires Only',
    'TB-WIRES': 'Tribander + Wires',
    'POTA': 'Parks on the Air',
}
