#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Web interface for contestants to submit and validate Cabrillo log files
"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile

# Import your existing validation module
# Adjust the import path based on your project structure
# from laqp.core.validator import validate_single_log

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = 'logs/incoming'
app.config['ALLOWED_EXTENSIONS'] = {'log', 'txt', 'cbr'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def format_set_as_list(s):
    """Convert set to sorted list for display"""
    if not s:
        return []
    return sorted(list(s))


def format_multipliers_by_band_mode(mult_dict):
    """Format the multipliers_by_band_mode dictionary for display"""
    if not mult_dict:
        return []
    
    result = []
    for key, value in sorted(mult_dict.items()):
        result.append({
            'band_mode': key,
            'multipliers': sorted(list(value)) if isinstance(value, set) else value
        })
    return result


def format_result_for_display(result):
    """
    Convert the result dictionary to a format suitable for HTML display
    Handles sets, dicts, and other complex types
    """
    display_result = {}
    
    # Copy simple values
    simple_fields = [
        'callsign', 'category', 'overlay', 'location_type', 'mode_category',
        'power_level', 'final_score', 'qso_points', 'total_qsos', 'valid_qsos',
        'total_multipliers', 'parishes_worked_multiplier', 'states_worked_multiplier',
        'provinces_multiplier', 'dx_worked_multiplier', 'rover_bonus_points',
        'worked_n5lcc', 'num_n5lcc_contacts', 'name', 'claimed_score'
    ]
    
    for field in simple_fields:
        display_result[field] = result.get(field, 'N/A')
    
    # Convert sets to sorted lists
    display_result['parishes_worked'] = format_set_as_list(result.get('parishes_worked', set()))
    display_result['states_worked'] = format_set_as_list(result.get('states_worked', set()))
    display_result['provinces_worked'] = format_set_as_list(result.get('provinces_worked', set()))
    display_result['dx_worked'] = format_set_as_list(result.get('dx_worked', set()))
    display_result['parishes_activated'] = format_set_as_list(result.get('parishes_activated', set()))
    display_result['bands_worked'] = result.get('bands_worked', [])
    
    # Format QSOs by band
    qsos_by_band = result.get('qsos_by_band', {})
    display_result['qsos_by_band'] = [
        {'band': band, 'count': count}
        for band, count in sorted(qsos_by_band.items(), key=lambda x: x[0])
    ]
    
    # Format QSOs by mode
    qsos_by_mode = result.get('qsos_by_mode', {})
    display_result['qsos_by_mode'] = [
        {'mode': mode, 'count': count}
        for mode, count in qsos_by_mode.items()
    ]
    
    # Format QSOs by hour
    qsos_by_hour = result.get('qsos_by_hour', {})
    display_result['qsos_by_hour'] = [
        {'hour': hour, 'count': count}
        for hour, count in sorted(qsos_by_hour.items())
    ]
    
    # Format multipliers by band/mode
    display_result['multipliers_by_band_mode'] = format_multipliers_by_band_mode(
        result.get('multipliers_by_band_mode', {})
    )
    
    return display_result


@app.route('/')
def home():
    """Render the log upload page"""
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_log():
    """
    Handle log file upload and validation
    Returns JSON response with validation results and formatted data
    """
    try:
        # Get form data
        email = request.form.get('email', '').strip()
        mode = request.form.get('mode', '').strip()
        power = request.form.get('power', '').strip()
        station_type = request.form.get('station_type', '').strip()
        overlay = request.form.get('overlay', '').strip()
        
        # Validate required fields
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email address is required'
            }), 400
        
        # Get log content (either from file or pasted text)
        log_content = None
        filename = None
        
        if 'logfile' in request.files:
            file = request.files['logfile']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                log_content = file.read().decode('utf-8', errors='ignore')
        
        if not log_content:
            log_text = request.form.get('log_text', '').strip()
            if log_text:
                log_content = log_text
                filename = f"pasted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        if not log_content:
            return jsonify({
                'success': False,
                'error': 'No log file provided. Please upload a file or paste log content.'
            }), 400
        
        # Save to temporary file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as tmp:
            tmp.write(log_content)
            tmp_path = tmp.name
        
        try:
            # TODO: Replace this with your actual validation function
            # result = validate_single_log(tmp_path)
            
            # MOCK VALIDATION FOR TESTING - Replace with actual validation
            # This simulates what your validate_single_log function should return
            result = {
                'success': True,  # or False if validation fails
                'errors': [],  # List of error messages if validation fails
                'callsign': 'K5ABC',
                'category': 'nl_ph_lo',
                'overlay': None,
                'location_type': 'NON-LA',
                'mode_category': 'Phone',
                'power_level': 'Low',
                'final_score': 1250,
                'qso_points': 625,
                'total_qsos': 350,
                'valid_qsos': 313,
                'total_multipliers': 2,
                'parishes_worked': {'ORL', 'JEF', 'STB', 'PLQ', 'TAN'},
                'parishes_worked_multiplier': 5,
                'states_worked': set(),
                'states_worked_multiplier': 0,
                'provinces_worked': set(),
                'provinces_multiplier': 0,
                'dx_worked': set(),
                'dx_worked_multiplier': 0,
                'parishes_activated': set(),
                'rover_bonus_points': 0,
                'worked_n5lcc': True,
                'num_n5lcc_contacts': 3,
                'qsos_by_band': {'160': 0, '80': 45, '40': 123, '20': 142, '15': 3, '10': 0, '6': 0, '2': 0},
                'qsos_by_mode': {'Phone': 313, 'CW/Digital': 0},
                'qsos_by_hour': {0: 28, 1: 35, 2: 42, 3: 38, 4: 31, 5: 29, 6: 26, 7: 24, 8: 22, 9: 18, 10: 12, 11: 8},
                'bands_worked': ['80', '40', '20', '15'],
                'multipliers_by_band_mode': {
                    '40-Phone': {'ORL', 'JEF', 'STB', 'PLQ'},
                    '20-Phone': {'ORL', 'JEF', 'TAN'},
                    '80-Phone': {'ORL', 'JEF'}
                },
                'name': 'John Smith',
                'claimed_score': 1250
            }
            
            if result.get('success', True):
                # Save the accepted log
                final_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(final_path, 'w') as f:
                    f.write(log_content)
                
                # Format the result for display
                display_result = format_result_for_display(result)
                
                return jsonify({
                    'success': True,
                    'message': 'Log file validated and accepted successfully!',
                    'result': display_result
                })
            else:
                # Validation failed
                errors = result.get('errors', ['Unknown validation error'])
                return jsonify({
                    'success': False,
                    'error': 'Log validation failed',
                    'errors': errors
                }), 400
                
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
