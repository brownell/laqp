# Louisiana QSO Party - Web Log Upload Application

Single-page Flask application for contestants to upload and validate their contest logs.

## Features

- **Louisiana Contest Club Styling**: Matches the look and feel of https://laqp.louisianacontestclub.org
- **Real-time Validation**: Validates logs immediately upon upload
- **Dual Input Methods**: Upload file OR paste log text
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Form Validation**: Collects all required information (email, mode, power, station type, overlay)
- **Clear Feedback**: Shows success or detailed error messages

## File Structure

```
web/
├── app.py                      # Flask application
├── README.md                   # This file
├── static/
│   ├── css/
│   │   └── upload.css         # Styling (Louisiana Contest Club theme)
│   └── js/
│       └── upload.js          # Form handling and AJAX
└── templates/
    └── upload.html            # Main upload page
```

## Setup

### 1. Install Dependencies

```bash
pip install flask
```

(Flask is already in requirements.txt for the main project)

### 2. Run Development Server

```bash
# From the project root directory
cd web
python app.py
```

The application will start on http://localhost:5000

### 3. Access the Page

Open your browser to:
```
http://localhost:5000
```

## Production Deployment

### Option 1: Gunicorn (Linux/Mac)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Option 2: Apache/mod_wsgi

Create `web/wsgi.py`:
```python
import sys
sys.path.insert(0, '/path/to/laqp_processor/web')
from app import app as application
```

Apache configuration:
```apache
<VirtualHost *:80>
    ServerName laqp.yourdomain.com
    
    WSGIDaemonProcess laqp user=www-data group=www-data threads=5
    WSGIScriptAlias / /path/to/laqp_processor/web/wsgi.py
    
    <Directory /path/to/laqp_processor/web>
        WSGIProcessGroup laqp
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```

### Option 3: Nginx + Gunicorn

Nginx configuration:
```nginx
server {
    listen 80;
    server_name laqp.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/laqp_processor/web/static;
    }
}
```

## How It Works

### User Flow

1. **Contestant arrives at page**
   - Sees form matching Louisiana Contest Club styling
   - Banner says "Sponsored by the Jefferson Amateur Radio Club - w5gad.org"

2. **Fills out required information**
   - Email address
   - Mode category (Mixed, CW/Digital Only, Phone Only)
   - Overlay category (None, Wires, TB-Wires, POTA)
   - Power level (QRP, Low, High)
   - Station type (Fixed, Rover)

3. **Submits log**
   - Either uploads .log/.txt/.cbr file
   - OR pastes Cabrillo text into textarea
   - Cannot do both (JavaScript prevents this)

4. **Backend validates log**
   - Uses existing `laqp.core.validator` module
   - Checks Cabrillo format
   - Validates all QSO lines
   - Checks dates/times, frequencies, modes, callsigns

5. **Result displayed**
   - **Success**: Green box, shows callsign and QSO count, log saved to `logs/incoming/`
   - **Error**: Red box, lists all validation errors, log NOT saved

### Technical Details

**Form Validation**:
- Required fields checked client-side (HTML5) and server-side
- File type restricted to .log, .txt, .cbr
- Max upload size: 5MB (configurable in config.py)

**Log Storage**:
- Temporary file created during validation
- If valid: moved to `logs/incoming/` with proper filename
- If invalid: deleted immediately
- Duplicate filenames handled by adding number suffix

**Security**:
- Filename sanitization using `werkzeug.utils.secure_filename`
- HTML escaping in JavaScript to prevent XSS
- CSRF protection via Flask secret key
- File type restrictions

**Responsive Design**:
- Desktop (>768px): Full width form, horizontal radio buttons
- Tablet (768px-480px): Slightly compressed, radio buttons stack
- Mobile (<480px): Fully stacked layout, touch-friendly buttons

## Styling Notes

The CSS matches the Louisiana Contest Club website:
- **Background**: #f5efe0 (cream)
- **Primary text**: #000 (black)
- **Accent color**: #cd2653 (red)
- **Secondary text**: #6d6d6d (gray)
- **Font**: -apple-system, BlinkMacSystemFont, "Helvetica Neue"
- **HR style**: Custom styled-separator with crossed bars (from TwentyTwenty theme)

## Customization

### Change Banner Text

Edit `web/templates/upload.html` line with class `site-description`:
```html
<p class="site-description">
    Your custom text here - <a href="https://example.com">link</a>
</p>
```

### Change Accent Color

Edit `web/static/css/upload.css`:
```css
/* Find all instances of #cd2653 and replace with your color */
```

### Add Logo

Add to header in `upload.html`:
```html
<div class="site-logo">
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
</div>
```

## Testing

### Test with Sample Log

Create `test_log.txt`:
```
START-OF-LOG: 3.0
CALLSIGN: W5TEST
CONTEST: LA-QSO-PARTY
CATEGORY-OPERATOR: SINGLE-OP
CATEGORY-POWER: LOW
CATEGORY-STATION: FIXED
EMAIL: test@example.com
QSO: 7040 CW 2025-04-05 1430 W5TEST 599 GA N5XX 599 ORLE
QSO: 14255 PH 2025-04-05 1445 W5TEST 59 GA W5XX 59 JEFF
END-OF-LOG:
```

Upload this file through the web interface - it should be accepted.

### Test with Invalid Log

Remove the `CATEGORY-POWER:` line - it should be rejected with an error message.

## Troubleshooting

**Problem**: "Internal Server Error"
- **Solution**: Check Flask console for error messages, ensure all dependencies installed

**Problem**: Uploaded files not appearing in `logs/incoming/`
- **Solution**: Check directory permissions, ensure `config.ensure_directories()` ran

**Problem**: Styling looks wrong
- **Solution**: Check browser console for 404 on CSS file, verify static files path

**Problem**: Form submission does nothing
- **Solution**: Check browser console for JavaScript errors, verify `/upload` endpoint is working

## Future Enhancements

Possible additions:
- Email confirmation after successful upload
- Upload progress bar for large files
- Duplicate detection (warn if callsign already uploaded)
- Score estimation (show approximate score after validation)
- Previous submissions list (if user cookies enabled)
- Admin dashboard to view all submissions

## Support

Questions or issues? Contact questions@laqp.org
