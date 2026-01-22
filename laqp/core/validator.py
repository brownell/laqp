"""
Louisiana QSO Party Log Validator - Enhanced Version

Validates Cabrillo log files for LAQP compliance AND checks that the log
matches the web form submission data.


Adapted from TQP statistics.py for LA rules created by Charles Sanders, NO5W

This version extends the base validator to cross-check:
- Email address in log vs. web form
- Mode category (Phone/CW-Digital/Mixed) in log vs. web form
- Power level (QRP/Low/High) in log vs. web form  
- Station type (Fixed/Rover) in log vs. web form
- Overlay category (None/Wires/TB-Wires/POTA) in log vs. web form
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# Import configuration and utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import (
    CONTEST_START_DAY1, CONTEST_END_DAY1,
    TIME_FORMAT, DATE_FORMAT,
    VALID_MODES,
    freq_to_band
)


class ValidationResult:
    """Holds validation results for a log"""
    def __init__(self, callsign: str):
        self.callsign = callsign
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.qso_count = 0
        self.invalid_qso_count = 0
        self.has_valid_power = True
        self.has_valid_operator = True
        self.has_email = False
        
        # Log header fields
        self.log_email = ""
        self.log_mode_category = ""  # PHONE-ONLY, CW/DIGITAL-ONLY, MIXED
        self.log_power = ""  # QRP, LOW, HIGH
        self.log_station = ""  # FIXED, ROVER
        self.log_overlay = ""  # WIRES, TB-WIRES, POTA, or empty
        
    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False
        
    def add_warning(self, message: str):
        self.warnings.append(message)
        
    def to_report(self) -> List[str]:
        """Generate a text report of validation results"""
        report = []
        report.append(f"Validation Report for {self.callsign}")
        report.append("=" * 60)
        report.append(f"Total QSOs: {self.qso_count}")
        report.append(f"Invalid QSOs: {self.invalid_qso_count}")
        report.append(f"Overall Status: {'VALID' if self.is_valid else 'INVALID'}")
        report.append("")
        
        if self.warnings:
            report.append("Warnings:")
            for warning in self.warnings:
                report.append(f"  - {warning}")
            report.append("")
        
        if self.errors:
            report.append("Errors:")
            for error in self.errors:
                report.append(f"  - {error}")
            report.append("")
        
        return report


class LogValidator:
    """Validates LAQP Cabrillo log files"""
    
    def __init__(self, upload, parish_list: List[str], state_province_list: List[str]):
        self.upload = upload
        self.parishes = set(p.upper() for p in parish_list)
        self.states_provinces = set(s.upper() for s in state_province_list)
        
    def validate_log_file(self, upload,
                         log_path: Path, 
                         form_email: Optional[str] = None,
                         form_mode: Optional[str] = None,
                         form_power: Optional[str] = None,
                         form_station: Optional[str] = None,
                         form_overlay: Optional[str] = None) -> ValidationResult:
        """
        Validate a log file and optionally check against web form data.
        
        Args:
            log_path: Path to the Cabrillo log file
            form_email: Email from web form (optional)
            form_mode: Mode category from web form: 'mixed', 'cw_digital', 'phone' (optional)
            form_power: Power level from web form: 'qrp', 'low', 'high' (optional)
            form_station: Station type from web form: 'fixed', 'rover' (optional)
            form_overlay: Overlay category from web form: 'none', 'wires', 'tb_wires', 'pota' (optional)
        
        Returns:
            ValidationResult object with validation status and any errors
        """
        result = ValidationResult("")
        
        has_start = False
        has_end = False
        has_power = False
        has_operator = False
        
        qso_modes = set()  # Track which modes are actually used
        
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip().upper()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                tag = parts[0]
                
                # ===== HEADER VALIDATION =====
                
                if tag == "START-OF-LOG:":
                    has_start = True
                    if len(parts) < 2 or parts[1] != "3.0":
                        result.add_warning(f"Line {line_num}: Expected START-OF-LOG: 3.0")
                
                elif tag == "END-OF-LOG:":
                    has_end = True
                
                elif tag == "CALLSIGN:":
                    if len(parts) < 2:
                        result.add_error(f"Line {line_num}: Missing callsign")
                    else:
                        result.callsign = parts[1]
                
                elif tag == "EMAIL:":
                    if len(parts) >= 2:
                        result.log_email = parts[1]
                        result.has_email = True
                
                elif tag == "CONTEST:":
                    if len(parts) < 2 or parts[1] != "LA-QSO-PARTY":
                        result.add_error(f"Line {line_num}: CONTEST must be LA-QSO-PARTY")
                
                elif tag == "CATEGORY-POWER:":
                    if len(parts) >= 2:
                        has_power = True
                        result.log_power = parts[1]
                        if parts[1] not in ["QRP", "LOW", "HIGH"]:
                            result.add_error(f"Line {line_num}: CATEGORY-POWER must be QRP, LOW, or HIGH")
                
                elif tag == "CATEGORY-OPERATOR:":
                    has_operator = True
                
                elif tag == "CATEGORY-STATION:":
                    if len(parts) >= 2:
                        result.log_station = parts[1]
                        if parts[1] not in ["FIXED", "ROVER", "MOBILE"]:
                            result.add_warning(f"Line {line_num}: CATEGORY-STATION should be FIXED or ROVER")
                
                elif tag == "CATEGORY-OVERLAY:":
                    if len(parts) >= 2:
                        result.log_overlay = parts[1]
                        if parts[1] not in ["WIRES", "TB-WIRES", "POTA"]:
                            result.add_warning(f"Line {line_num}: CATEGORY-OVERLAY should be WIRES, TB-WIRES, or POTA")
                
                # ===== QSO LINE VALIDATION =====
                
                elif tag == "QSO:":
                    result.qso_count += 1
                    error_code, error_msg = self._validate_qso_line(line, line_num)
                    
                    # Track which modes are used
                    if len(parts) >= 3:
                        mode = parts[2]
                        qso_modes.add(mode)
                    
                    if error_code == -1:  # Fatal error
                        result.invalid_qso_count += 1
                        result.add_error(f"Line {result.qso_count}: {error_msg}")
                    elif error_code > 0 and error_code < 8:  # Invalid but parseable
                        result.invalid_qso_count += 1
                        result.add_error(f"Line {result.qso_count}: {error_msg}")
                    elif error_code == 8:  # Multi-parish (warning only)
                        result.add_warning(f"Line {result.qso_count}: {error_msg}")

        # read all lines from the log file
        # print(result.to_report())
        
        # ===== CHECK REQUIRED FIELDS =====
        
        if not has_start:
            result.add_error("Missing START-OF-LOG: 3.0")
        
        if not has_end:
            result.add_error("Missing END-OF-LOG:")
        
        if not result.callsign:
            result.add_error("Missing CALLSIGN:")
        
        if not has_power:
            result.add_error("Missing CATEGORY-POWER:")
            result.has_valid_power = False
        
        if not has_operator:
            result.add_warning("Missing CATEGORY-OPERATOR: (not critical for LA rules)")
            result.has_valid_operator = False
        
        if not result.has_email:
            result.add_error("Missing EMAIL:")
        
        if result.qso_count == 0:
            result.add_error("No QSOs found in log")
        
        # ===== DETERMINE ACTUAL MODE CATEGORY FROM QSOs =====
        
        has_phone = any(mode in qso_modes for mode in ['PH', 'FM', 'SSB', 'LSB', 'USB'])
        has_cw_digital = any(mode in qso_modes for mode in ['CW', 'RY', 'RTTY', 'DIG', 'FT8', 'FT4'])
        
        if has_phone and has_cw_digital:
            result.log_mode_category = "MIXED"
        elif has_phone:
            result.log_mode_category = "PHONE-ONLY"
        elif has_cw_digital:
            result.log_mode_category = "CW/DIGITAL-ONLY"
        else:
            result.log_mode_category = "UNKNOWN"
        
        # ===== CROSS-CHECK WITH WEB FORM DATA IFF this is processing an uploaded file =====
        if upload:
            if form_email is not None and result.log_email:
                if result.log_email.lower() != form_email.lower():
                    result.add_error(
                        f"Email mismatch: Log has '{result.log_email}' but form has '{form_email}'"
                    )
            
            if form_mode is not None:
                # Convert form mode to log format
                form_mode_map = {
                    'mixed': 'MIXED',
                    'cw_digital': 'CW/DIGITAL-ONLY',
                    'phone': 'PHONE-ONLY'
                }
                expected_mode = form_mode_map.get(form_mode, '')
                
                if expected_mode and result.log_mode_category != expected_mode:
                    result.add_error(
                        f"Mode category mismatch: Your log contains {result.log_mode_category} QSOs "
                        f"but you selected '{expected_mode}' on the form. "
                        f"Please select the correct category."
                    )
            
            if form_power is not None and result.log_power:
                form_power_upper = form_power.upper()
                if result.log_power != form_power_upper:
                    result.add_error(
                        f"Power level mismatch: Log has CATEGORY-POWER: {result.log_power} "
                        f"but you selected '{form_power_upper}' on the form"
                    )
            
            if form_station is not None and result.log_station:
                form_station_upper = form_station.upper()
                if result.log_station != form_station_upper and result.log_station != "MOBILE":
                    result.add_error(
                        f"Station type mismatch: Log has CATEGORY-STATION: {result.log_station} "
                        f"but you selected '{form_station_upper}' on the form"
                    )
            
            if form_overlay is not None:
                # Convert form overlay to log format
                form_overlay_map = {
                    'none': '',
                    'wires': 'WIRES',
                    'tb_wires': 'TB-WIRES',
                    'pota': 'POTA'
                }
                expected_overlay = form_overlay_map.get(form_overlay, '')
                
                if form_overlay != 'none' and result.log_overlay != expected_overlay:
                    result.add_error(
                        f"Overlay category mismatch: Log has CATEGORY-OVERLAY: {result.log_overlay or '(none)'} "
                        f"but you selected '{expected_overlay}' on the form"
                    )
                elif form_overlay == 'none' and result.log_overlay:
                    result.add_error(
                        f"Overlay category mismatch: Log has CATEGORY-OVERLAY: {result.log_overlay} "
                        f"but you selected 'None' on the form"
                    )
            
            # ===== FINAL VALIDATION =====
            
            if result.invalid_qso_count > 0:
                result.is_valid = False
        
        return result
    
    def _validate_qso_line(self, line: str, line_num: int) -> Tuple[int, str]:
        """
        Validate a single QSO line.
        
        Returns:
            (error_code, error_message)
            error_code: -1 = fatal, 0 = OK, 1-7 = invalid field, 8 = warning
        """
        parts = line.split()
        
        # QSO line format:
        # QSO: freq mo date time call rst-sent qth-sent call-rcvd rst-rcvd qth-rcvd [tx#]
        
        if len(parts) < 11:
            return (-1, f"QSO line too short (need at least 11 fields)")
        
        freq_str = parts[1]
        mode = parts[2]
        date_str = parts[3]
        time_str = parts[4]
        call_sent = parts[5]
        rst_sent = parts[6]
        qth_sent = parts[7]
        call_rcvd = parts[8]
        rst_rcvd = parts[9]
        qth_rcvd = parts[10]
        
        # Validate frequency
        try:
            freq = int(freq_str)
            band = freq_to_band(freq)
            if not band:
                return (1, f"Invalid frequency {freq} kHz (not in a valid contest band)")
        except ValueError:
            return (1, f"Invalid frequency - not an integer: '{freq_str}'")
        
        # Validate mode
        if mode not in VALID_MODES:
            return (2, f"Invalid mode '{mode}' (valid: {', '.join(VALID_MODES)})")
        
        # Validate date
        try:
            qso_date = datetime.strptime(date_str, DATE_FORMAT).date()
            if not (CONTEST_START_DAY1 <= qso_date <= CONTEST_END_DAY1):
                return (3, f"Date {date_str} outside contest period")
        except ValueError:
            return (3, f"Invalid date format '{date_str}' (use YYYY-MM-DD)")
        
        # Validate time
        try:
            qso_time = datetime.strptime(time_str, TIME_FORMAT).time()
        except ValueError:
            return (4, f"Invalid time format '{time_str}' (use HHMM)")
        
        # Validate callsigns
        if not call_sent or not call_rcvd:
            return (5, f"Missing callsign")
        
        # Validate RST
        if not rst_sent or not rst_rcvd:
            return (6, f"Missing RST")
        
        # Validate QTH
        if not qth_sent or not qth_rcvd:
            return (7, f"Missing QTH exchange")
        
        # Check if QTH is valid parish or state/province
        qth_sent_upper = qth_sent.upper()
        qth_rcvd_upper = qth_rcvd.upper()
        
        # Check for multi-parish (e.g., "ORLE/JEFF")
        if '/' in qth_sent_upper or '/' in qth_rcvd_upper:
            return (8, f"Multi-parish QTH detected: {qth_sent} / {qth_rcvd} (will be split during processing)")
        
        # Validate sent QTH
        if qth_sent_upper not in self.parishes and qth_sent_upper not in self.states_provinces:
            return (7, f"Invalid QTH-sent '{qth_sent}' (not a valid parish or state/province)")
        
        # Validate received QTH  
        if qth_rcvd_upper not in self.parishes and qth_rcvd_upper not in self.states_provinces:
            return (7, f"Invalid QTH-rcvd '{qth_rcvd}' (not a valid parish or state/province)")
        
        return (0, "OK")


def validate_single_log(upload, log_path: Path, 
                       parish_file: Path, 
                       state_province_file: Path,
                       output_dir: Path = None,
                       form_email: str = None,
                       form_mode: str = None,
                       form_power: str = None,
                       form_station: str = None,
                       form_overlay: str = None) -> ValidationResult:
    """
    Validate a single log file with optional web form cross-checking.
    
    Args:
        log_path: Path to log file
        parish_file: Path to parish abbreviations file
        state_province_file: Path to state/province abbreviations file
        output_dir: Optional directory to write validation report
        form_email: Email from web form (optional)
        form_mode: Mode category from web form (optional)
        form_power: Power level from web form (optional)
        form_station: Station type from web form (optional)
        form_overlay: Overlay category from web form (optional)
    
    Returns:
        ValidationResult object
    """
    # Load reference data
    with open(parish_file, 'r') as f:
        parishes = [line.strip() for line in f if line.strip()]
    
    with open(state_province_file, 'r') as f:
        states_provinces = [line.strip() for line in f if line.strip()]
    
    # Create validator
    validator = LogValidator(upload, parishes, states_provinces)
    
    # Validate (with optional form data)
    result = validator.validate_log_file(
        upload,
        log_path,
        form_email=form_email,
        form_mode=form_mode,
        form_power=form_power,
        form_station=form_station,
        form_overlay=form_overlay
    )
    
    # Write report if output directory specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{result.callsign}-validation.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result.to_report()))
    
    return result


if __name__ == "__main__":
    # Test the validator
    print("LAQP Log Validator - Enhanced Version")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
    print("Or import validate_single_log() in your Flask app.")
