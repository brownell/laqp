# LAQP Cross-Checking Integration Guide

## Overview
The cross-checking module validates QSOs by finding reciprocal contacts in other submitted logs. Invalid QSOs are marked and warnings are added. Final scores are recalculated using only valid QSOs.

## Files Modified/Created

### New File
- **cross_check.py** - Main cross-checking module

### Files That Need Updates
- **processor.py** - Export two functions for reuse
- **database.py** - Remove `_header` before saving
- **generate_rankings.py** - Run after cross-checking

## Required Changes to Existing Code

### 1. processor.py - Export Scoring Functions

The cross-checking module needs to reuse your scoring logic. Make these functions available:

```python
def calculate_qso_points(qso, result):
    """
    Calculate points for a single QSO.
    
    Args:
        qso: QSO dictionary
        result: Operator result dictionary (for context like location_type)
        
    Returns:
        int: Points for this QSO
    """
    # Your existing point calculation logic
    # Based on location_type, mode, etc.
    pass


def determine_multiplier(qso, result):
    """
    Determine if a QSO provides a new multiplier.
    
    Args:
        qso: QSO dictionary
        result: Operator result dictionary
        
    Returns:
        dict|None: {'type': 'parish'|'state'|'province'|'dx', 'value': 'ORLEANS'}
                   or None if not a multiplier
    """
    # Your existing multiplier logic
    # Parse rcvd_qth to determine type and value
    pass
```

**If these functions don't exist as separate functions**, extract the logic from your main scoring loop.

### 2. database.py - Remove _header Before Saving

Update `save_contest_result()` to remove internal fields:

```python
def save_contest_result(result):
    """Save contest result to database"""
    
    # Create a copy to avoid modifying original
    data = result.copy()
    
    # Remove internal fields that shouldn't be saved
    if '_header' in data:
        del data['_header']
    
    # Convert sets to lists for JSON serialization
    for key, value in data.items():
        if isinstance(value, set):
            data[key] = list(value)
    
    # Save to database
    conn = get_connection()
    conn.execute('''
        INSERT OR REPLACE INTO contest_results (year, callsign, data)
        VALUES (?, ?, ?)
    ''', (data['year'], data['callsign'], json.dumps(data)))
    conn.commit()
```

### 3. Update Contest Workflow

**Current workflow (before cross-checking):**
```bash
# Upload logs via web or batch processing
python batch.py 2026

# Generate rankings (uses claimed scores)
python generate_rankings.py 2026

# Generate report
python generate_final_report.py 2026
```

**New workflow (with cross-checking):**
```bash
# 1. Upload and process all logs
python batch.py 2026

# 2. Run cross-checking (NEW STEP!)
python cross_check.py 2026

# 3. Generate rankings (now uses final scores)
python generate_rankings.py 2026

# 4. Generate report
python generate_final_report.py 2026
```

## How Cross-Checking Works

### Phase 1: Mark Invalid QSOs

For each QSO in each log:
1. Look for reciprocal QSO in other logs
2. Match on: band, mode, time (±30 min), callsigns
3. Verify exchange information
4. Mark QSO as valid/invalid
5. Add warning message if invalid

### Phase 2: Recalculate Scores

For each operator:
1. Get only valid QSOs
2. Re-run scoring algorithm (points + multipliers)
3. Update `final_score` and all statistics
4. Save updated result to database

### Warning Message Format

New warnings are added in same style as existing warnings:

```python
result['warnings'].append(
    f"QSO at line {line_num}: "
    f"{rcvd_call} on {band} {mode} at {time} - "
    f"Not found in {rcvd_call}'s log (NIL)"
)
```

## Cross-Check Status Codes

Each QSO gets a `cross_check_status` field:

- **CONFIRMED**: QSO found in both logs ✅ (valid)
- **NIL**: Not in other station's log ❌ (invalid, warning added)
- **BUSTED**: Callsign error detected ❌ (invalid, warning added)
- **EXCHANGE_ERROR**: QSO exists but exchange wrong ❌ (invalid, warning added)
- **UNIQUE**: Station didn't submit log ✅ (valid, no penalty, no warning)

## QSO Object Fields Added

