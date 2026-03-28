# Cross-Check Integration - Quick Start

## What You Need to Do

### 1. Update your `_score_qsos()` method in UnifiedLogProcessor class

Add this check at the beginning of your QSO processing loop:

```python
class UnifiedLogProcessor:
    # ... your __init__ and other methods ...
    
    def _score_qsos(self, result):
        """Score all QSOs and calculate multipliers"""
        
        # Reset counters
        result['qso_points'] = 0
        result['parishes_worked'] = set()
        result['states_worked'] = set()
        # ... etc
        
        # Process each QSO
        for qso in result['qsos']:
            # NEW: Skip QSOs flagged by cross-checking
            if qso.get('xcheck', '') != '':
                continue  # This QSO is NIL, B, or XCH - skip it
            
            # Your existing scoring logic
            points = self.calculate_points(qso)  # or however you calculate
            result['qso_points'] += points
            
            # Track multipliers
            # ... your existing multiplier logic
        
        # Calculate final score
        result['final_score'] = result['qso_points'] * result['total_multipliers']
        # ... any other final calculations
```

That's it! Just add the 2-line check to skip invalid QSOs.

### 2. QSO Field: `xcheck`

Each QSO will have an `xcheck` field added by cross_check.py:

- `''` (empty string) - Valid QSO, include in scoring
- `'NIL'` - Not found in other log, SKIP
- `'B'` - Busted callsign, SKIP  
- `'XCH'` - Exchange error, SKIP

### 3. Workflow

```bash
# After contest closes:

# Step 1: Process all logs (your current batch.py)
python batch.py 2026
# Result: All logs processed, claimed_score calculated

# Step 2: Run cross-checking (NEW!)
python cross_check.py 2026
# Result: Invalid QSOs marked, final_score recalculated

# Step 3: Generate rankings (existing code)
python generate_rankings.py 2026
# Now uses final_score instead of claimed_score

# Step 4: Generate reports (existing code)
python generate_final_report.py 2026
```

### 4. What Happens in Each Step

**batch.py** (existing):
- Processes each log file
- Sets `xcheck = ''` for all QSOs (or doesn't set it at all)
- Calculates `claimed_score` using all QSOs
- Saves to database

**cross_check.py** (NEW):
- Loads all logs from database
- Finds reciprocal QSOs
- Sets `xcheck` to 'NIL', 'B', or 'XCH' for invalid QSOs
- Creates `UnifiedLogProcessor` instance
- Calls `processor._score_qsos(result)` for each operator to recalculate
- Saves updated results with `final_score`

**_score_qsos()** (modified):
- Skips QSOs where `xcheck != ''`
- Recalculates points and multipliers using only valid QSOs
- Updates `final_score`

### 5. Testing

Run the test suite first:

```bash
python test_cross_check.py
```

This creates 3 test logs with known issues and verifies cross-checking works correctly.

### 6. Result Object Changes

Before cross-check:
```python
{
    'claimed_score': 45000,  # What operator calculated
    'final_score': 45000,    # Same as claimed initially
    'warnings': [...],       # Any format/mode warnings
}
```

After cross-check:
```python
{
    'claimed_score': 45000,      # Unchanged
    'final_score': 43500,        # Recalculated using valid QSOs only
    'score_reduction_pct': 3.3,  # New field
    'warnings': [                # New warnings added
        "QSO at line 42: W5XYZ on 20m PH at 14:30 - Not found in W5XYZ's log (NIL)",
        # ...
    ],
}
```

## Configuration

Edit these at top of cross_check.py:

```python
TIME_WINDOW_MINUTES = 30  # ±30 minutes for time matching
ENABLE_FUZZY_MATCHING = True  # Detect callsign typos
MAX_EDIT_DISTANCE = 2  # Max character differences for fuzzy matching
```

## Questions?

**Q: What if an operator doesn't submit a log?**  
A: Their QSO in your log is marked UNIQUE (xcheck='') - no penalty.

**Q: What about mode mismatches from initial processing?**  
A: QSOs already marked `is_valid=False` are skipped by cross-check.

**Q: Can I re-run cross-checking?**  
A: Yes! It's safe to run multiple times - it will re-mark everything.

**Q: How do I show before/after to users?**  
A: Use `claimed_score` vs `final_score` and show `score_reduction_pct`.
