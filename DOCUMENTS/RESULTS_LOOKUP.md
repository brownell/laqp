# Louisiana QSO Party - Results Lookup Feature

This feature allows contestants to look up their past contest results by entering their callsign and contest year.

## How It Works

### User Flow

1. User visits `/results` page
2. Enters their callsign (e.g., K5ABC)
3. Selects contest year (2023-2026)
4. Clicks "Look Up Results"
5. Their results display directly on the same page
6. User can print results using the print button

### Technical Flow

```
User submits form
    ↓
JavaScript sends AJAX request to /lookup_results
    ↓
Flask looks for HTML_RESULTS/{year}/{callsign}_results.html
    ↓
If found: Extract results content and return as JSON
    ↓
JavaScript displays content in results div
```

## File Organization

Results are organized by year:

```
HTML_RESULTS/
├── 2026/
│   ├── K5ABC_results.html
│   ├── W5XYZ_results.html
│   └── ...
├── 2025/
│   ├── K5ABC_results.html
│   └── ...
└── 2024/
    └── ...
```

## Setup

### 1. Generate HTML Results (Batch Processing)

When processing logs in batch mode, generate HTML files organized by year:

```python
from processor import process_batch_logs
from html_results import generate_all_html_results

# Process logs
results = process_batch_logs(Path('logs/incoming'))

# Filter valid results
valid_results = [r for r in results if r['is_valid']]

# Generate HTML files for 2026 contest
html_files = generate_all_html_results(
    valid_results, 
    output_dir=Path('HTML_RESULTS'),
    year='2026'  # ← Specify year
)

# Results will be saved to: HTML_RESULTS/2026/
```

### 2. Configure Flask App

Ensure your Flask app can access the HTML_RESULTS directory:

```python
# app.py already configured to look for:
# HTML_RESULTS/{year}/{callsign}_results.html
```

### 3. Add Years to Dropdown

Edit `templates/results.html` to add new years:

```html
<select id="year" name="year" required>
    <option value="">Select year...</option>
    <option value="2027">2027</option>  <!-- Add new year -->
    <option value="2026">2026</option>
    <option value="2025">2025</option>
    <option value="2024">2024</option>
</select>
```

## Routes

### GET /results
Displays the results lookup form page.

### POST /lookup_results
Looks up results for a callsign and year.

**Request:**
```json
{
    "callsign": "K5ABC",
    "year": "2026"
}
```

**Success Response:**
```json
{
    "success": true,
    "html": "<div class='result-group'>...</div>"
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "No results found for K5ABC in 2026"
}
```

## Features

### Auto-Uppercase Callsign
The callsign field automatically converts to uppercase as the user types.

### Loading Indicator
Shows a spinner while looking up results.

### Error Handling
- Missing callsign or year
- Results not found
- Server errors

### Print Functionality
Print button shows after results are displayed. Uses the same print-friendly CSS as the upload page.

### Responsive Design
Works on desktop, tablet, and mobile devices.

## Styling

Uses the same CSS (`upload.css`) as the upload page for consistency:
- Louisiana Contest Club theme
- Dark red (#8B0000) headers
- Cream background (#f5f5dc)
- Print-friendly styles

## Security Considerations

### Filename Sanitization
Callsigns with slashes (e.g., portable/mobile indicators) are sanitized:
```python
safe_callsign = callsign.replace('/', '_')
```

### Path Traversal Prevention
The Flask route only allows lookups within the HTML_RESULTS directory structure.

### Input Validation
- Callsign required
- Year required
- Year must be from dropdown (2023-2026)

## Testing

### 1. Generate Test Results

```python
# Create a test result
test_result = {
    'callsign': 'K5TEST',
    'category': 'nl_ph_lo',
    'final_score': 1000,
    # ... other fields
}

# Generate HTML
from html_results import generate_html_result
html_file = generate_html_result(test_result, Path('HTML_RESULTS'), year='2026')
print(f"Created: {html_file}")
```

### 2. Test Lookup

1. Start Flask app: `python app.py`
2. Visit: http://localhost:5000/results
3. Enter: Callsign = K5TEST, Year = 2026
4. Click "Look Up Results"
5. Verify results display correctly

### 3. Test Error Cases

- Missing callsign → Shows error
- Missing year → Shows error
- Callsign not found → Shows "No results found" message
- Invalid year → Year must be from dropdown

## Customization

### Change Default Year

Update both places:
1. `html_results.py` - default parameter
2. `templates/results.html` - dropdown selected value

### Add More Years

Edit `templates/results.html`:
```html
<option value="2027">2027</option>
<option value="2026" selected>2026</option>  <!-- default -->
```

### Change Results Directory

Update both:
1. `app.py` - line with `HTML_RESULTS/{year}/`
2. `html_results.py` - default parameter

### Customize Messages

Edit `static/js/results.js`:
```javascript
showMessage('Custom error message', 'error');
```

## Integration with Existing Features

### Link from Upload Page
The upload page footer now includes a link to view past results:
```html
<a href="/results">View Past Results →</a>
```

### Link from Results Page
The results page footer includes a link back to submission:
```html
<a href="/">← Back to Log Submission</a>
```

## Troubleshooting

### "No results found"
1. Check that HTML file exists: `HTML_RESULTS/2026/K5ABC_results.html`
2. Check callsign matches filename (case-sensitive in filenames)
3. Check year is correct

### Results Don't Display
1. Check browser console for JavaScript errors
2. Check Flask logs for server errors
3. Verify HTML content is being returned in JSON

### Styling Issues
1. Verify `upload.css` is accessible
2. Check browser cache (hard refresh: Ctrl+Shift+R)
3. Verify CSS path in `results.html`

## Future Enhancements

Possible additions:
- [ ] Search by name in addition to callsign
- [ ] Show leaderboard/rankings
- [ ] Download results as PDF
- [ ] Compare results across years
- [ ] Category filtering
- [ ] Email results to contestant

## Example Complete Workflow

```python
# 1. Process logs for 2026 contest
from processor import process_batch_logs
from html_results import generate_all_html_results

results = process_batch_logs(Path('logs/2026/incoming'))
valid = [r for r in results if r['is_valid']]

# 2. Generate HTML files
html_files = generate_all_html_results(valid, Path('HTML_RESULTS'), year='2026')

# 3. Start web server
# python app.py

# 4. Users can now look up their 2026 results at:
# http://yourserver.com/results
```

## Files Modified/Created

- ✅ `app.py` - Added `/results` and `/lookup_results` routes
- ✅ `templates/results.html` - New results lookup page
- ✅ `static/js/results.js` - New JavaScript for lookup
- ✅ `html_results.py` - Updated to support year parameter
- ✅ `templates/upload.html` - Added link to results page

All files use the existing CSS (`upload.css`) - no additional styling needed!
