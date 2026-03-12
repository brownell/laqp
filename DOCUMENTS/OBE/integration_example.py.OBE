#!/usr/bin/env python3
"""
Example: Integrating validate_single_log with the Flask App

This file shows how to modify your existing validate_single_log function
to work with the HTML results display.
"""

# EXAMPLE: Your existing validator function might look like this
def validate_single_log_OLD(log_path):
    """
    OLD VERSION - Returns just the result dict
    """
    # ... your validation code ...
    
    result = {
        'callsign': 'K5ABC',
        'category': 'nl_ph_lo',
        # ... all fields ...
    }
    
    return result


# UPDATED: Modify it to return success status and errors
def validate_single_log(log_path):
    """
    UPDATED VERSION - Returns dict with success flag and errors
    
    This is what the Flask app expects.
    """
    try:
        # Your existing validation code here
        # ...
        
        # Initialize result dictionary
        result = {
            'callsign': '',
            'category': '',
            'overlay': None,
            'location_type': 'NON-LA',
            'mode_category': 'Mixed',
            'power_level': 'Low',
            'final_score': 0,
            'qso_points': 0,
            'total_qsos': 0,
            'valid_qsos': 0,
            'total_multipliers': 0,
            'parishes_worked': set(),
            'parishes_worked_multiplier': 0,
            'states_worked': set(),
            'states_worked_multiplier': 0,
            'provinces_worked': set(),
            'provinces_multiplier': 0,
            'dx_worked': set(),
            'dx_worked_multiplier': 0,
            'parishes_activated': set(),
            'rover_bonus_points': 0,
            'worked_n5lcc': False,
            'num_n5lcc_contacts': 0,
            'qsos_by_band': {'160': 0, '80': 0, '40': 0, '20': 0, '15': 0, '10': 0, '6': 0, '2': 0},
            'qsos_by_mode': {'Phone': 0, 'CW/Digital': 0},
            'qsos_by_hour': {i: 0 for i in range(12)},
            'bands_worked': [],
            'multipliers_by_band_mode': {},
            'name': '',
            'claimed_score': 0,
        }
        
        # Your validation logic here
        # Parse log file, validate QSOs, calculate scores, etc.
        # ...
        
        # If validation finds errors, collect them
        validation_errors = []
        
        # Example validation checks
        if not result['callsign']:
            validation_errors.append('Missing CALLSIGN field in log header')
        
        if result['total_qsos'] == 0:
            validation_errors.append('No valid QSOs found in log')
        
        # Add more validation checks as needed
        # ...
        
        # If there are errors, return failure
        if validation_errors:
            return {
                'success': False,
                'errors': validation_errors
            }
        
        # Otherwise return success with all result data
        result['success'] = True
        return result
        
    except Exception as e:
        # Handle any unexpected errors
        return {
            'success': False,
            'errors': [f'Validation error: {str(e)}']
        }


# ALTERNATIVE: Wrapper function if you don't want to modify original
def validate_single_log_wrapper(log_path):
    """
    WRAPPER APPROACH - Wrap your existing function
    
    Use this if you want to keep your original validate_single_log unchanged
    """
    try:
        # Call your existing function
        result = validate_single_log_OLD(log_path)
        
        # Add success flag
        result['success'] = True
        
        return result
        
    except ValidationError as e:
        # If your validator raises exceptions, catch them here
        return {
            'success': False,
            'errors': [str(e)]
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [f'Unexpected error: {str(e)}']
        }


# EXAMPLE: Custom validation error class
class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


# EXAMPLE: Function that validates individual fields
def validate_log_header(log_lines):
    """
    Example helper function to validate log header fields
    """
    errors = []
    required_fields = ['START-OF-LOG', 'CALLSIGN', 'CONTEST', 'CATEGORY']
    
    header_fields = {}
    for line in log_lines:
        if line.startswith('END-OF-LOG'):
            break
        if ':' in line:
            field, value = line.split(':', 1)
            header_fields[field.strip()] = value.strip()
    
    for field in required_fields:
        if field not in header_fields:
            errors.append(f'Missing required header field: {field}')
    
    return errors, header_fields


