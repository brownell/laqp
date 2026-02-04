# LAQP Scoring and Statistics Update - Implementation Plan

## Overview

Major restructuring of scoring and statistics to support 36 categories and individual contestant reports.

---

## Changes Required

### 1. Category System (36 categories)

**Structure**: Location × Mode × Power
- **Locations**: NON-LA (nl), LA Fixed (lf), LA Rover (lr)
- **Modes**: Phone (ph), CW (cw), Mixed (mx)
- **Power**: QRP (qp), Low (lo), High (hi), Overlay (ol)

**Overlay Handling**:
- Logs with overlays appear in TWO places:
  - Base category (e.g., `nl_cw_lo`)
  - Overlay category (e.g., `nl_cw_ol`)
- Track which overlay: WIRES, TB-WIRES, or POTA

**Files to Create/Update**:
- ✅ `laqp/categories.py` - Category definitions and helper functions
- ⏳ `laqp/core/scoring.py` - Update to use new category system

---

### 2. Individual Score Files

**Location**: `output/individual_results/`
**Format**: `CALLSIGN.txt` (e.g., `KJ5BYZ.txt`)

**Contents**:
```
============================================================
LOUISIANA QSO PARTY 2026 - INDIVIDUAL RESULTS
============================================================

Callsign: KJ5BYZ
Category: NON-LA - Phone Only - Low Power
Overlay: POTA (if applicable)

FINAL RESULTS:
Overall Placement: 5th in category
Final Score: 12,450 points
Total QSOs: 145
Multipliers: 42 (parishes worked)

BREAKDOWN:
States Worked: 35
Provinces Worked: 5
DX Contacts: 2

QSOs by Band:
  160m: 10
  80m: 25
  40m: 40
  20m: 35
  15m: 20
  10m: 15

QSOs by Mode:
  Phone: 145
  CW/Digital: 0

============================================================
Thank you for participating in the Louisiana QSO Party!
============================================================
```

**Files to Update**:
- ⏳ `laqp/core/scoring.py` - Add function to generate individual reports

---

### 3. Summary PDF Report

**Location**: `output/report_summary.pdf`

**Structure**:

```
┌─────────────────────────────────────────────────────┐
│  LOUISIANA QSO PARTY 2026                          │
│  Hosted by Jefferson Amateur Radio Club            │
│  w5gad.org                                         │
└─────────────────────────────────────────────────────┘

[REPORT_TXT from config]

┌─────────────────────────────────────────────────────┐
│  OVERALL STANDINGS - ALL CATEGORIES                 │
└─────────────────────────────────────────────────────┘

Rank  Callsign  Category              Score    QSOs
───────────────────────────────────────────────────────
1     W5XX      LA Fixed - Mixed - High  45,000   200
2     K5YY      NON-LA - Phone - Low     38,500   175
3     N5ZZ      LA Rover - Mixed - Low   32,100   190
...

┌─────────────────────────────────────────────────────┐
│  LOUISIANA QSO PARTY - CONTEST STATISTICS          │
└─────────────────────────────────────────────────────┘

Total Logs Received: 87
Total QSOs: 12,450
Unique Callsigns: 456
...

[Current contest_statistics.txt content]

┌─────────────────────────────────────────────────────┐
│  CATEGORY: NON-LA - Phone Only - Low Power         │
└─────────────────────────────────────────────────────┘

Rank  Callsign  Score    QSOs  Multipliers
──────────────────────────────────────────
1     K5ABC     12,450   145   42
2     W5DEF      9,800   125   39
...

[Category-specific statistics]

[Repeat for each active category]
```

**Files to Create**:
- ⏳ `laqp/core/pdf_report.py` - Generate PDF report using reportlab
- ⏳ Update `laqp/core/statistics.py` - Generate category-specific stats

---

### 4. File Structure Changes

**Remove**:
- ❌ `output/scores/CALLSIGN-score.txt` (old single-category files)
- ❌ `output/statistics/contest_statistics.txt` (moves to PDF)

**Keep**:
- ✅ `logs/prepared/` - Prepared logs with category info
- ✅ Database (for now, not using it yet)

**Add**:
- ⏳ `output/individual_results/CALLSIGN.txt` - Individual results
- ⏳ `output/report_summary.pdf` - Master PDF report

---

## Implementation Steps

### Step 1: Update Categories
- [x] Create `laqp/categories.py` with all 36 categories
- [ ] Add to `config/config.py`:
  - `INDIVIDUAL_RESULTS_DIR`
  - `OUTPUT_DIR`
  - `REPORT_TXT`
  - Update `ensure_directories()`

### Step 2: Update Scoring Module
- [ ] Modify `laqp/core/scoring.py`:
  - Use new category system
  - Track overlay information
  - Generate individual `.txt` files in `INDIVIDUAL_RESULTS_DIR`
  - Calculate placement within category
  - Track all required statistics (QSOs, multipliers, states, provinces, DX)

### Step 3: Update Statistics Module
- [ ] Modify `laqp/core/statistics.py`:
  - Generate overall standings (all logs sorted by score)
  - Generate category-specific statistics
  - Return data structures for PDF generation
  - Keep current contest statistics content

### Step 4: Create PDF Generator
- [ ] Create `laqp/core/pdf_report.py`:
  - Install `reportlab`: `pip install reportlab`
  - Generate PDF with:
    - Header (title, sponsor, year)
    - REPORT_TXT
    - Overall standings
    - Contest statistics
    - Category sections (only active categories)
  - Output to `output/report_summary.pdf`

### Step 5: Update Main Processing Script
- [ ] Modify `scripts/process_all_logs.py`:
  - After scoring, collect all score data
  - Generate category standings
  - Create individual result files
  - Generate PDF report
  - Remove old file cleanup

### Step 6: Testing
- [ ] Test with sample logs
- [ ] Verify categories assigned correctly
- [ ] Check overlay handling
- [ ] Verify individual files created
- [ ] Check PDF generation
- [ ] Verify placements calculated correctly

---

## Data Flow

```
1. Validated Logs
   ↓
2. Preparation (adds TQP-CATEGORY)
   ↓
3. Scoring (calculates points, assigns categories)
   ↓
4. Collect all scores
   ↓
5. Sort by score (overall)
   ↓
6. Generate individual_results/CALLSIGN.txt (with placement)
   ↓
7. Group by category
   ↓
8. For each category:
   - Sort by score
   - Calculate placements
   - Generate statistics
   ↓
9. Generate PDF:
   - Overall standings
   - Contest statistics
   - Category sections (only active ones)
   ↓
10. Output: report_summary.pdf
```

---

## Category Assignment Logic

```python
# Determine base category
location = determine_location(log)  # nl, lf, lr
mode = determine_mode(log)  # ph, cw, mx
power = determine_power(log)  # qp, lo, hi
overlay = determine_overlay(log)  # None, WIRES, TB-WIRES, POTA

# Assign to categories
if overlay:
    base_category = f"{location}_{mode}_{power}"
    overlay_category = f"{location}_{mode}_ol"
    categories = [base_category, overlay_category]
else:
    category = f"{location}_{mode}_{power}"
    categories = [category]
```

---

## Next Steps

1. Review this plan
2. Update `config/config.py` with new settings
3. Implement updated scoring module
4. Implement PDF generation
5. Test with sample data

Ready to proceed?
