"""
Louisiana QSO Party - Log Upload Flask Application

Simple single-page app for contestants to upload and validate their logs.
"""
import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    INCOMING_LOGS, LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    FLASK_SECRET_KEY, MAX_UPLOAD_SIZE, ensure_initial_directories
)
from laqp.core.validator import validate_single_log

# Create Flask app
app = Flask(__name__, 
    static_folder='/var/www/laqp/static',
    static_url_path='/static')
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# Ensure directories exist
ensure_initial_directories()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'log', 'txt', 'cbr', 'LOG', 'TXT', 'CBR'}

def allowed_file(filename):
    """Check if filename has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Main upload page"""
    return render_template('upload.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['POST'])
def upload_log():
    """Handle log file upload and validation"""
    
    # Get form data
    email = request.form.get('email', '').strip()
    mode_category = request.form.get('mode_category', '')
    overlay = request.form.get('overlay', '')
    power = request.form.get('power', '')
    station_type = request.form.get('station_type', '')
    
    # Validate form fields
    errors = []
    if not email:
        errors.append("Email address is required")
    
    if not mode_category:
        errors.append("Mode category is required")
    
    if not power:
        errors.append("Power level is required")
    
    if not station_type:
        errors.append("Station category is required")
    
    # Check if file was uploaded or pasted
    log_file = request.files.get('log_file')
    log_text = request.form.get('log_text', '').strip()
    
    if not log_file and not log_text:
        errors.append("You must either upload a log file OR paste your log, but not both")
    
    if log_file and log_text:
        errors.append("Please use either file upload OR paste, not both")
    
    # If errors, return them
    if errors:
        return jsonify({
            'success': False,
            'errors': errors
        }), 400
    
    # Process the log
    temp_log_path = None
    
    try:
        # Save log to temporary file
        if log_file:
            # From uploaded file
            if not allowed_file(log_file.filename):
                return jsonify({
                    'success': False,
                    'errors': ['Invalid file type. Please upload .log, .txt, or .cbr files']
                }), 400
            
            filename = secure_filename(log_file.filename)
            temp_log_path = INCOMING_LOGS / f"temp_{filename}"
            log_file.save(str(temp_log_path))
        else:
            # From pasted text
            # Try to extract callsign from log for filename
            callsign = "UNKNOWN"
            for line in log_text.split('\n'):
                if line.upper().startswith('CALLSIGN:'):
                    callsign = line.split(':', 1)[1].strip()
                    break
            
            filename = f"{callsign}.log"
            temp_log_path = INCOMING_LOGS / f"temp_{filename}"
            with open(temp_log_path, 'w', encoding='utf-8') as f:
                f.write(log_text)
        
        # Validate the log
        validation_result = validate_single_log(
            True,
            temp_log_path,
            LA_PARISHES_FILE,
            WVE_ABBREVS_FILE
        )
        
        if validation_result.is_valid:
            # Log is valid - rename from temp to final
            final_path = INCOMING_LOGS / filename
            
            # overwrite existing files
            name_part = filename.rsplit('.', 1)[0]
            ext_part = filename.rsplit('.', 1)[1] if '.' in filename else 'log'
            final_path = INCOMING_LOGS / f"{name_part}.{ext_part}"
            
            temp_log_path.rename(final_path)
            
            return jsonify({
                'success': True,
                'message': f'Your log has been accepted! Callsign: {validation_result.callsign}',
                'callsign': validation_result.callsign,
                'qso_count': validation_result.qso_count,
                'warnings': validation_result.warnings
            })
        else:
            # Log is invalid
            # Delete temp file
            if temp_log_path and temp_log_path.exists():
                temp_log_path.unlink()
            
            return jsonify({
                'success': False,
                'errors': validation_result.errors,
                'warnings': validation_result.warnings,
                'qso_count': validation_result.qso_count,
                'invalid_qso_count': validation_result.invalid_qso_count
            }), 400
    
    except Exception as e:
        # Clean up temp file on error
        if temp_log_path and temp_log_path.exists():
            temp_log_path.unlink()
        
        return jsonify({
            'success': False,
            'errors': [f'Error processing log: {str(e)}']
        }), 500


if __name__ == '__main__':
    # Development mode (testing only)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    
    # Production mode
    app.run(host='0.0.0.0', port=5000, debug=False)
