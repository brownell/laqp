# Installation Checklist - LAQP Scoring Updates

## Files to Update

### 1. Config File
```bash
cd /home/brownell/Development/laqp

# Backup current config
cp config/config.py config/config.py.backup

# Copy new config
cp /path/to/config_updated.py config/config.py
```

**Check for**: `ROVER_PARISH_BONUS` (not `ROVER_PARISH_ACTIVATION_BONUS`)

### 2. Categories Module (NEW)
```bash
# Add categories module at top level of laqp/
cp /path/to/categories.py laqp/categories.py
```

### 3. Individual Results Module (NEW)
```bash
# Add individual results generator
cp /path/to/individual_results_v2.py laqp/core/individual_results.py
```

### 4. Scoring Module
```bash
# Backup old scoring
mv laqp/core/scoring.py laqp/core/scoring.py.backup

# Copy new scoring
cp /path/to/scoring_updated.py laqp/core/scoring.py
```

### 5. Update __init__.py
```bash
nano laqp/core/__init__.py
```

**Change FROM:**
```python
from .scoring_OLD import ScoreCalculator, score_single_log, generate_score_report
```

**Change TO:**
```python
from .scoring import ScoreCalculator, score_single_log, generate_score_report
from .individual_results import IndividualResultsGenerator, generate_all_individual_results
```

**And update __all__:**
```python
__all__ = [
    'LogValidator',
    'ValidationResult',
    'validate_single_log',
    'LogPreparation',
    'prepare_single_log',
    'ScoreCalculator',
    'score_single_log',
    'generate_score_report',
    'StatisticsGenerator',
    'generate_statistics_from_logs',
    'IndividualResultsGenerator',           # ADD THIS
    'generate_all_individual_results',      # ADD THIS
]
```

### 6. Process Script
```bash
# Backup old script
cp scripts/process_all_logs.py scripts/process_all_logs.py.backup

# Copy new script
cp /path/to/process_all_logs_updated.py scripts/process_all_logs.py
chmod +x scripts/process_all_logs.py
```

---

## Quick Check Before Running

Run these checks to make sure everything is in place:

```bash
cd /home/brownell/Development/laqp

# 1. Check config has new constants
grep "ROVER_PARISH_BONUS" config/config.py
grep "DATA_OUTPUT_DIR" config/config.py
grep "INDIVIDUAL_RESULTS_DIR" config/config.py

# 2. Check categories module exists
ls -l laqp/categories.py

# 3. Check individual_results exists
ls -l laqp/core/individual_results.py

# 4. Check scoring is updated (not scoring_OLD)
grep "get_category_short_name" laqp/core/scoring.py

# 5. Check __init__.py imports individual_results
grep "individual_results" laqp/core/__init__.py

# 6. Test imports work
python3 -c "from laqp.categories import CATEGORIES; print(f'{len(CATEGORIES)} categories loaded')"
python3 -c "from laqp.core import IndividualResultsGenerator; print('individual_results imported OK')"
```

---

## If You Get Errors

### Error: "cannot import name 'ROVER_PARISH_ACTIVATION_BONUS'"
**Fix**: Update config.py - it should be `ROVER_PARISH_BONUS` not `ROVER_PARISH_ACTIVATION_BONUS`

### Error: "cannot import name 'get_category_name'"
**Fix**: Add compatibility shim to bottom of config.py:
```python
def get_category_name(location_type, mode_category, power_level, overlay):
    from laqp.categories import get_category_short_name
    return get_category_short_name(location_type, mode_category, power_level, overlay)
```

### Error: "No module named 'laqp.categories'"
**Fix**: Copy categories.py to `laqp/categories.py` (not in core/)

### Error: Import from scoring_OLD
**Fix**: Edit `laqp/core/__init__.py` and change `scoring_OLD` to `scoring`

---

## After Everything is Installed

Test the pipeline:

```bash
cd /home/brownell/Development/laqp

# Full pipeline (if you have test logs)
python3 scripts/process_all_logs.py

# Or just validation
python3 scripts/process_all_logs.py --validate-only
```

---

## Directory Structure Check

After installation, you should have:

```
laqp/
├── categories.py                    ← NEW (top level)
├── core/
│   ├── __init__.py                 ← UPDATED
│   ├── validator.py                ← Existing
│   ├── preparation.py              ← Existing  
│   ├── scoring.py                  ← UPDATED (new 36-category system)
│   ├── scoring.py.backup           ← Backup of old
│   ├── individual_results.py       ← NEW
│   └── statistics.py               ← Existing

config/
├── config.py                       ← UPDATED (new directories, ROVER_PARISH_BONUS)
└── config.py.backup                ← Backup of old

scripts/
├── process_all_logs.py             ← UPDATED
└── process_all_logs.py.backup      ← Backup of old
```

---

## Summary of Changes

✅ **New 36-category system** (location × mode × power)
✅ **Individual DOCX result files** for each contestant
✅ **Overlay tracking** (logs appear in both categories)
✅ **Detailed statistics** (parishes, states, provinces, DX, bands, modes)
✅ **Better spacing and formatting** in DOCX files

Not yet done:
⏳ Summary_Report.docx generation (Step 4 - next)
⏳ Updated statistics module for category breakdowns
