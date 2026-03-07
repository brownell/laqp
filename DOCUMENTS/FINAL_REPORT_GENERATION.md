# Louisiana QSO Party - Final Report HTML Generation

## Overview

The `generate_final_report.py` script creates a complete HTML final report with all leaderboards in an Excel-like table format.

## Features

### Excel-Like Tables
- ✅ Fixed-width font (Courier New)
- ✅ Gridlines on all cells (black borders)
- ✅ Blue header row
- ✅ Alternating row colors (white/gray)
- ✅ Gold/Silver/Bronze highlighting for top 3
- ✅ Rank column centered and bold

### Report Structure
- Contest title and year
- Generation date
- Introductory text (from `FINAL_REPORT_TXT`)
- Sections with leaderboard tables
- Professional footer

## Usage

### Generate Report

```bash
# For current/default year
python generate_final_report.py

# For specific year
python generate_final_report.py 2026

# Custom output directory
python generate_final_report.py 2026 /custom/path
```

### In Contest Workflow

```bash
# Step 1: Process all logs
python batch.py

# Step 2: Calculate rankings
python generate_rankings.py 2026

# Step 3: Generate final report HTML
python generate_final_report.py 2026

# Result: laqp/data/results/final_report_2026.html
```

## Output

### File Location
```
laqp/data/results/
└── final_report_2026.html
```

### HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Louisiana QSO Party 2026 - Final Results</title>
    <style>/* Excel-like styling */</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Louisiana QSO Party 2026</h1>
            <h2>Final Results</h2>
            <p>Generated: March 5, 2026</p>
        </header>

        <div class="report-intro">
            <p>Introductory text...</p>
        </div>

        <!-- Section 1 -->
        <div class="section">
            <h2>Louisiana Stations</h2>
            
            <!-- Table 1 -->
            <div class="table-container">
                <h3>Louisiana - Fixed QRP Power</h3>
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>CallSign</th>
                            <th>Score</th>
                            ...
                        </tr>
                    </thead>
                    <tbody>
                        <tr> <!-- Gold for 1st -->
                            <td class="rank-cell">1</td>
                            <td class="data-cell">K5ABC</td>
                            <td class="data-cell">1250</td>
                        </tr>
                        <tr> <!-- Silver for 2nd -->
                            <td class="rank-cell">2</td>
                            <td class="data-cell">W5XYZ</td>
                            <td class="data-cell">980</td>
                        </tr>
                        ...
                    </tbody>
                </table>
            </div>
            
            <!-- More tables... -->
        </div>

        <!-- More sections... -->

        <footer>
            <p>&copy; 2026 Jefferson Amateur Radio Club</p>
        </footer>
    </div>
</body>
</html>
```

## Styling Features

### Table Appearance

**Headers:**
- Blue background (#4472C4)
- White text
- Bold font
- Black gridlines

**Rows:**
- Alternating white/gray (#f0f0f0)
- Black gridlines on all cells
- Hover effect (light blue)

**Top 3 Highlighting:**
- 1st place: Gold background (#FFD700)
- 2nd place: Silver background (#C0C0C0)
- 3rd place: Bronze background (#CD7F32)

**Rank Column:**
- Centered text
- Bold font
- Gray background (#f9f9f9)
- Fixed width (60px)

### Fonts

- **Tables:** Courier New (fixed-width, Excel-like)
- **Headers:** Georgia (serif, professional)
- **Body text:** Georgia

## Configuration Required

### In config/config.py

```python
# Introductory text for final report
FINAL_REPORT_TXT = """
Congratulations to all participants in the 2026 Louisiana QSO Party!
This report contains the final results across all categories.
"""

# Rankings dict (already defined)
RANKINGS = {
    'LFQ': 'Louisiana - Fixed QRP Power',
    ...
}

# Leaderboards config (already defined)
LEADERBOARDS = [...]

# Output directory
FINAL_REPORTS_DIR = 'laqp/data/results'
```

## Example Output

```
=============================================================
Louisiana QSO Party - Generate Final Report HTML (2026)
=============================================================

Generating leaderboards...
Creating HTML report...

=============================================================
Summary
=============================================================
Sections: 3
Tables: 18
Total entries: 247
Saved to: laqp/data/results/final_report_2026.html
```

## Integration with Results Page

Once generated, the HTML file is automatically available:

```
User visits: /results
Selects year: 2026
Clicks: "Show Final Report"
→ System reads: laqp/data/results/final_report_2026.html
→ Displays in browser
```

## Print-Friendly

The report includes print styles:
- Clean white background
- No shadows or hover effects
- Page breaks avoid splitting tables
- Professional formatting

## Customization

### Change Table Colors

```python
# In _get_css() function

# Header color
.leaderboard-table thead {
    background-color: #4472C4;  # Change blue
}

# Top 3 colors
.leaderboard-table tbody tr:nth-child(1) {
    background-color: #FFD700 !important;  # Gold
}
```

### Change Font

```python
# Tables
.leaderboard-table {
    font-family: 'Courier New', Courier, monospace;
}

# Headers
.report-header h1 {
    font-family: Georgia, serif;
}
```

### Add Logo

```html
<header class="report-header">
    <img src="logo.png" alt="Club Logo">
    <h1>Louisiana QSO Party {year}</h1>
    ...
</header>
```

## Testing

```bash
# 1. Ensure data exists
python batch.py
python generate_rankings.py 2026

# 2. Generate report
python generate_final_report.py 2026

# 3. View in browser
# Open: laqp/data/results/final_report_2026.html

# 4. Test via web interface
python web.py
# Visit: http://localhost:5000/results
# Select year: 2026
# Click: "Show Final Report"
```

## Troubleshooting

### Report file not found

```bash
# Check if directory exists
ls -la laqp/data/results/

# Create directory if needed
mkdir -p laqp/data/results

# Run generator
python generate_final_report.py 2026
```

### Empty tables

```bash
# Ensure rankings were generated
python generate_rankings.py 2026

# Check database has data
sqlite3 laqp/database/laqp.db "SELECT COUNT(*) FROM contest_results WHERE year = '2026';"
```

### Styling issues

- CSS is embedded in HTML (no external files needed)
- Clear browser cache if styles don't update
- Check browser console for errors

## Files

- ✅ `generate_final_report.py` - Main generator script
- ✅ Output: `laqp/data/results/final_report_{year}.html`

The final report generator creates professional Excel-like leaderboards ready for web display and printing!
