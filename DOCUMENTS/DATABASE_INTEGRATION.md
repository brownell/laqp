# Louisiana QSO Party - Database Integration

This document explains how contest results are stored in the SQLite database.

## Overview

Contest results are stored in a SQLite database with a composite key of **year** and **callsign**. When a log is processed (either via web upload or batch processing), the result is automatically saved to the database. If a record already exists for that year/callsign combination, it is **replaced** with the new result.

## Database Schema

### Table: contest_results

**Primary Key:** (year, callsign)

| Field | Type | Description |
|-------|------|-------------|
| year | TEXT | Contest year (e.g., '2026') |
| callsign | TEXT | Station callsign (e.g., 'K5ABC') |
| name | TEXT | Operator name |
| category | TEXT | Short category code (e.g., 'nl_ph_lo') |
| overlay | TEXT | Overlay category ('WIRES', 'TB-WIRES', 'POTA', or NULL) |
| location_type | TEXT | 'DX', 'NON-LA', 'LA-FIXED', 'LA-ROVER' |
| mode_category | TEXT | 'PHONE', 'CW-DIGITAL', 'MIXED' |
| power_level | TEXT | 'QRP', 'LOW', 'HIGH' |
| is_rover | INTEGER | 0 or 1 (boolean) |
| final_score | INTEGER | Total score with bonuses |
| qso_points | INTEGER | Points from QSOs only |
| total_qsos | INTEGER | Total number of QSOs |
| valid_qsos | INTEGER | Valid QSOs (dups excluded) |
| total_multipliers | INTEGER | Total multiplier count |
| parishes_worked | TEXT | JSON array of parishes |
| parishes_worked_multiplier | INTEGER | Count |
| states_worked | TEXT | JSON array of states |
| states_worked_multiplier | INTEGER | Count |
| provinces_worked | TEXT | JSON array of provinces |
| provinces_multiplier | INTEGER | Count |
| dx_worked | TEXT | JSON array of DX |
| dx_worked_multiplier | INTEGER | Count |
| parishes_activated | TEXT | JSON array of parishes (rovers) |
| rover_bonus_points | INTEGER | Bonus points |
| worked_n5lcc | INTEGER | 0 or 1 (boolean) |
| num_n5lcc_contacts | INTEGER | Count |
| qsos_by_band | TEXT | JSON object |
| qsos_by_mode | TEXT | JSON object |
| qsos_by_hour | TEXT | JSON object |
| bands_worked | TEXT | JSON array |
| multipliers_by_band_mode | TEXT | JSON object |
| claimed_score | INTEGER | Operator's claimed score |
| errors | TEXT | JSON array of error strings |
| warnings | TEXT | JSON array of warning strings |
| has_valid_power | INTEGER | 0 or 1 (boolean) |
| has_valid_operator | INTEGER | 0 or 1 (boolean) |
| has_email | INTEGER | 0 or 1 (boolean) |
| is_valid | INTEGER | 0 or 1 (boolean) |
| **rankings** | TEXT | **JSON object with category rankings** |
| created_at | TEXT | ISO timestamp |
| updated_at | TEXT | ISO timestamp |

### Indexes

- `idx_year` - On (year)
- `idx_category` - On (year, category)
- `idx_score` - On (year, final_score DESC)

## Rankings Field

The `rankings` field stores a JSON object mapping ranking categories to placement:

```json
{
  "overall": 1,
  "nl_ph_lo": 2,
  "phone": 5,
  "low": 3
}
```

**Format:** `{'category': rank_integer}`

**Examples:**
- `{'cw': 45}` - 45th place in CW category
- `{'overall': 1, 'nl_ph_hi': 1}` - 1st place overall and in their category
- `{}` - Empty initially, populated when rankings are calculated

## Usage

### Web Upload (web.py)

When a contestant uploads a log via the web interface:

1. Log is validated, prepared, and scored
2. Year is added from form field (or defaults to current year)
3. Result is saved to database with `save_result(result)`
4. If a record exists for (year, callsign), it's replaced
5. HTML results are displayed to contestant

```python
# In web.py
result = process_single_log(Path(tmp_path), ...)
result['year'] = year  # From form or current year
save_result(result)  # Saves or updates database record
```

### Batch Processing (batch.py)

When processing all logs in batch mode:

1. All logs in incoming directory are processed
2. Year is from CONTEST_YEAR environment variable (or current year)
3. For each valid result:
   - HTML file is generated in `HTML_RESULTS/{year}/`
   - Result is saved to database
4. Invalid logs are reported but not saved

```python
# In batch.py
results = process_batch_logs(INCOMING_LOGS)
for result in results:
    result['year'] = year
    if result['is_valid']:
        generate_html_result(result, Path(HTML_RESULTS), year=year)
        save_result(result)  # Saves to database
```

### Setting Contest Year

**For Web:**
- Year comes from form field on upload page
- Falls back to current year if not provided

