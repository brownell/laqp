# Louisiana QSO Party - Rankings System

## Overview

The rankings system stores each operator's ranking in various categories. Rankings are stored as a JSON dict in the `rankings` field of the `contest_results` table.

## Design Decision: JSON Field vs Separate Table

**Chosen Approach:** JSON dict in `rankings` field ✅

### Why?

**Primary Use Case:** User-centric lookups
- "Show me K5ABC's results" → Need all their rankings
- "Generate K5ABC's HTML report" → Need all their rankings
- Individual results page → Display all rankings for that user

**NOT the primary use case:**
- "Show me everyone ranked 3rd in category X"

The JSON approach is optimal for user-centric queries.

### Storage Format

```python
# In database (JSON string)
rankings = '{"NQ": 5, "NL": 12, "NC": 3}'

# When retrieved (Python dict)
rankings = {
    "NQ": 5,    # 5th place in Non-LA QRP
    "NL": 12,   # 12th place in Non-LA LOW
    "NC": 3     # 3rd place in Non-LA CW/Digital
}
```

## Configuration

### RANKINGS Dict (in config.py)

Maps ranking codes to display strings:

```python
RANKINGS = {
    # Louisiana Stations
    'LFQ': 'Louisiana - Fixed QRP Power',
    'LFL': 'Louisiana - Fixed LOW Power',
    'LFH': 'Louisiana - Fixed HIGH Power',
    'LFC': 'Louisiana - Fixed CW/Digital Mode',
    'LFS': 'Louisiana - Fixed SSB (phone) Mode',
    'LFM': 'Louisiana - Fixed MIXED Modes',
    'LRQ': 'Louisiana - Rover QRP Power',
    'LRL': 'Louisiana - Rover LOW Power',
    'LRH': 'Louisiana - Rover HIGH Power',
    'LRC': 'Louisiana - Rover CW/Digital Mode',
    'LRS': 'Louisiana - Rover SSB (phone) Mode',
    'LRM': 'Louisiana - Rover MIXED Modes',
    
    # Non-Louisiana Stations
    'NQ': 'Non Louisiana - QRP Power',
    'NL': 'Non Louisiana - LOW Power',
    'NH': 'Non Louisiana - HIGH Power',
    'NC': 'Non Louisiana - CW/Digital Mode',
    'NS': 'Non Louisiana - SSB (phone) Mode',
    'NM': 'Non Louisiana - MIXED Modes',
    
    # Add more as needed...
}
```

### LEADERBOARDS Config (Updated)

Now uses ranking codes instead of full titles:

```python
LEADERBOARDS = [
    [
        {'section_title': 'Louisiana Stations',
         'show': [['callsign', 'CallSign'], ['final_score', 'Score'], ...]},
        
        # OLD: {'title': 'LA Fixed QRP', ...}
        # NEW: Uses ranking code
        {'title': 'LFQ', 'ands': [['location_type', 'LA-FIXED'], ['power_level', 'QRP']]},
        {'title': 'LFL', 'ands': [['location_type', 'LA-FIXED'], ['power_level', 'LOW']]},
        ...
    ],
    ...
]
```

## How It Works

### 1. Generate Rankings

```bash
# Run after all logs processed
python generate_rankings.py 2024
```

This:
1. Clears all rankings for the year
2. Generates each leaderboard table
3. For each user in each table:
   - Saves ranking code + rank to their `rankings` field
4. Updates database with all rankings

### 2. Ranking Storage Process

For each leaderboard table (e.g., "NQ" - Non-LA QRP):

```python
# Query returns users sorted by score
results = [
    ('K5ABC', 1250),  # Rank 1
    ('W5XYZ', 980),   # Rank 2
    ('N5TEST', 750),  # Rank 3
]

# For each user, save ranking
K5ABC.rankings = {"NQ": 1, ...}  # Add NQ: 1
W5XYZ.rankings = {"NQ": 2, ...}  # Add NQ: 2
N5TEST.rankings = {"NQ": 3, ...}  # Add NQ: 3
```

### 3. Multiple Rankings Per User

A user may appear in multiple categories:

```python
# K5ABC's rankings after all leaderboards generated
{
    "NQ": 1,   # 1st in Non-LA QRP
    "NL": 5,   # 5th in Non-LA LOW (if also submitted LOW)
    "NS": 2,   # 2nd in Non-LA SSB
    "NM": 3    # 3rd in Non-LA MIXED (if also submitted MIXED)
}
```

## Database Schema

```sql
CREATE TABLE contest_results (
    ...
    rankings TEXT,  -- JSON dict: {"NQ": 1, "NL": 5, ...}
    ...
)
```

## Usage Examples

### Generate All Rankings

```python
from leaderboards import generate_leaderboards
from config.config import LEADERBOARDS, RANKINGS

# Generate and save rankings
sections = generate_leaderboards('2024', LEADERBOARDS, RANKINGS, save_rankings=True)
```

### Get User's Rankings

```python
from database import get_result

result = get_result('2024', 'K5ABC')
rankings = result['rankings']

# Display to user
for code, rank in rankings.items():
    title = RANKINGS[code]
    print(f"{title}: Rank {rank}")

# Output:
# Non Louisiana - QRP Power: Rank 1
# Non Louisiana - SSB (phone) Mode: Rank 2
```

### Display on Results Page

```html
<h3>Your Rankings</h3>
<table>
  <tr><th>Category</th><th>Rank</th></tr>
  {% for code, rank in result.rankings.items() %}
  <tr>
    <td>{{ RANKINGS[code] }}</td>
    <td>{{ rank }}</td>
  </tr>
  {% endfor %}
</table>
```

## Complete Workflow

### During Contest

```bash
# Users upload logs (web or batch)
python web.py  # or python batch.py
# Results saved to database with rankings = {}
```

### After Contest Closes

```bash
# Step 1: Generate rankings
python generate_rankings.py 2024
# All users now have their rankings populated

# Step 2: Generate HTML reports (next phase)
python generate_reports.py 2024
# Creates HTML files for each user with their rankings

# Step 3: Publish results
# Users can look up their results at /results
```

## Example Database Record

```python
{
    'year': '2024',
    'callsign': 'K5ABC',
    'final_score': 1250,
    'location_type': 'NON-LA',
    'power_level': 'QRP',
    'mode_category': 'PHONE',
    # ... other fields ...
    'rankings': {
        'NQ': 1,     # 1st in Non-LA QRP
        'NS': 2,     # 2nd in Non-LA SSB
        'NL': 5      # 5th in Non-LA LOW (if multiple submissions)
    }
}
```

## Advantages of JSON Storage

✅ **Simple** - One field, one query
✅ **Fast** - Single SELECT gets all user's rankings
✅ **Atomic** - All rankings updated together
✅ **Perfect for display** - Already in dict format
✅ **Scalable** - Dozens of categories OK (JSON is small)

## When to Regenerate Rankings

Regenerate rankings if:
- New logs added after initial ranking
- Scoring rules change
- Categories added/modified

```bash
# Regenerate rankings
python generate_rankings.py 2024
```

This clears and recalculates all rankings.

## Code Flow

```
generate_rankings.py
    ↓
generate_leaderboards(year, LEADERBOARDS, RANKINGS)
    ↓
For each section:
    For each table (ranking category):
        1. Clear old rankings for this year
        2. Query database with AND conditions
        3. Sort by final_score DESC
        4. For each user (rank 1, 2, 3...):
            Get current rankings dict
            Add: rankings[code] = rank
            Save back to database
    ↓
All users now have complete rankings dict
```

## Testing

```python
# Test rankings generation
from leaderboards import generate_leaderboards
from database import get_result

# Generate
sections = generate_leaderboards('2024', LEADERBOARDS, RANKINGS)

# Check a user
result = get_result('2024', 'K5ABC')
print(f"Rankings: {result['rankings']}")
# {'NQ': 1, 'NS': 2, 'NL': 5}

# Verify ranking count
for code, rank in result['rankings'].items():
    print(f"  {RANKINGS[code]}: Rank {rank}")
```

The rankings system is now complete and ready to populate individual rankings!
