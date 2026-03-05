# Louisiana QSO Party - Results Page Implementation

## Overview

The results page (`/results`) allows visitors to view either individual results with a certificate or the complete final contest report.

## Features

### 1. Year Selection
- Dropdown populated from `CONTEST_YEARS` config
- Required for both individual and final report viewing

### 2. Individual Results
User enters:
- Contest year
- Callsign

Displays:
- **Certificate of Achievement** (printable separately)
- **Score & Statistics** (printable separately)

### 3. Final Contest Report
- Shows complete leaderboards for selected year
- Reads from `final_report_{year}.html` file
- Single print button for entire report

## Certificate Generation

The certificate is dynamically generated from database results and includes:

### Design Elements
- Green decorative border (matching Louisiana theme)
- "Jefferson Amateur Radio Club" header (not "Louisiana Contest Club")
- Fleur-de-lis graphics (Louisiana symbol)
- Large callsign in green
- Contest year and score
- Rankings in long-form descriptions

### Rankings Display
Rankings use full descriptions from `RANKINGS` dict:

```python
# Database: {'NQ': 1, 'LFQ': 3}
# Display:
#   #1 Non Louisiana - QRP Power
#   #3 Louisiana - Fixed QRP Power
```

### Images
- **Fleur-de-lis**: `/static/images/fleur.svg` (decorative)
- **Club logo**: `/static/images/sticker2.png` (bottom right)
- **Signature placeholder**: Gray box (bottom left) - replace with actual signature graphic later

## File Structure

```
templates/
└── results_lookup.html         # Main results page

static/
├── css/
│   ├── upload.css             # Shared styles
│   └── results.css            # Results-specific styles
├── js/
│   └── results_lookup.js      # Results functionality
└── images/
    ├── fleur.svg              # Fleur-de-lis graphic
    └── sticker2.png           # Club logo

laqp/data/results/
└── final_report_2026.html     # Final reports by year
```

## Configuration Required

### In config/config.py

```python
# Years available for results lookup
CONTEST_YEARS = ['2026', '2025', '2024', '2023']

# Rankings dict (maps codes to descriptions)
RANKINGS = {
    'LFQ': 'Louisiana - Fixed QRP Power',
    'NQ': 'Non Louisiana - QRP Power',
    # ... all ranking categories
}

# Directory for final reports
FINAL_REPORTS_DIR = 'laqp/data/results'
```

## API Endpoints

### POST /api/individual_results
Get individual results and certificate data.

**Request:**
```json
{
    "year": "2026",
    "callsign": "K5ABC"
}
```

**Response:**
```json
{
    "success": true,
    "result": {
        "callsign": "K5ABC",
        "year": "2026",
        "final_score": 1250,
        "rankings": {"NQ": 1, "NS": 2},
        // ... all result fields
    },
    "rankings_display": [
        "#1 Non Louisiana - QRP Power",
        "#2 Non Louisiana - SSB (phone) Mode"
    ]
}
```

### GET /api/final_report/{year}
Get final contest report HTML.

**Response:**
```json
{
    "success": true,
    "html": "<h2>Final Results...</h2>..."
}
```

## Printing

Three separate print functions:

### 1. Print Certificate Only
```javascript
printCertificate()
```
Hides everything except certificate section.

### 2. Print Statistics Only
```javascript
printStatistics()
```
Hides everything except statistics section.

### 3. Print Final Report
```javascript
printFinalReport()
```
Hides everything except final report section.

## Usage Flow

### Individual Results

```
1. User selects year: 2026
2. User enters callsign: K5ABC
3. Clicks "Show My Results"
4. System:
   - Queries database for (2026, K5ABC)
   - Gets rankings dict: {"NQ": 1, "NS": 2}
   - Looks up full descriptions in RANKINGS
   - Generates certificate HTML
   - Formats statistics HTML
5. Displays:
   - Certificate (with print button)
   - Statistics (with print button)
```

### Final Report

```
1. User selects year: 2026
2. Clicks "Show Final Report"
3. System:
   - Reads laqp/data/results/final_report_2026.html
   - Extracts content
   - Displays in page
4. Shows report with print button
```

## Generating Final Report HTML

The final report should be generated after rankings are calculated:

```python
from leaderboards import generate_leaderboards
from config.config import LEADERBOARDS, RANKINGS

# Generate leaderboards
sections = generate_leaderboards('2026', LEADERBOARDS, RANKINGS)

# Convert to HTML
html = generate_final_report_html(sections, '2026')

# Save to file
with open('laqp/data/results/final_report_2026.html', 'w') as f:
    f.write(html)
```

(HTML generation function to be created)

## Styling

### Certificate
- Green border (Louisiana theme)
- Professional certificate layout
- Large callsign (3.5rem, green)
- Contest name in blue
- Rankings prominently displayed

### Print Styles
- Hides navigation, buttons, and forms
- Clean certificate on white background
- Page breaks avoided within certificate
- Separate print styles for each section

## Testing

### Test Individual Results

```bash
# 1. Ensure database has data
python batch.py

# 2. Generate rankings
python generate_rankings.py 2026

# 3. Start web server
python web.py

# 4. Visit
http://localhost:5000/results

# 5. Select year: 2026, callsign: K5ABC
# 6. Click "Show My Results"
# 7. Verify certificate and statistics display
```

### Test Final Report

```bash
# 1. Generate final report HTML (to be implemented)
python generate_final_report.py 2026

# 2. Visit /results
# 3. Select year: 2026
# 4. Click "Show Final Report"
# 5. Verify leaderboards display
```

## Customization

### Update Certificate Header
Edit `results_lookup.js`:
```javascript
<div class="certificate-org">Your Club Name Here</div>
```

### Change Certificate Colors
Edit `results.css`:
```css
.certificate-callsign {
    color: #008000;  /* Change green */
}

.certificate-contest {
    color: #0000CD;  /* Change blue */
}
```

### Add Club Logo
Replace `/static/images/sticker2.png` with your logo.

### Add Signature
Replace the signature placeholder:
```javascript
<div class="certificate-signature">
    <img src="/static/images/signature.png" alt="Signature">
</div>
```

## Next Steps

1. ✅ Results page created
2. ✅ Certificate generation implemented
3. ✅ Individual results API
4. ✅ Final report API
5. ⬜ Generate final report HTML script
6. ⬜ Add actual signature graphic
7. ⬜ Test with real data
8. ⬜ Deploy to production

## Files Created/Modified

- ✅ `templates/results_lookup.html` - Results page
- ✅ `static/css/results.css` - Results styling
- ✅ `static/js/results_lookup.js` - Results functionality
- ✅ `static/images/fleur.svg` - Fleur-de-lis graphic
- ✅ `static/images/sticker2.png` - Club logo
- ✅ `web.py` - Added API routes
- ⬜ `generate_final_report.py` - To be created

The results page is ready for testing!