# EXAMPLE: Function that validates QSO lines
def validate_qso_lines(log_lines):
    """
    Example helper function to validate QSO records
    """
    errors = []
    qso_count = 0
    
    for i, line in enumerate(log_lines, 1):
        if not line.startswith('QSO:'):
            continue
        
        qso_count += 1
        fields = line.split()
        
        # Basic validation
        if len(fields) < 10:
            errors.append(f'QSO line {i}: Insufficient fields')
            continue
        
        # Validate frequency
        try:
            freq = int(fields[1])
            if freq < 1800 or freq > 450000:
                errors.append(f'QSO line {i}: Invalid frequency {freq}')
        except ValueError:
            errors.append(f'QSO line {i}: Non-numeric frequency')
        
        # Add more validation as needed
        # ...
    
    if qso_count == 0:
        errors.append('No QSO records found in log')
    
    return errors


# EXAMPLE: Complete validation function with all checks
def validate_single_log_complete_example(log_path):
    """
    Complete example showing full validation workflow
    """
    try:
        # Read log file
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_lines = [line.strip() for line in f if line.strip()]
        
        # Validate header
        header_errors, header_fields = validate_log_header(log_lines)
        
        # Validate QSO lines
        qso_errors = validate_qso_lines(log_lines)
        
        # Combine all errors
        all_errors = header_errors + qso_errors
        
        # If there are errors, return them
        if all_errors:
            return {
                'success': False,
                'errors': all_errors
            }
        
        # Process log and build result dictionary
        result = process_log_file(log_path, header_fields, log_lines)
        result['success'] = True
        
        return result
        
    except FileNotFoundError:
        return {
            'success': False,
            'errors': ['Log file not found']
        }
    except PermissionError:
        return {
            'success': False,
            'errors': ['Permission denied reading log file']
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [f'Unexpected error: {str(e)}']
        }


def process_log_file(log_path, header_fields, log_lines):
    """
    Example function that processes log and builds result dict
    This is where your scoring logic would go
    """
    result = {
        'callsign': header_fields.get('CALLSIGN', ''),
        'category': header_fields.get('CATEGORY', ''),
        'overlay': header_fields.get('OVERLAY'),
        'name': header_fields.get('NAME', ''),
        'claimed_score': int(header_fields.get('CLAIMED-SCORE', 0)),
        # Initialize other fields
        'location_type': 'NON-LA',
        'mode_category': 'Mixed',
        'power_level': 'Low',
        'final_score': 0,
        'qso_points': 0,
        'total_qsos': 0,
        'valid_qsos': 0,
        'total_multipliers': 0,
        'parishes_worked': set(),
        'parishes_worked_multiplier': 0,
        'states_worked': set(),
        'states_worked_multiplier': 0,
        'provinces_worked': set(),
        'provinces_multiplier': 0,
        'dx_worked': set(),
        'dx_worked_multiplier': 0,
        'parishes_activated': set(),
        'rover_bonus_points': 0,
        'worked_n5lcc': False,
        'num_n5lcc_contacts': 0,
        'qsos_by_band': {'160': 0, '80': 0, '40': 0, '20': 0, '15': 0, '10': 0, '6': 0, '2': 0},
        'qsos_by_mode': {'Phone': 0, 'CW/Digital': 0},
        'qsos_by_hour': {i: 0 for i in range(12)},
        'bands_worked': [],
        'multipliers_by_band_mode': {},
    }
    
    # Process each QSO line
    for line in log_lines:
        if not line.startswith('QSO:'):
            continue
        
        # Parse QSO and update result dict
        # Your scoring logic here
        # ...
    
    # Calculate final scores
    result['final_score'] = result['qso_points'] * result['total_multipliers']
    
    return result


# USAGE IN app.py:
"""
# Import your validator
from your_module import validate_single_log

# In the /upload route:
result = validate_single_log(tmp_path)

if result.get('success', True):
    # Success - format and display results
    display_result = format_result_for_display(result)
    return jsonify({
        'success': True,
        'message': 'Log validated successfully!',
        'result': display_result
    })
else:
    # Validation failed - show errors
    return jsonify({
        'success': False,
        'error': 'Log validation failed',
        'errors': result.get('errors', [])
    }), 400
"""
