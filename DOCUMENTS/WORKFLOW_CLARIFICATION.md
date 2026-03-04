# Louisiana QSO Party - Processing Workflow

This document clarifies what happens at each stage of log processing.

## Overview

**Key Principle:** The database stores the result objects. HTML generation happens separately, later.

## Two Processing Paths

### Path 1: Web Upload (Individual Contestant)

```
User uploads log
    ↓
Validate → Prepare → Score
    ↓
result object created (with empty rankings: {})
    ↓
Save result to DATABASE
    ↓
Format result for HTML display
    ↓
Return HTML to browser (displayed immediately, NOT saved to file)
```

**What's Saved:**
- ✅ Original log file → `logs/incoming/`
- ✅ Result object → Database

**What's NOT Saved:**
- ❌ HTML file (only displayed to user in browser)

### Path 2: Batch Processing (All Logs)

```
Read all logs from incoming/
    ↓
For each log:
    Validate → Prepare → Score
    ↓
    result object created (with empty rankings: {})
    ↓
    Save result to DATABASE
    ↓
Done
```

**What's Saved:**
- ✅ Result objects → Database (valid AND invalid logs)

**What's NOT Saved:**
- ❌ HTML files (generated later, after rankings)

## Complete Contest Workflow

### Phase 1: During Contest Period (What We Just Built)

**Web Uploads:**
1. Contestants upload logs anytime
2. Each log processed immediately
3. Result saved to database
4. HTML displayed to contestant (not saved)
5. Contestant can resubmit (overwrites database record)

**Or Batch Processing:**
1. Collect all logs in `incoming/` directory
2. Run batch.py
3. All results saved to database
4. No HTML generated yet

### Phase 2: After Contest Closes (To Be Built)

**Calculate Rankings:**
```python
# rankings.py (to be created)
1. Get all valid results from database for year
2. Group by categories
3. Calculate rankings within each category
4. Update database with rankings
```

**Generate HTML Reports:**
```python
# generate_reports.py (to be created)  
1. Get all results from database (with rankings populated)
2. Generate HTML file for each contestant
3. Save to HTML_RESULTS/{year}/{callsign}_results.html
4. Generate leaderboards
```

## Database Storage

### What's Stored in Database:

```python
{
    'year': '2026',
    'callsign': 'K5ABC',
    'name': 'John Smith',
    'category': 'nl_ph_lo',
    'final_score': 1250,
    'qso_points': 625,
    'total_qsos': 350,
    # ... all scoring details ...
    'parishes_worked': {'ORL', 'JEF', 'STB'},  # As JSON
    'multipliers_by_band_mode': {...},         # As JSON
    'rankings': {},  # Empty initially, populated later
    'is_valid': True,
    'errors': [],
    'warnings': []
}
```

### What's NOT Stored:

- ❌ `_qso_lines` - Internal processing only
- ❌ `_header` - Internal processing only
- ❌ HTML output
- ❌ Original log file content (stored separately in filesystem)

## File Locations

```
Project/
├── laqp/
│   ├── logs/
│   │   └── incoming/          # Original log files
│   │       ├── K5ABC.log
│   │       ├── W5XYZ.log
│   │       └── ...
│   └── database/
│       └── laqp.db           # SQLite database with result objects
│
└── HTML_RESULTS/              # Generated LATER after rankings
    └── 2026/
        ├── K5ABC_results.html    # Generated from database
        ├── W5XYZ_results.html    # Generated from database
        └── ...
```

## Current State (Phase 1 Complete)

✅ **Web Upload:**
- Processes log
- Saves to database
- Displays HTML to user
- Initializes rankings as `{}`

✅ **Batch Processing:**
- Processes all logs
- Saves to database
- Initializes rankings as `{}`
- Does NOT generate HTML yet

✅ **Database:**
- Stores all result objects
- Keyed by (year, callsign)
- Rankings field present but empty
- Ready for Phase 2

## Next Phase (To Be Built)

⬜ **Calculate Rankings:**
- Read all results from database
- Group by categories
- Rank contestants
- Update rankings field

⬜ **Generate HTML Reports:**
- Read results from database (with rankings)
- Generate HTML for each contestant
- Save to HTML_RESULTS/
- Generate leaderboards
- Make available via /results lookup

## Why This Approach?

### Benefits:

1. **Database is source of truth** - All results in one place
2. **Rankings calculated once** - After contest closes
3. **HTML generated once** - After rankings calculated
4. **Resubmissions easy** - Just replace database record
5. **No duplicate data** - Don't store HTML in DB

### Timeline:

- **During contest:** Results flow into database
- **Contest closes:** Run rankings calculation
- **After rankings:** Generate all HTML reports
- **Ongoing:** Users can look up their results

## Example: Complete Flow

### During Contest (Current Implementation)

```bash
# Contestant uploads via web
User: Upload K5ABC.log
Web:  Process → Save to DB → Display HTML
DB:   {year: 2026, callsign: K5ABC, score: 1250, rankings: {}}

# Or batch process
Admin: python batch.py
Batch: Process all → Save all to DB
DB:    Multiple records with rankings: {}
```

### After Contest (Next Phase)

```bash
# Calculate rankings
Admin: python rankings.py --year 2026
Script: Read DB → Calculate → Update DB
DB:     {year: 2026, callsign: K5ABC, rankings: {overall: 5, nl_ph_lo: 2}}

# Generate HTML
Admin: python generate_reports.py --year 2026
Script: Read DB → Generate HTML files
Files:  HTML_RESULTS/2026/K5ABC_results.html
        HTML_RESULTS/2026/W5XYZ_results.html
        ...

# Users view results
User:  Go to /results → Enter K5ABC, 2026
Web:   Serve HTML_RESULTS/2026/K5ABC_results.html
```

## Summary

**Current (Phase 1):**
- ✅ Web: Process → DB → Display (no HTML file)
- ✅ Batch: Process → DB (no HTML files)
- ✅ Rankings field: Empty `{}`

**Next (Phase 2):**
- ⬜ Calculate rankings → Update DB
- ⬜ Generate HTML files from DB
- ⬜ Serve HTML via /results

The database is the single source of truth. HTML files are generated output, created later from the database.
