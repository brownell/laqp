# Louisiana QSO Party - HTML Results Implementation
## Deployment Guide

This package contains all the files needed to convert your log upload system from DOCX output to HTML display with in-browser results and print functionality.

---

## 📦 What's Included

### Core Application Files
- **app.py** - Flask application with result formatting
- **requirements.txt** - Python dependencies
- **README.md** - Complete documentation

### Templates
- **templates/upload.html** - HTML page with form and results display

### Static Files
- **static/css/upload.css** - Stylesheet with Louisiana Contest Club theme
- **static/js/upload.js** - JavaScript for AJAX submission and results rendering

### Helper Files
- **integration_example.py** - Examples of integrating with your validator
- **test_app.py** - Test suite to verify installation

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the Installation
```bash
python test_app.py
```

### 3. Integrate Your Validator

Edit `app.py` around line 170:

**Replace this:**
```python
# MOCK VALIDATION FOR TESTING
result = {
    'success': True,
    # ... mock data ...
}
```

**With this:**
```python
from laqp.core.validator import validate_single_log
result = validate_single_log(tmp_path)
```

### 4. Update Your validate_single_log Function

Your validator should return:

**Success:**
```python
{
    'success': True,
    'callsign': 'K5ABC',
    'category': 'nl_ph_lo',
    # ... all other result fields ...
}
```

**Failure:**
```python
{
    'success': False,
    'errors': [
        'Error message 1',
        'Error message 2',
    ]
}
```

See **integration_example.py** for detailed examples.

### 5. Run the Application
```bash
python app.py
```

Visit: http://localhost:5000

---

## 📋 Result Dict Structure

The application expects these fields in your result dictionary:

### Station Information
- `callsign` - Station callsign
- `name` - Operator name
- `category` - Short category name (e.g., 'nl_ph_lo')
- `overlay` - Overlay category ('WIRES', 'TB-WIRES', 'POTA', or None)
- `location_type` - 'NON-LA', 'LA Fixed', or 'LA Rover'
- `mode_category` - 'Phone', 'CW', 'Digital', or 'Mixed'
- `power_level` - 'QRP', 'Low', or 'High'

### Scores
- `final_score` - Total score with bonuses
- `qso_points` - Points from QSOs only
- `claimed_score` - Operator's claimed score
- `total_multipliers` - Total multiplier count

### QSO Statistics
- `total_qsos` - Total number of QSOs
- `valid_qsos` - Number of valid QSOs for scoring
- `qsos_by_band` - Dict: {'160': 0, '80': 45, '40': 123, ...}
- `qsos_by_mode` - Dict: {'Phone': 313, 'CW/Digital': 0}
- `qsos_by_hour` - Dict: {0: 28, 1: 35, 2: 42, ...}
- `bands_worked` - List: ['80', '40', '20', '15']

### Multipliers (for NON-LA stations)
- `parishes_worked` - Set: {'ORL', 'JEF', 'STB', 'PLQ', 'TAN'}
- `parishes_worked_multiplier` - Count

### Multipliers (for LA stations)
- `states_worked` - Set
- `states_worked_multiplier` - Count
- `provinces_worked` - Set
- `provinces_multiplier` - Count
- `dx_worked` - Set
- `dx_worked_multiplier` - Count

### Multipliers Detail
- `multipliers_by_band_mode` - Dict: {'40-Phone': {'ORL', 'JEF'}, ...}

### Bonuses
- `worked_n5lcc` - Boolean
- `num_n5lcc_contacts` - Count
- `parishes_activated` - Set (for rovers)
- `rover_bonus_points` - Points

---

## 🎨 Key Features

### Processing Flow
1. User fills form and uploads/pastes log
2. JavaScript shows loading spinner
3. Flask validates and processes log
4. Results displayed in organized sections
5. Print button allows browser printing

### Results Display Sections
- Station Information
- Score Summary
- QSO Statistics
- QSOs by Band (table)
- QSOs by Mode (table)
- QSOs by Hour (table)
- Multipliers (with lists of worked entities)
- Multipliers by Band/Mode (grid of cards)
- Bonuses
- Bands Worked

### Error Handling
- Form validation before submission
- Server-side validation with detailed errors
- User-friendly error messages
- Option to resubmit after corrections

### Print Functionality
- Hides form when printing
- Shows only results section
- Maintains formatting
- Works with all major browsers

---

## 🔧 Customization

### Colors and Styling
Edit `static/css/upload.css`:
- Change `#8B0000` to your preferred dark red shade
- Modify fonts (currently Georgia)
- Adjust spacing and layout

### Field Labels
Edit `static/js/upload.js`:
- Modify labels in `generateResultsHTML()` function
- Change section headers
- Customize value formatting

### Form Fields
Edit `templates/upload.html`:
- Add/remove form fields
- Modify dropdown options
- Change required fields

---

## 🚢 Production Deployment

### With Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### With Systemd
Create `/etc/systemd/system/laqp-web.service`:
```ini
[Unit]
Description=Louisiana QSO Party Web Service
After=network.target

[Service]
Type=notify
User=your-user
WorkingDirectory=/path/to/app
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

### With Nginx
```nginx
server {
    listen 443 ssl;
    server_name laqp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
    }
}
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in app.py
- [ ] Set appropriate file size limits
- [ ] Configure allowed file extensions
- [ ] Use HTTPS in production
- [ ] Set up proper file permissions
- [ ] Configure firewall rules
- [ ] Enable rate limiting if needed

---

## 🐛 Troubleshooting

### Results not displaying
1. Check browser console for errors
2. Verify JSON response from `/upload`
3. Check Flask logs

### Styling issues
1. Hard refresh (Ctrl+Shift+R)
2. Check static file paths
3. Verify Flask static folder config

### Print not working
1. Check print media query in CSS
2. Test in different browser
3. Verify results section is visible

---

## 📞 Support

If you encounter issues:

1. Run the test suite: `python test_app.py`
2. Check the README.md for detailed docs
3. Review integration_example.py for validator examples
4. Check Flask logs for error messages

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Run test suite
3. ⬜ Integrate your validator
4. ⬜ Test with real log files
5. ⬜ Customize styling if needed
6. ⬜ Deploy to production

---

## 📝 Notes

- The mock validation data in app.py is for testing only
- All sets are automatically converted to sorted lists for display
- JSON serialization is handled automatically
- Print functionality works with all modern browsers
- Responsive design works on mobile devices

---

**Created for the Louisiana QSO Party**
**Jefferson Amateur Radio Club**
**2026**
