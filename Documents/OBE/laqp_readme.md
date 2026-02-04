# Louisiana QSO Party Log Processor

Contest log processing system for the Louisiana QSO Party, hosted by Jefferson Amateur Radio Club.

## Directory Structure

```
laqp_processor/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── setup.py                   # Package installation
├── .gitignore
│
├── config/                    # Configuration
│   ├── __init__.py
│   ├── config.py             # Contest settings, categories, scoring rules
│   └── database.py           # Database connection config
│
├── data/                      # Reference data files
│   ├── LA_Parish_Abbrevs.txt # Louisiana parish abbreviations (64 parishes)
│   ├── WVE_Abbrevs.txt       # US states and Canadian provinces
│   └── Canadian_Provinces.txt # 13 recognized Canadian provinces
│
├── laqp/                      # Main package
│   ├── __init__.py
│   │
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── database.py       # SQLAlchemy models and DB manager
│   │   └── log_entry.py      # Data classes for log parsing
│   │
│   ├── core/                  # Core processing modules
│   │   ├── __init__.py
│   │   ├── validator.py      # ✓ Log validation (completed)
│   │   ├── preparation.py    # TODO: Adapt from TX preparation.py
│   │   ├── scoring.py        # TODO: Adapt from TX scoring.py
│   │   └── statistics.py     # TODO: Adapt from TX statistics.py
│   │
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   ├── cabrillo.py       # Cabrillo parsing utilities
│   │   ├── callsign.py       # Callsign prefix/country lookup
│   │   └── file_ops.py       # File operations helpers
│   │
│   └── cli/                   # Command-line interface
│       ├── __init__.py
│       └── commands.py        # CLI command definitions
│
├── web/                       # Flask web application (future)
│   ├── __init__.py
│   ├── app.py                # Flask app initialization
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py         # Log upload endpoint
│   │   ├── validate.py       # Real-time validation
│   │   └── results.py        # Results display
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
│
├── logs/                      # Log processing directories
│   ├── incoming/             # Upload logs here
│   ├── validated/            # Valid logs after validation
│   ├── prepared/             # Logs prepared for scoring
│   ├── problems/             # Invalid logs
│   └── reports/              # Validation error reports
│
├── output/                    # Generated reports
│   ├── scores/               # Score reports and leaderboards
│   └── statistics/           # Contest statistics
│
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── test_validator.py
│   ├── test_preparation.py
│   ├── test_scoring.py
│   ├── test_statistics.py
│   └── sample_logs/          # Test log files
│
└── scripts/                   # Command-line scripts
    ├── process_all_logs.py   # ✓ Main batch processor (completed)
    ├── generate_reports.py   # TODO: Generate leaderboards/certificates
    └── init_database.py      # TODO: Initialize/reset database
```

## Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- sqlalchemy (database ORM)
- flask (web framework)
- pandas (data analysis)
- python-dateutil (date parsing)

### 2. Create Data Files

Create the parish abbreviations file at `data/LA_Parish_Abbrevs.txt`:
```
ACAD
ALLE
ASCE
...
(all 64 Louisiana parishes)
```

### 3. Initialize Database

```bash
python -c "from laqp.models.database import Database; from config.config import DATABASE_URL; db = Database(DATABASE_URL); db.create_tables()"
```

### 4. Create Directory Structure

```bash
python -c "from config.config import ensure_directories; ensure_directories()"
```

## Usage

### Batch Processing (Command Line)

Process all logs in the `logs/incoming/` directory:

```bash
# Full processing pipeline
python scripts/process_all_logs.py

# Validation only
python scripts/process_all_logs.py --validate-only

# Skip database storage
python scripts/process_all_logs.py --skip-db
```

### Web Application (Future)

```bash
# Start Flask development server
python -m flask --app web.app run

# Production with gunicorn
gunicorn -w 4 web.app:app
```

## Key Differences: LAQP vs TQP

### Categories
- **TQP**: Power (QRP/LOW/HIGH) × Mode (CWO/PHO/DGO/MIX) × Location (DX/NTX/TX-Fixed/TX-Mobile) × Operators (SO/MO)
- **LAQP**: Mode only (Phone/CW-Digital/Mixed) × Location (DX/Non-LA/LA-Fixed/LA-Rover)
  - Power is tracked but doesn't create separate categories
  - Number of operators is ignored (everyone lumped together)
  - Overlays (WIRES/TB-WIRES/POTA) are separate awards, not categories

### Scoring
- **TQP**: 2 pts phone, 3 pts CW/digital
- **LAQP**: 2 pts phone, 4 pts CW/digital

### Multipliers
- **TQP**: Counted once for entire contest
- **LAQP**: Counted per band AND per mode type (CW/Digital vs Phone)
  - Example: Working CADDO parish on 40m CW and 40m SSB = 2 multipliers

### Bonuses
- **TQP**: 
  - Mobile tracking: 500 pts per 5 counties worked per mobile
  - County activation: 1000 pts per county with 5+ QSOs
- **LAQP**:
  - N5LCC bonus: 100 pts one-time for working club station
  - Rover activation: 50 pts per parish activated (rovers only)

### Contest Period
- **TQP**: Two sessions (Saturday afternoon + Sunday afternoon)
- **LAQP**: Single session (Saturday 1400Z - Sunday 0200Z)

## Development Roadmap

### Phase 1: Core Processing (Current)
- [x] Project structure
- [x] Configuration system
- [x] Database schema
- [x] Log validator
- [ ] Log preparation (adapt from TQP)
- [ ] Scoring engine (adapt from TQP)
- [ ] Statistics generator (adapt from TQP)

### Phase 2: Command Line Tools
- [x] Batch processor
- [ ] Report generator
- [ ] Database utilities
- [ ] Leaderboard generator

### Phase 3: Web Application
- [ ] Flask app setup
- [ ] Log upload interface
- [ ] Real-time validation
- [ ] Score lookup
- [ ] Public results page

### Phase 4: Advanced Features
- [ ] Duplicate detection across logs
- [ ] Log checking (spot mismatches)
- [ ] Certificate generation
- [ ] Email notifications
- [ ] Admin dashboard

## LA Rules Summary

### Scoring
1. **QSO Points**: 2 for phone, 4 for CW/digital
2. **Multipliers**: 
   - Non-LA: LA parishes worked (per band/mode)
   - LA: parishes + states + provinces + DXCC (per band/mode)
3. **Score**: QSO points × multipliers + bonuses

### Categories (12 total)
- Non-LA: Phone Only, CW/Digital Only, Mixed
- LA Fixed: Phone Only, CW/Digital Only, Mixed  
- LA Rover: Phone Only, CW/Digital Only, Mixed
- (Each category can have 3 power levels: QRP/Low/High)

### Overlays (Separate Awards)
- WIRES: Wire antennas only
- TB-WIRES: Tribander + wires
- POTA: Parks/campgrounds/refuges

## Contact

Louisiana QSO Party
Jefferson Amateur Radio Club
questions@laqp.org

Contest Manager: KJ5BYZ
