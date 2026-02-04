# LAQP Processor - Quick Start Guide

## Summary: What's Been Completed

All four core processing modules are now **fully functional**:

✅ **Validator** - Validates Cabrillo log format and LA rules
✅ **Preparation** - Converts logs for scoring (band conversion, multi-parish splitting, category determination)
✅ **Scoring** - Calculates scores with LA rules (2pt phone, 4pt CW/dig, per-band-per-mode multipliers, bonuses)
✅ **Statistics** - Generates contest statistics and parish activity reports

You can now process logs end-to-end!

### 1. Create Project Directory

```bash
mkdir ~/laqp_processor
cd ~/laqp_processor
```

### 2. Set Up Python Virtual Environment (Recommended)

```bash
# Python 3 is already installed on Linux Mint
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

### 3. Create Project Structure

Save the `init_project.sh` script and run it:

```bash
chmod +x init_project.sh
./init_project.sh
```

Or manually create the structure from the README.

### 4. Save the Core Files

Save these files to the project directory:

- `requirements.txt`
- `setup.py`
- `.gitignore`
- `README.md`
- `config/config.py`
- `laqp/models/database.py`
- `laqp/core/validator.py`
- `scripts/process_all_logs.py`
- `data/LA_Parish_Abbrevs.txt`

And the `__init__.py` files in:
- `config/__init__.py`
- `laqp/__init__.py`
- `laqp/models/__init__.py`
- `laqp/core/__init__.py`
- `laqp/utils/__init__.py`
- `laqp/cli/__init__.py`
- `web/__init__.py`
- `tests/__init__.py`

### 5. Install Dependencies

```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### 6. Verify SQLite

```bash
# Check SQLite is available (it should be)
python3 -c "import sqlite3; print('SQLite version:', sqlite3.sqlite_version)"

# Check SQLAlchemy installed correctly
python3 -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)"
```

### 7. Initialize Database

```bash
python3 -c "
from laqp.models.database import Database
from config.config import DATABASE_URL
db = Database(DATABASE_URL)
db.create_tables()
print('Database initialized successfully!')
"
```

This creates `laqp.db` in your project root directory.

### 8. Test with Sample Log

The init script created a test log at `tests/sample_logs/TEST.log`.

Copy it to incoming:
```bash
cp tests/sample_logs/TEST.log logs/incoming/
```

### 9. Run Full Processing Pipeline

```bash
# Process all logs (validate, prepare, score, statistics)
python3 scripts/process_all_logs.py

# Or just validation
python3 scripts/process_all_logs.py --validate-only
```

You should see output for each stage with checkmarks:
```
============================================================
STEP 1: VALIDATION
============================================================
Found 1 log files to validate
Validating TEST.log... ✓ VALID

============================================================
STEP 2: PREPARATION  
============================================================
Preparing TEST.log... ✓ Non-LA Mixed Mode (Low Power (≤100W))

============================================================
STEP 3: SCORING
============================================================
Scoring TEST-prep.log... ✓ 8 points

============================================================
STEP 4: STATISTICS
============================================================
✓ Statistics generated!
  Total logs: 1
  Total QSOs: 2
  Parishes with activity: 2
```

### 10. Check Results

```bash
# Valid log moved here:
ls logs/validated/

# Database has the file path
python3 -c "
from laqp.models.database import Database
from config.config import DATABASE_URL
db = Database(DATABASE_URL)
session = db.get_session()
from laqp.models.database import Contestant
print('Contestants in database:', session.query(Contestant).count())
session.close()
"
```

## Common Issues & Solutions

### Python Not Found
```bash
# Use python3 explicitly on Linux
python3 --version
```

### Permission Denied on init_project.sh
```bash
chmod +x init_project.sh
```

### Module Not Found Error
```bash
# Make sure you're in project root when running scripts
cd ~/laqp_processor
python3 scripts/process_all_logs.py
```

### Virtual Environment Not Activated
```bash
# Activate it
source venv/bin/activate

# Deactivate when done
deactivate
```

### Can't Find laqp.db
```bash
# It's created in project root, check:
ls -la *.db

# Force creation:
python3 << 'EOF'
from laqp.models.database import Database
from config.config import DATABASE_URL
print(f"Database URL: {DATABASE_URL}")
db = Database(DATABASE_URL)
db.create_tables()
print("Database created!")
EOF
```

### Import Errors
```bash
# Make sure you're running from project root
# Python needs to find the modules
pwd  # Should show ~/laqp_processor

# The scripts use sys.path.insert to find modules
# This is already in process_all_logs.py
```

## Next Steps

### 1. Adapt the TX Scripts

Now copy your four TX scripts and modify them:

```bash
# Your TX scripts
cp /path/to/preparation.py laqp/core/preparation.py
cp /path/to/scoring.py laqp/core/scoring.py  
cp /path/to/statistics.py laqp/core/statistics.py

# Edit each file to:
# - Change imports to use config.config
# - Replace "county" with "parish"
# - Update scoring rules (2pt phone, 4pt CW/dig)
# - Update multiplier logic (per band/mode)
# - Update category logic (simpler than TX)
```

### 2. Create Real Data Files

Get the actual parish abbreviations from LAQP website and update:
- `data/LA_Parish_Abbrevs.txt`

### 3. Test with Real Logs

When you get real contest logs:
```bash
# Copy to incoming
cp /path/to/real_logs/*.log logs/incoming/

# Process them
python3 scripts/process_all_logs.py --validate-only
```

### 4. Development Workflow

```bash
# Always activate virtual environment first
source venv/bin/activate

# Make code changes...

# Test
python3 scripts/process_all_logs.py --validate-only

# When done
deactivate
```

## File Locations Reference

```
~/laqp_processor/
├── laqp.db              ← SQLite database file (auto-created)
├── venv/                ← Virtual environment (create with python3 -m venv venv)
├── logs/
│   ├── incoming/        ← PUT LOGS HERE to process
│   ├── validated/       ← Valid logs go here
│   ├── problems/        ← Invalid logs go here
│   └── reports/         ← Error reports for invalid logs
└── output/
    ├── scores/          ← Score reports (future)
    └── statistics/      ← Statistics reports (future)
```

## Getting Help

- Check the main README.md for detailed documentation
- Look at the sample log: `tests/sample_logs/TEST.log`
- Examine the validator output in `logs/reports/` for invalid logs
- Python errors? Check you're in project root and venv is activated

## Quick Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Validate logs only
python3 scripts/process_all_logs.py --validate-only

# Full processing (when modules ready)
python3 scripts/process_all_logs.py

# Check database
sqlite3 laqp.db ".tables"
sqlite3 laqp.db "SELECT * FROM contestants;"

# Deactivate virtual environment
deactivate
```
