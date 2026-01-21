"""
Louisiana QSO Party Log Validator

Validates Cabrillo log files for LAQP compliance.
Refactored from TQP validation.py with LA-specific rules.
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict

# Import configuration and utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import (
    CONTEST_START_DAY1, CONTEST_END_DAY1,
    TIME_FORMAT, DATE_FORMAT,
    VALID_BANDS, BAND_RANGES, VALID_MODES,
    US_PREFIXES, CANADIAN_PREFIXES
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
    
    def __init__(self, parish_list: List[str], state_province_list: List[str]):
        self.parish_list = [p.strip().upper() for p in parish_list]
        self.state_province_list = [s.strip().upper() for s in state_province_list]
        
        # Convert contest times to timestamps
        self.start_timestamp = self._parse_timestamp(CONTEST_START_DAY1)
        self.end_timestamp = self._parse_timestamp(CONTEST_END_DAY1)
        
    def _parse_timestamp(self, time_string: str) -> int:
        """Convert time string to Unix timestamp"""
        dt = datetime.strptime(time_string, TIME_FORMAT)
        return int(dt.timestamp())
    
    # Validation helper functions
    def is_valid_callsign(self, call: str) -> bool:
        """Check if callsign format is valid"""
        if not call or len(call) < 3:
            return False
        has_slash = "/" in call
        only_alphanum = call.replace("/", "").isalnum()
        has_digit = any(c.isdigit() for c in call)
        return only_alphanum and has_digit
    
    def has_slash_in_qth(self, qth: str) -> bool:
        """Check if QTH has slash (multi-parish indicator)"""
        return "/" in qth
    
    def is_valid_band(self, freq_khz: int) -> bool:
        """Check if frequency is in valid LAQP band"""
        for band, (low, high) in BAND_RANGES.items():
            if low <= freq_khz <= high:
                return True
        return False
    
    def is_valid_mode(self, mode: str) -> bool:
        """Check if mode is valid"""
        return mode in VALID_MODES
    
    def is_valid_datetime(self, date_str: str, time_str: str) -> bool:
        """Check if date/time is within contest period"""
        try:
            dt_string = f"{date_str} {time_str}"
            dt = datetime.strptime(dt_string, TIME_FORMAT)
            timestamp = int(dt.timestamp())
            return self.start_timestamp <= timestamp <= self.end_timestamp
        except ValueError:
            return False
    
    def is_valid_date_format(self, date_str: str) -> bool:
        """Check if date format is correct"""
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return True
        except ValueError:
            return False
    
    def is_valid_time_format(self, time_str: str) -> bool:
        """Check if time format is correct (4 digits)"""
        return len(time_str) == 4 and time_str.isdigit()
    
    def get_callsign_prefix(self, call: str) -> str:
        """Extract prefix from callsign"""
        for i, char in enumerate(call):
            if char.isdigit():
                return call[:i]
        return call
    
    def is_us_callsign(self, call: str) -> bool:
        """Check if callsign is US"""
        prefix = self.get_callsign_prefix(call)
        if not prefix:
            return False
        if prefix[0] in ('K', 'N', 'W'):
            return True
        return prefix in US_PREFIXES
    
    def is_canadian_callsign(self, call: str) -> bool:
        """Check if callsign is Canadian"""
        prefix = self.get_callsign_prefix(call)
        return prefix in CANADIAN_PREFIXES
    
    def is_dx_callsign(self, call: str) -> bool:
        """Check if callsign is DX (not US or VE)"""
        return not (self.is_us_callsign(call) or self.is_canadian_callsign(call))
    
    def is_la_parish(self, qth: str) -> bool:
        """Check if QTH is a Louisiana parish"""
        return qth in self.parish_list
    
    def is_non_la_state_province(self, qth: str) -> bool:
        """Check if QTH is non-LA state or province"""
        return qth in self.state_province_list
    
    def is_valid_qth(self, qth: str) -> bool:
        """Check if QTH format is valid"""
        # if len(qth) :
        #     return False
        if qth.isdigit():  # All digits not allowed
            return False
        return True
    
    def validate_qso_line(self, line: str) -> Tuple[int, str]:
        """
        Validate a QSO line.
        
        Returns:
            (error_code, error_message)
            error_code: 0 = valid, negative = not a QSO line, positive = specific error
        """
        parts = line.split()
        
        if not parts or parts[0] != "QSO:":
            return (0, "")  # Not a QSO line
        
        # LA QSO lines have 11 elements
        if len(parts) != 11:
            return (-1, "Missing or excess data in QSO line")
        
        # Validate each field
        freq_khz = int(parts[1])
        mode = parts[2]
        date = parts[3]
        time = parts[4]
        sent_call = parts[5]
        sent_qth = parts[7]
        rcvd_call = parts[8]
        rcvd_qth = parts[10]
        
        # Check frequency
        if not self.is_valid_band(freq_khz):
            return (1, f"Invalid frequency: {freq_khz} kHz")
        
        # Check mode
        if not self.is_valid_mode(mode):
            return (2, f"Invalid mode: {mode}")
        
        # Check date/time format
        if not self.is_valid_date_format(date):
            return (3, f"Invalid date format: {date}")
        
        if not self.is_valid_time_format(time):
            return (3, f"Invalid time format: {time}")
        
        # Check if within contest period
        if not self.is_valid_datetime(date, time):
            return (3, f"QSO outside contest period: {date} {time}")
        
        # Check callsigns
        if not self.is_valid_callsign(sent_call):
            return (4, f"Invalid sent callsign: {sent_call}")
        
        if not self.is_valid_callsign(rcvd_call):
            return (6, f"Invalid received callsign: {rcvd_call}")
        
        # Check QTH
        # if sent_qth == "TX":
        #     print("sent QTH TX")
        # if rcvd_qth == "TX":
        #     print("rcvd QTH TX")    
        if not self.is_valid_qth(sent_qth):
            return (5, f"Invalid sent QTH: {sent_qth}")
        
        if not self.is_valid_qth(rcvd_qth):
            return (7, f"Invalid received QTH: {rcvd_qth}")
        
        # Check for slash in rcvd QTH (multi-parish, will be split in preparation)
        if self.has_slash_in_qth(rcvd_qth):
            return (8, f"Received QTH has slash (multi-parish): {rcvd_qth} - will be split during preparation")
        
        return (0, "")  # Valid
    
    def validate_log_file(self, filepath: Path) -> ValidationResult:
        """
        Validate a complete log file.
        
        Returns ValidationResult object with validation status and details.
        """
        result = ValidationResult(filepath.stem)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            result.add_error(f"Could not read file: {str(e)}")
            return result
        
        # Track required headers
        has_power = False
        has_operator = False
        
        for line in lines:
            line = line.strip().upper()
            if not line:
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            tag = parts[0]
            
            # Check for required tags
            if tag == "CALLSIGN:":
                if len(parts) > 1:
                    result.callsign = parts[1]
            
            elif tag == "EMAIL:":
                if len(parts) > 1:
                    result.has_email = True
                else:
                    result.add_warning("EMAIL tag present but empty")
            
            elif tag == "CATEGORY-POWER:":
                if len(parts) > 1 and parts[1] in ('QRP', 'LOW', 'HIGH'):
                    has_power = True
                else:
                    result.add_error("CATEGORY-POWER missing or invalid (should be QRP, LOW, or HIGH)")
            
            elif tag == "CATEGORY-OPERATOR:":
                # LA rules: operator category is ignored, everyone lumped together
                if len(parts) > 1:
                    has_operator = True
                else:
                    result.add_warning("CATEGORY-OPERATOR missing")
            
            elif tag == "CATEGORY-STATION:":
                # Check for FIXED, MOBILE, ROVER, PORTABLE
                if len(parts) < 2 or parts[1] not in ('FIXED', 'MOBILE', 'ROVER', 'PORTABLE'):
                    result.add_warning("CATEGORY-STATION missing or invalid")
            
            elif tag == "CERTIFICATE:":
                # Check if contestant wants certificate
                pass
            
            elif tag == "QSO:":
                result.qso_count += 1
                error_code, error_msg = self.validate_qso_line(line)
                
                if error_code < 0:  # Malformed line
                    result.invalid_qso_count += 1
                    result.add_error(f"Line {result.qso_count}: {error_msg}")
                elif error_code > 0 and error_code < 8:  # Invalid but parseable
                    result.invalid_qso_count += 1
                    result.add_error(f"Line {result.qso_count}: {error_msg}")
                elif error_code == 8:  # Multi-parish (warning only)
                    result.add_warning(f"Line {result.qso_count}: {error_msg}")
        
        # Check required fields
        result.has_valid_power = has_power
        result.has_valid_operator = has_operator
        
        if not has_power:
            result.add_error("Missing CATEGORY-POWER")
        
        if not has_operator:
            result.add_warning("Missing CATEGORY-OPERATOR (not critical for LA rules)")
        
        if result.qso_count == 0:
            result.add_error("No QSOs found in log")
        
        # Final validation
        if result.invalid_qso_count > 0:
            result.is_valid = False
        
        return result


def validate_single_log(log_path: Path, parish_file: Path, state_province_file: Path, 
                       output_dir: Path = None) -> ValidationResult:
    """
    Validate a single log file.
    
    Args:
        log_path: Path to log file
        parish_file: Path to parish abbreviations file
        state_province_file: Path to state/province abbreviations file
        output_dir: Optional directory to write validation report
    
    Returns:
        ValidationResult object
    """
    # Load reference data
    with open(parish_file, 'r') as f:
        parishes = [line.strip() for line in f if line.strip()]
    
    with open(state_province_file, 'r') as f:
        states_provinces = [line.strip() for line in f if line.strip()]
    
    # Create validator
    validator = LogValidator(parishes, states_provinces)
    
    # Validate
    result = validator.validate_log_file(log_path)
    
    # Write report if output directory specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"{result.callsign}-validation.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result.to_report()))
    
    return result


if __name__ == "__main__":
    # Test the validator
    print("LAQP Log Validator Test")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