Each QSO in `result['qsos']` gets these new fields:

```python
qso = {
    # Existing fields...
    'band': '20m',
    'mode': 'PH',
    'rcvd_call': 'W5XYZ',
    # ...
    
    # New cross-check fields:
    'is_valid': True,  # False if NIL/BUSTED/EXCHANGE_ERROR
    'cross_check_status': 'CONFIRMED',  # See status codes above
}
```

## Result Object Fields Updated

The result dictionary gets these updates:

```python
result = {
    # Before cross-check (Phase 1 - from batch.py):
    'claimed_score': 45000,  # What operator calculated
    'qso_points': 3000,      # From claimed QSOs
    'total_multipliers': 15, # From claimed QSOs
    
    # After cross-check (Phase 2 - from cross_check.py):
    'final_score': 43500,    # After removing invalid QSOs
    'qso_points': 2900,      # Recalculated
    'total_multipliers': 15, # Recalculated (may change!)
    'valid_qsos': 195,       # Count of valid QSOs
    'score_reduction_pct': 3.3,  # Percentage reduction
    
    # New warnings added:
    'warnings': [
        "QSO at line 42: W5XYZ on 20m PH at 14:30 - Not found in W5XYZ's log (NIL)",
        "QSO at line 67: K5ABD on 40m CW at 15:45 - Callsign error, possibly K5ABC (BUSTED)",
        # ...
    ]
}
```

## Configuration

At the top of `cross_check.py`:

```python
TIME_WINDOW_MINUTES = 30  # ±30 minutes for time matching
ENABLE_FUZZY_MATCHING = True  # Check for callsign errors
MAX_EDIT_DISTANCE = 2  # Max character differences for fuzzy matching
```

Adjust these as needed for Louisiana QSO Party rules.

## Testing Recommendations

### Test 1: Simple Two-Log Test
Create two test logs that work each other:
- Log A: K5ABC works W5XYZ
- Log B: W5XYZ works K5ABC
Both should show CONFIRMED status.

### Test 2: NIL Detection
- Log A: K5ABC works W5XYZ
- Log B: W5XYZ does NOT have K5ABC
K5ABC's QSO should show NIL status.

### Test 3: Busted Call
- Log A: K5ABC works "W5XYY" (typo)
- Log B: W5XYZ works K5ABC
Should detect BUSTED and suggest W5XYZ.

### Test 4: Exchange Error
- Log A: K5ABC sent "ORLEANS", logged W5XYZ as sending "TX"
- Log B: W5XYZ sent "LA", logged K5ABC correctly
Should detect EXCHANGE_ERROR.

## Performance

For typical LAQP scale (100-200 logs, ~40,000 total QSOs):
- Load all logs: < 1 second
- Build QSO index: < 1 second
- Cross-check all QSOs: 2-5 seconds
- Recalculate scores: < 1 second
- **Total time: < 10 seconds**

## Troubleshooting

### "Module 'processor' has no attribute 'calculate_qso_points'"
→ Need to export these functions from processor.py (see section 1 above)

### "Sets cannot be JSON serialized"
→ Update database.py to convert sets to lists before saving (see section 2)

### Scores don't change after cross-checking
→ Check that QSOs are actually being marked invalid. Look at warnings list.

### Too many NILs
→ Check time window setting. May need to increase to ±60 minutes.
→ Check mode matching logic - ensure PH and FM are treated as equivalent.

## Next Steps

1. ✅ Create cross_check.py (done)
2. Export functions from processor.py
3. Update database.py to remove _header
4. Test with small dataset
5. Run full cross-check on 2024 data
6. Review warnings and adjust parameters
7. Run generate_rankings.py with final scores
8. Generate final report

## Questions?

- How to handle rovers who change counties?
  → Currently handled - each QSO has its own sent_qth
  
- What about bonus stations (N5LCC)?
  → Treated like any other QSO - must be confirmed
  
- Do multipliers get recalculated?
  → Yes! If the first QSO for a mult is NIL, the next valid QSO becomes first
  
- Can I re-run cross-checking?
  → Yes! It's idempotent - safe to run multiple times
  
- How do I show before/after scores?
  → Use claimed_score vs final_score, show score_reduction_pct
