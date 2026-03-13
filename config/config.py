"""
Louisiana QSO Party - Configuration
Application logic and contest rules (NOT secrets/credentials)
"""
import os

from pathlib import Path

# Load environment variables from .env file (for local development)
# In production (Fly.io), environment variables are already set
try:
    from dotenv import load_dotenv
    # Find .env file in parent directory
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not installed (production), that's OK
    pass

# ============================================================================
# ENVIRONMENT VARIABLES (read from .env)
# ============================================================================

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in environment!")

FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
CONTEST_YEAR = os.environ.get('CONTEST_YEAR', '2026')


# ============================================================================
# REFERENCE DATA FILES
# Reference data (from repo, in /app/)
# ============================================================================
# 
REFERENCE_DATA_DIR = os.environ.get('REFERENCE_DATA_DIR', '/app/reference_data')
# Reference files
LA_PARISHES_FILE = REFERENCE_DATA_DIR + '/la_parishes.txt'
WVE_ABBREVS_FILE = REFERENCE_DATA_DIR + '/wve_abbrevs.txt'


# ============================================================================
# PERSISTENT DATA FILES
# User data (on volume, in /data/)
# ============================================================================
BATCH_INPUT_DIR = os.environ.get('BATCH_INPUT_DIR', '/data/batch_input')
DATABASE_FILE = os.environ.get('DATABASE_FILE', '/data/database/laqp.db')
FINAL_REPORTS_DIR = os.environ.get('FINAL_REPORTS_DIR', '/data/final_reports')

# ============================================================================
# CONTEST CONFIGURATION
# ============================================================================

# Available years for results lookup
CONTEST_YEARS = os.environ.get('CONTEST_YEARS', '2026,2025,2024,2023').split(',')
CONTEST_YEAR = os.environ.get('CONTEST_YEAR', '2026')

# Log file extensions allowed for upload
ALLOWED_LOG_EXTENSIONS = {'log', 'txt', 'cbr'}

# Scoring rules
PHONE_QSO_POINTS = 2
CW_DIGITAL_QSO_POINTS = 4

# Bonus points
BONUS_CALLSIGN = 'N5LCC'  # Bonus for working N5LCC (Louisiana Contest Club)
CALLSIGN_BONUS_POINTS = 100  # Bonus for working N5LCC (Louisiana Contest Club)
ROVER_PARISH_BONUS = 50  # Bonus per parish activated (rovers only)

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

# Phone modes (for scoring)
PHONE_MODES = ['PH', 'FM', 'SSB', 'LSB', 'USB']

# CW/Digital modes (for scoring)
CW_DIGITAL_MODES = ['CW/DIGITAL', 'CW', 'RY', 'DIG', 'RTTY', 'FT8', 'FT4']

# ============================================================================
# CATEGORIES
# ============================================================================

# Log value options
POWER_VALUE_OPTIONS = ('QRP', 'LOW', 'HIGH')
STATION_VALUE_OPTIONS = ('FIXED', 'PORTABLE', 'MOBILE', 'ROVER')
OVERLAY_VALUE_OPTIONS = ('WIRES', 'TB-WIRES', 'POTA')

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

# ============================================================================
# RANKINGS - Short codes to full descriptions
# ============================================================================

RANKINGS = {
    # Louisiana Fixed
    'LFQ': 'Louisiana - Fixed QRP Power',
    'LFL': 'Louisiana - Fixed LOW Power',
    'LFH': 'Louisiana - Fixed HIGH Power',
    'LFC': 'Louisiana - Fixed CW/Digital Mode',
    'LFS': 'Louisiana - Fixed SSB (phone) Mode',
    'LFM': 'Louisiana - Fixed MIXED Modes (SSB, CW, Digital)',
    
    # Louisiana Rover
    'LRQ': 'Louisiana - Rover QRP Power',
    'LRL': 'Louisiana - Rover LOW Power',
    'LRH': 'Louisiana - Rover HIGH Power',
    'LRC': 'Louisiana - Rover CW/Digital Mode',
    'LRS': 'Louisiana - Rover SSB (phone) Mode',
    'LRM': 'Louisiana - Rover MIXED Modes (SSB, CW, Digital)',
    
    # Non-Louisiana
    'NQ': 'Non Louisiana - QRP Power',
    'NL': 'Non Louisiana - LOW Power',
    'NH': 'Non Louisiana - HIGH Power',
    'NC': 'Non Louisiana - CW/Digital Mode',
    'NS': 'Non Louisiana - SSB (phone) Mode',
    'NM': 'Non Louisiana - MIXED Modes (SSB, CW, Digital)',
    
    # DX
    'DQ': 'DX - QRP Power',
    'DL': 'DX - LOW Power',
    'DH': 'DX - HIGH Power',
    'DC': 'DX - CW/Digital Mode',
    'DS': 'DX - SSB (phone) Mode',
    'DM': 'DX - MIXED Modes (SSB, CW, Digital)',
    
    # Overlays
    'WIRES': 'WIRES-X Overlay',
    'TB-WIRES': 'TB-WIRES Overlay',
    'POTA': 'Parks on the Air Overlay',
}

# ============================================================================
# LEADERBOARD helpers - Declarative configuration
# ============================================================================

FINAL_REPORT_TXT = "this is the introductory text for the final report"

