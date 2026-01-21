"""
Louisiana QSO Party Log Preparation

Prepares validated logs for scoring by:
1. Converting frequency to band number
2. Removing slashes from callsigns 
3. Splitting multi-parish QSOs into separate lines
4. Marking DX QTH indicators
5. Determining contest category from log contents

Adapted from TQP preparation.py for LA rules.
"""
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import (
    BAND_RANGES,
    LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    US_PREFIXES, CANADIAN_PREFIXES,
    LOC_DX, LOC_NON_LA, LOC_LA_FIXED, LOC_LA_ROVER,
    MODE_PHONE_ONLY, MODE_CW_DIGITAL_ONLY, MODE_MIXED,
    POWER_QRP, POWER_LOW, POWER_HIGH,
    OVERLAY_NONE, OVERLAY_WIRES, OVERLAY_TB_WIRES, OVERLAY_POTA
)


class LogPreparation:
    """Prepares validated logs for scoring"""
    
    def __init__(self, parish_file: Path, state_province_file: Path):
        # Load reference data
        with open(parish_file, 'r') as f:
            self.parish_list = [line.strip().upper() for line in f if line.strip()]
        
        with open(state_province_file, 'r') as f:
            self.state_province_list = [line.strip().upper() for line in f if line.strip()]
        
        # Set of ambiguous QTH that need DX suffix when from DX station
        self.ambiguous_dx_qth = {"ON", "PA", "CT", "TN", "LA", "HI", "OK", "CO", "OH"}
    
    def convert_khz_to_band(self, freq_khz: int) -> int:
        """Convert frequency in kHz to band number"""
        # First check if already a band number
        if freq_khz in [160, 80, 40, 20, 15, 10, 6, 2]:
            return freq_khz
        
        # Otherwise convert from frequency
        for band, (low, high) in BAND_RANGES.items():
            if low <= freq_khz <= high:
                return band
        
        return 0  # Invalid
    
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
        """Check if QTH is LA parish"""
        return qth in self.parish_list
    
    def is_non_la_state_province(self, qth: str) -> bool:
        """Check if QTH is non-LA state or province"""
        return qth in self.state_province_list
    
    def needs_dx_suffix(self, qso_line: str) -> int:
        """
        Check if QSO line needs DX suffix added.
        
        Returns:
            0 = no change needed
            1 = sent QTH needs DX suffix
            2 = rcvd QTH needs DX suffix
        """
        parts = qso_line.split()
        if parts[0] != "QSO:" or len(parts) < 11:
            return 0
        
        sent_call = parts[5]
        sent_qth = parts[7]
        rcvd_call = parts[8]
        rcvd_qth = parts[10]
        
        sent_is_dx = self.is_dx_callsign(sent_call)
        rcvd_is_dx = self.is_dx_callsign(rcvd_call)
        
        sent_qth_ambiguous = sent_qth in self.ambiguous_dx_qth
        rcvd_qth_ambiguous = rcvd_qth in self.ambiguous_dx_qth
        
        if sent_is_dx and sent_qth_ambiguous:
            return 1
        if rcvd_is_dx and rcvd_qth_ambiguous:
            return 2
        
        return 0
    
    def reformat_qso_line(self, qso_line: str, change_code: int) -> List[str]:
        """
        Reformat a QSO line:
        - Convert frequency to band
        - Remove slashes from callsigns
        - Split multi-parish QSOs
        - Add DX suffix if needed
        
        Returns list of reformatted QSO lines (may be multiple if multi-parish)
        """
        parts = qso_line.split()
        if len(parts) < 11:
            return [qso_line + "    [ERROR: Missing QSO elements]"]
        
        # Convert frequency to band
        band = str(self.convert_khz_to_band(int(parts[1])))
        
        # Remove slashes from callsigns (mobile indicators)
        sent_call = parts[5].split("/")[0]
        rcvd_call = parts[8].split("/")[0]
        
        # Split multi-parish QTH (may have slashes for county-line operation)
        rcvd_qth_list = parts[10].split("/")
        
        # Build reformatted lines
        result_lines = []
        for qth in rcvd_qth_list:
            if change_code == 0:
                # No DX suffix needed
                line = f"{parts[0]} {band} {parts[2]} {parts[3]} {parts[4]} {sent_call} {parts[6]} {parts[7]} {rcvd_call} {parts[9]} {qth}"
            elif change_code == 1:
                # Sent QTH needs DX suffix
                line = f"{parts[0]} {band} {parts[2]} {parts[3]} {parts[4]} {sent_call} {parts[6]} {parts[7]}DX {rcvd_call} {parts[9]} {qth}"
            else:  # change_code == 2
                # Rcvd QTH needs DX suffix
                line = f"{parts[0]} {band} {parts[2]} {parts[3]} {parts[4]} {sent_call} {parts[6]} {parts[7]} {rcvd_call} {parts[9]} {qth}DX"
            
            result_lines.append(line)
        
        return result_lines
    
    def determine_location_type(self, qso_lines: List[str], header_station: str, header_fixed: bool) -> int:
        """
        Determine location type from QSO lines.
        
        Returns:
            LOC_DX = 0
            LOC_NON_LA = 1
            LOC_LA_FIXED = 2
            LOC_LA_ROVER = 3
        """
        sent_parishes = []
        
        for line in qso_lines:
            parts = line.split()
            if parts[0] != "QSO:" or len(parts) < 11:
                continue
            
            sent_call = parts[5]
            sent_qth = parts[7]
            
            # Check if DX
            if self.is_dx_callsign(sent_call):
                return LOC_DX
            
            # Check if non-LA US/VE
            if self.is_non_la_state_province(sent_qth):
                return LOC_NON_LA
            
            # Check if LA
            if self.is_la_parish(sent_qth):
                sent_parishes.append(sent_qth)
        
        # If we got here, station is in Louisiana
        unique_parishes = list(set(sent_parishes))
        
        # If header says FIXED/PORTABLE, use that
        if header_fixed:
            return LOC_LA_FIXED
        
        # If header says MOBILE/ROVER, use that
        if header_station in ('MOBILE', 'ROVER'):
            return LOC_LA_ROVER
        
        # Otherwise determine from parishes
        if len(unique_parishes) > 1:
            # Operated from multiple parishes = rover
            return LOC_LA_ROVER
        else:
            # Single parish = fixed
            return LOC_LA_FIXED
    
    def determine_mode_category(self, qso_lines: List[str]) -> int:
        """
        Determine mode category from QSO lines.
        
        Returns:
            MODE_PHONE_ONLY = 0
            MODE_CW_DIGITAL_ONLY = 1
            MODE_MIXED = 2
        """
        has_cw = False
        has_digital = False
        has_phone = False
        
        for line in qso_lines:
            parts = line.split()
            if parts[0] != "QSO:" or len(parts) < 11:
                continue
            
            mode = parts[2]
            if mode == "CW":
                has_cw = True
            elif mode in ("DG", "RY"):
                has_digital = True
            elif mode in ("PH", "FM"):
                has_phone = True
        
        # LA rules: CW and Digital are grouped together
        has_cw_digital = has_cw or has_digital
        
        if has_cw_digital and not has_phone:
            return MODE_CW_DIGITAL_ONLY
        elif has_phone and not has_cw_digital:
            return MODE_PHONE_ONLY
        else:
            return MODE_MIXED
    
    def determine_power_level(self, header_power: str) -> int:
        """
        Determine power level from header.
        
        Returns:
            POWER_QRP = 0
            POWER_LOW = 1
            POWER_HIGH = 2
        """
        if header_power == "QRP":
            return POWER_QRP
        elif header_power == "LOW":
            return POWER_LOW
        else:
            return POWER_HIGH
    
    def determine_overlay(self, header_overlay: str) -> int:
        """
        Determine overlay category from header.
        
        Returns:
            OVERLAY_NONE = 0
            OVERLAY_WIRES = 1
            OVERLAY_TB_WIRES = 2
            OVERLAY_POTA = 3
        """
        if header_overlay == "WIRES":
            return OVERLAY_WIRES
        elif header_overlay == "TB-WIRES":
            return OVERLAY_TB_WIRES
        elif header_overlay == "POTA":
            return OVERLAY_POTA
        else:
            return OVERLAY_NONE
    
    def prepare_log(self, input_path: Path, output_path: Path) -> dict:
        """
        Prepare a validated log for scoring.
        
        Returns dict with category information:
            callsign, location_type, is_rover, mode_category, power_level, overlay
        """
        prepared_lines = []
        qso_lines = []
        
        # Parse header information
        callsign = ""
        header_power = "LOW"
        header_station = "FIXED"
        header_overlay = ""
        header_fixed = False
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().upper()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                tag = parts[0]
                
                if tag == "CALLSIGN:":
                    callsign = parts[1] if len(parts) > 1 else ""
                
                elif tag == "CATEGORY-POWER:":
                    header_power = parts[1] if len(parts) > 1 else "LOW"
                
                elif tag == "CATEGORY-STATION:":
                    header_station = parts[1] if len(parts) > 1 else "FIXED"
                    if header_station in ("FIXED", "PORTABLE"):
                        header_fixed = True
                
                elif tag == "CATEGORY-OVERLAY:":
                    header_overlay = parts[1] if len(parts) > 1 else ""
                
                elif tag == "QSO:":
                    qso_lines.append(line)
                    # Check if needs DX suffix
                    change_code = self.needs_dx_suffix(line)
                    # Reformat and expand multi-parish
                    reformatted = self.reformat_qso_line(line, change_code)
                    prepared_lines.extend(reformatted)
                
                else:
                    # Keep other header lines as-is
                    prepared_lines.append(line)
        
        # Determine category
        location_type = self.determine_location_type(qso_lines, header_station, header_fixed)
        is_rover = (location_type == LOC_LA_ROVER)
        mode_category = self.determine_mode_category(qso_lines)
        power_level = self.determine_power_level(header_power)
        overlay = self.determine_overlay(header_overlay)
        
        # Generate category name
        category_name = get_category_name(location_type, mode_category, is_rover, power_level, overlay)
        
        # Insert category line after header
        prepared_lines.insert(1, f"TQP-CATEGORY: {category_name}")
        
        # Write prepared log
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in prepared_lines:
                f.write(f"{line}\n")
        
        # Return category information
        return {
            'callsign': callsign,
            'location_type': location_type,
            'is_rover': is_rover,
            'mode_category': mode_category,
            'power_level': power_level,
            'overlay': overlay,
            'category_name': category_name
        }


def prepare_single_log(input_path: Path, output_path: Path, 
                       parish_file: Path, state_province_file: Path) -> dict:
    """
    Prepare a single log file.
    
    Args:
        input_path: Path to validated log
        output_path: Path for prepared log
        parish_file: Path to parish abbreviations
        state_province_file: Path to state/province abbreviations
    
    Returns:
        Dictionary with category information
    """
    prep = LogPreparation(parish_file, state_province_file)
    return prep.prepare_log(input_path, output_path)


if __name__ == "__main__":
    print("LAQP Log Preparation Module")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