**For Batch:**
```bash
# Set via environment variable
export CONTEST_YEAR=2026
python batch.py

# Or in docker-compose.yml
environment:
  - CONTEST_YEAR=2026
```

## Database Operations

### Initialize Database

```python
from database import ContestDatabase

db = ContestDatabase('laqp/database/laqp.db')
# Tables are created automatically
```

### Save a Result

```python
from database import save_result

# Result dict must include 'year' and 'callsign'
result['year'] = '2026'
result['callsign'] = 'K5ABC'

# Save (or replace if exists)
if save_result(result):
    print("Saved successfully")
```

### Get a Result

```python
from database import get_result

result = get_result('2026', 'K5ABC')
if result:
    print(f"Score: {result['final_score']}")
```

### Get All Results for a Year

```python
from database import ContestDatabase

db = ContestDatabase()
results = db.get_results_by_year('2026', valid_only=True)

for result in results:
    print(f"{result['callsign']}: {result['final_score']}")
```

### Get Results by Category

```python
db = ContestDatabase()
results = db.get_results_by_category('2026', 'nl_ph_lo')

for rank, result in enumerate(results, 1):
    print(f"{rank}. {result['callsign']}: {result['final_score']}")
```

### Update Rankings

```python
db = ContestDatabase()

# Calculate rankings (to be implemented)
rankings_dict = {
    'K5ABC': {'overall': 1, 'nl_ph_lo': 1},
    'W5XYZ': {'overall': 2, 'nl_ph_lo': 2},
}

db.update_rankings('2026', rankings_dict)
```

### Get Statistics

```python
db = ContestDatabase()
stats = db.get_statistics('2026')

print(f"Total logs: {stats['total_logs']}")
print(f"Valid logs: {stats['valid_logs']}")
print(f"Total QSOs: {stats['total_qsos']}")
print(f"Top score: {stats['top_callsign']} - {stats['top_score']}")
```

## Data Serialization

The database module automatically handles:

- **Sets → JSON arrays** (sorted)
- **Dicts → JSON objects**
- **Booleans → integers** (0 or 1)
- **JSON arrays → Sets** (when deserializing set fields)

### Example

**In memory:**
```python
result = {
    'parishes_worked': {'ORL', 'JEF', 'STB'},
    'worked_n5lcc': True
}
```

**In database:**
```sql
parishes_worked = '["JEF", "ORL", "STB"]'  -- Sorted JSON array
worked_n5lcc = 1                            -- Integer
```

**Retrieved from database:**
```python
result = {
    'parishes_worked': {'JEF', 'ORL', 'STB'},  -- Back to set
    'worked_n5lcc': True                        -- Back to bool
}
```

## Database Location

Default: `laqp/database/laqp.db`

Can be configured:
```python
db = ContestDatabase('custom/path/to/database.db')
```

Or via environment:
```bash
export DATABASE_PATH=/app/database/laqp.db
```

## Composite Key Behavior

The database uses `INSERT OR REPLACE` which means:

1. First submission for K5ABC in 2026 → Creates new record
2. Second submission for K5ABC in 2026 → **Replaces entire record**
3. Submission for K5ABC in 2027 → Creates new record (different year)

This allows contestants to resubmit corrected logs.

## Rankings Population

The `rankings` field is empty (`{}`) when first saved. Rankings are populated later by a separate script that:

1. Retrieves all valid results for a year
2. Groups by category
3. Calculates rankings
4. Updates all records with `update_rankings()`

(Rankings calculation to be implemented in next phase)

## Next Steps

This sets up the foundation for:

1. ✅ Store individual results keyed by year/callsign
2. ✅ Automatic database save on upload and batch
3. ✅ Replace existing records on resubmission
4. ✅ Rankings field ready for population
5. ⬜ Calculate and populate rankings (next phase)
6. ⬜ Display rankings to users (next phase)
7. ⬜ Generate leaderboards (next phase)

## Testing

### Test Database Save

```python
from database import save_result

test_result = {
    'year': '2026',
    'callsign': 'K5TEST',
    'final_score': 1000,
    'is_valid': True,
    # ... other fields
}

if save_result(test_result):
    print("✓ Saved")
```

### Test Database Retrieve

```python
from database import get_result

result = get_result('2026', 'K5TEST')
if result:
    print(f"✓ Retrieved: {result['callsign']}")
    print(f"  Score: {result['final_score']}")
    print(f"  Rankings: {result['rankings']}")
```

### View Database Contents

```bash
# Using sqlite3 command line
sqlite3 laqp/database/laqp.db

# View all records
SELECT year, callsign, final_score, rankings FROM contest_results;

# View 2026 results
SELECT callsign, final_score FROM contest_results 
WHERE year = '2026' AND is_valid = 1 
ORDER BY final_score DESC;
```

## Files Modified

- ✅ **database.py** - New database module
- ✅ **web.py** - Save results after web upload
- ✅ **batch.py** - Save results during batch processing
- ✅ **processor.py** - Results include all fields (no changes needed)

The database integration is now complete and ready for rankings calculation!