STATES_SUBSTRING = "SUBSTRING(callsign, 1, 2) IN ('AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','KA','KB','KC','KD','KE','KF','KG','KH','KI','KJ','KK','KL','KM','KN','KO','KP','KQ','KR','KS','KT','KU','KV','KW','KX','KY','KZ','NA','NB','NC','ND','NE','NF','NG','NH','NI','NJ','NK','NL','NM','NN','NO','NP','NQ','NR','NS','NT','NU','NV','NW','NX','NY','NZ','WA','WB','WC','WD','WE','WF','WG','WH','WI','WJ','WK','WL','WM','WN','WO','WP','WQ','WR','WS','WT','WU','WV','WW','WX','WY','WZ')"
PROVINCES_SUBSTRING = "SUBSTRING(callsign, 1, 2) IN ('VA', 'VE', 'VY', 'VO', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CY', 'CZ','XJ', 'XK', 'XL', 'XM', 'XN', 'XO')"

# ============================================================================
# LEADERBOARDS - Declarative configuration
# ============================================================================

LEADERBOARDS = [
    # Section 1: Louisiana Stations
    [
        # Section header
        {
            'section_title': 'Louisiana Stations',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Score'],
                ['name', 'Name'],
                ['location_type', 'Location'],
            ]
        },
        
        # Tables in this section
        {'title': 'LFQ', 'ands': [['location_type', 'LA-FIXED'], ['power_level', 'QRP']]},
        {'title': 'LFL', 'ands': [['location_type', 'LA-FIXED'], ['power_level', 'LOW']]},
        {'title': 'LFH', 'ands': [['location_type', 'LA-FIXED'], ['power_level', 'HIGH']]},
        {'title': 'LFC', 'ands': [['location_type', 'LA-FIXED'], ['mode_category', 'CW-DIGITAL']]},
        {'title': 'LFS', 'ands': [['location_type', 'LA-FIXED'], ['mode_category', 'PHONE']]},
        {'title': 'LFM', 'ands': [['location_type', 'LA-FIXED'], ['mode_category', 'MIXED']]},
        
        {'title': 'LRQ', 'ands': [['location_type', 'LA-ROVER'], ['power_level', 'QRP']]},
        {'title': 'LRL', 'ands': [['location_type', 'LA-ROVER'], ['power_level', 'LOW']]},
        {'title': 'LRH', 'ands': [['location_type', 'LA-ROVER'], ['power_level', 'HIGH']]},
        {'title': 'LRC', 'ands': [['location_type', 'LA-ROVER'], ['mode_category', 'CW-DIGITAL']]},
        {'title': 'LRS', 'ands': [['location_type', 'LA-ROVER'], ['mode_category', 'PHONE']]},
        {'title': 'LRM', 'ands': [['location_type', 'LA-ROVER'], ['mode_category', 'MIXED']]},
    ],
    
    # Section 2: Non-Louisiana Stations
    [
        {
            'section_title': 'Non-Louisiana Stations',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Score'],
                ['name', 'Name'],
                ['location_type', 'Location'],
            ]
        },
        
        {'title': 'NQ', 'ands': [['location_type', 'NON-LA'], ['power_level', 'QRP']]},
        {'title': 'NL', 'ands': [['location_type', 'NON-LA'], ['power_level', 'LOW']]},
        {'title': 'NH', 'ands': [['location_type', 'NON-LA'], ['power_level', 'HIGH']]},
        {'title': 'NC', 'ands': [['location_type', 'NON-LA'], ['mode_category', 'CW-DIGITAL']]},
        {'title': 'NS', 'ands': [['location_type', 'NON-LA'], ['mode_category', 'PHONE']]},
        {'title': 'NM', 'ands': [['location_type', 'NON-LA'], ['mode_category', 'MIXED']]},
    ],
    
    # Section 3: DX Stations
    [
        {
            'section_title': 'DX Stations',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Score'],
                ['name', 'Name'],
                ['location_type', 'Location'],
            ]
        },
        
        {'title': 'DQ', 'ands': [['location_type', 'DX'], ['power_level', 'QRP']]},
        {'title': 'DL', 'ands': [['location_type', 'DX'], ['power_level', 'LOW']]},
        {'title': 'DH', 'ands': [['location_type', 'DX'], ['power_level', 'HIGH']]},
        {'title': 'DC', 'ands': [['location_type', 'DX'], ['mode_category', 'CW-DIGITAL']]},
        {'title': 'DS', 'ands': [['location_type', 'DX'], ['mode_category', 'PHONE']]},
        {'title': 'DM', 'ands': [['location_type', 'DX'], ['mode_category', 'MIXED']]},
    ],
    
    # Section 4: Special Categories
    [
        {
            'section_title': 'Special Categories',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Score'],
                ['overlay', 'Overlay'],
            ]
        },
        
        {'title': 'WIRES', 'ands': [['overlay', 'WIRES']]},
        {'title': 'TB-WIRES', 'ands': [['overlay', 'TB-WIRES']]},
        {'title': 'POTA', 'ands': [['overlay', 'POTA']]},
    ],
]

# ============================================================================
# FINAL REPORT TEXT
# ============================================================================

FINAL_REPORT_TXT = """
Congratulations to all participants in the Louisiana QSO Party!

The Jefferson Amateur Radio Club is proud to present the final results.
Thank you for your participation and we look forward to seeing you next year!

73,
Jefferson Amateur Radio Club
"""
