#!/usr/bin/env python3
"""
Louisiana QSO Party - Unified Log Processor

Combines validation, preparation, and scoring into a single streamlined process.
Works in-memory without intermediate files.
Returns standardized result dictionary.

This module can be used by:
- Web upload app (single log processing)
- Batch processor (iterate through multiple logs)
"""

from pprint import pprint
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
from unittest import result

# Import your existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.config import (
    freq_to_band,
    LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    US_PREFIXES, CANADIAN_PREFIXES,
    PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    N5LCC_BONUS, ROVER_PARISH_BONUS,
    PHONE_MODES, CW_DIGITAL_MODES, PROVINCES
)


class UnifiedLogProcessor:
    """
    Unified processor that combines validation, preparation, and scoring.
    
    Uses consistent naming throughout:
    - location_type: 'DX', 'NON-LA', 'LA-FIXED', 'LA-ROVER'
    - mode_category: 'PHONE', 'CW-DIGITAL', 'MIXED'
    - power_level: 'QRP', 'LOW', 'HIGH'
    - overlay: None, 'WIRES', 'TB-WIRES', 'POTA'
    """
    
    def __init__(self, parish_file: Path, state_province_file: Path):
        """Initialize with reference data files"""
        # Load parishes
        with open(parish_file, 'r') as f:
            self.parishes = set(line.strip().upper() for line in f if line.strip())
        
        # Load states/provinces
        with open(state_province_file, 'r') as f:
            self.states_provinces = set(line.strip().upper() for line in f if line.strip())
        
        # Ambiguous QTH that need DX suffix
        self.ambiguous_dx_qth = {"ON", "PA", "CT", "TN", "LA", "HI", "OK", "CO", "OH"}
    
    def process_log(self, log_path: Path,
                   form_email: Optional[str] = None,
                   form_mode: Optional[str] = None,
                   form_power: Optional[str] = None,
                   form_station: Optional[str] = None,
                   form_overlay: Optional[str] = None) -> Dict:
        """
        Complete processing pipeline: validate → prepare → score
        
        Args:
            log_path: Path to Cabrillo log file
            form_*: Optional web form values to cross-check
        
        Returns:
            Complete result dictionary with all statistics
        """
        # Initialize result with your standardized structure
        result = self._init_result()
        
        # Phase 1: Validate and parse
        try:
            self._validate_and_parse(log_path, result, form_email, form_mode, 
                                    form_power, form_station, form_overlay)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Validation failed: {str(e)}")
            return result
        
        # If validation failed, return early
        if not result['is_valid']:
            return result
        
        # Phase 2: Prepare QSOs (in memory)
        try:
            prepared_qsos = self._prepare_qsos(result)
            result['valid_qsos'] = len(prepared_qsos)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Preparation failed: {str(e)}")

            pprint(f"Done preparing: {result}")
            print("BREAKPOINT")
            return result
        
        # Phase 3: Score
        try:
            self._score_qsos(prepared_qsos, result)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Scoring failed: {str(e)}")

            pprint(f"Done scoring: {result}")
            print("BREAKPOINT")
            return result
        
        return result
    
    def _init_result(self) -> Dict:
        """Initialize result dictionary with standardized structure"""
        return {
            'callsign': '',
            'name': '',
            'category': '',  # Short category name (e.g., 'nl_ph_lo')
            'overlay': None,  # 'WIRES', 'TB-WIRES', 'POTA', or None
            'location_type': 'NON-LA',  # 'DX', 'NON-LA', 'LA-FIXED', 'LA-ROVER'
            'mode_category': 'MIXED',  # 'PHONE', 'CW-DIGITAL', 'MIXED'
            'power_level': 'LOW',  # 'QRP', 'LOW', 'HIGH'
            'is_rover': False,
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
            'provinces_worked_multiplier': 0,
            'dx_worked': set(),
            'dx_worked_multiplier': 0,
            'parishes_activated': set(),
            'rover_bonus_points': 0,
            'worked_n5lcc': False,
            'num_n5lcc_contacts': 0,
            'qsos_by_band': {'160': 0, '80': 0, '40': 0, '20': 0, '15': 0, '10': 0, '6': 0, '2': 0},
            'qsos_by_mode': {'Phone': 0, 'CW/Digital': 0},
            'qsos_by_hour': {i: 0 for i in range(12)},
            'bands_worked': set(),
            'multipliers_by_band_mode': {},
            'claimed_score': 0,
            'errors': [],
            'warnings': [],
            'has_valid_power': True,
            'has_valid_operator': True,
            'has_email': False,
            'is_valid': True,
            # Store raw QSO lines for processing
            '_qso_lines': [],
            '_header': {}
        }
    
    def _validate_and_parse(self, log_path: Path, result: Dict,
                           form_email: Optional[str],
                           form_mode: Optional[str],
                           form_power: Optional[str],
                           form_station: Optional[str],
                           form_overlay: Optional[str]):
        """Phase 1: Validate and parse header/QSOs"""
        
        has_start = False
        has_end = False
        qso_modes = set()
        
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip().upper()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                tag = parts[0]
                
                # Parse header
                if tag == "START-OF-LOG:":
                    has_start = True
                    if len(parts) < 2 or parts[1] != "3.0":
                        result['warnings'].append(f"Line {line_num}: Expected START-OF-LOG: 3.0")
                
                elif tag == "END-OF-LOG:":
                    has_end = True
                
                elif tag == "CALLSIGN:":
                    if len(parts) < 2:
                        result['errors'].append(f"Line {line_num}: Missing callsign")
                        result['is_valid'] = False
                    else:
                        result['callsign'] = parts[1]
                
                elif tag == "NAME:":
                    result['name'] = ' '.join(parts[1:]) if len(parts) > 1 else ''
                
                elif tag == "EMAIL:":
                    if len(parts) >= 2:
                        result['_header']['email'] = parts[1]
                        result['has_email'] = True
                
                elif tag == "CLAIMED-SCORE:":
                    if len(parts) > 1:
                        try:
                            result['claimed_score'] = int(parts[1])
                        except ValueError:
                            result['claimed_score'] = 0
                
                elif tag == "CONTEST:":
                    if len(parts) < 2 or parts[1] not in ['LA-QSO-PARTY', 'LOUISIANA-QSO-PARTY', 'LAQP']:
                        result['errors'].append(f"Line {line_num}: CONTEST must be LA-QSO-PARTY")
                        result['is_valid'] = False
                
                elif tag == "CATEGORY-POWER:":
                    if len(parts) >= 2:
                        result['_header']['power'] = parts[1]
                        result['has_valid_power'] = True
                        if parts[1] not in ['QRP', 'LOW', 'HIGH']:
                            result['errors'].append(f"Line {line_num}: CATEGORY-POWER must be QRP, LOW, or HIGH")
                            result['is_valid'] = False
                    else:
                        result['has_valid_power'] = False
                
                elif tag == "CATEGORY-OPERATOR:":
                    result['has_valid_operator'] = True
                
                elif tag == "CATEGORY-STATION:":
                    if len(parts) >= 2:
                        result['_header']['station'] = parts[1]
                        if parts[1] not in ['FIXED', 'ROVER', 'MOBILE', 'PORTABLE']:
                            result['warnings'].append(f"Line {line_num}: CATEGORY-STATION should be FIXED or ROVER")
                
                elif tag == "CATEGORY-OVERLAY:":
                    if len(parts) >= 2:
                        result['_header']['overlay'] = parts[1]
                        if parts[1] not in ['WIRES', 'TB-WIRES', 'POTA']:
                            result['warnings'].append(f"Line {line_num}: CATEGORY-OVERLAY should be WIRES, TB-WIRES, or POTA")
                
                # Store QSO lines for later processing
                elif tag == "QSO:":
                    result['total_qsos'] += 1
                    result['_qso_lines'].append((line_num, line))
                    
                    # Track modes
                    if len(parts) >= 3:
                        qso_modes.add(parts[2])
                    
                    # Basic QSO validation
                    error_msg = self._validate_qso_line(line, line_num)
                    if error_msg:
                        result['warnings'].append(error_msg)

        # pprint(f' AFTER process log headers: result: {result}')
        # print("BREAKPOINT")
        
        # Check required fields
        if not has_start:
            result['errors'].append("Missing START-OF-LOG: 3.0")
            result['is_valid'] = False
        
        if not has_end:
            result['errors'].append("Missing END-OF-LOG:")
            result['is_valid'] = False
        
        if not result['callsign']:
            result['errors'].append("Missing CALLSIGN:")
            result['is_valid'] = False
        
        if not result['has_valid_power']:
            result['errors'].append("Missing CATEGORY-POWER:")
            result['is_valid'] = False
        
        if not result['has_email']:
            result['warnings'].append("Missing EMAIL: (recommended)")
        
        if result['total_qsos'] == 0:
            result['errors'].append("No QSOs found in log")
            result['is_valid'] = False
        
        # Determine mode category from actual QSOs
        has_phone = any(mode in qso_modes for mode in ['PH', 'FM', 'SSB', 'LSB', 'USB'])
        has_cw_digital = any(mode in qso_modes for mode in ['CW', 'RY', 'RTTY', 'DIG', 'FT8', 'FT4'])
        
        if has_phone and has_cw_digital:
            result['mode_category'] = 'MIXED'
        elif has_phone:
            result['mode_category'] = 'PHONE'
        elif has_cw_digital:
            result['mode_category'] = 'CW-DIGITAL'
        
        # Set power level from header
        result['power_level'] = result['_header'].get('power', 'LOW')
        
        # Set overlay from header
        result['overlay'] = result['_header'].get('overlay', None)
        
        # Cross-check with form data if provided
        if form_email and result['has_email']:
            if result['_header']['email'].lower() != form_email.lower():
                result['warnings'].append(f"Email mismatch: log has {result['_header']['email']}, form has {form_email}")
                
        # pprint(f"END validate + parse: errros: {result['errors']}, warnings: {result['warnings']}\nresult: {result}")
        # print("BREAKPOINT")

    # END of _validate_and_parse
    
    def _validate_qso_line(self, line: str, line_num: int) -> Optional[str]:
        """Basic QSO line validation - returns error message or None"""
        parts = line.split()
        if len(parts) < 11:
            return f"Line {line_num}: Insufficient QSO fields"
        
        # Validate frequency
        try:
            freq = int(parts[1])
            band = freq_to_band(freq)
            if band == 0:
                return f"Line {line_num}: Invalid frequency {freq} kHz"
        except (ValueError, IndexError):
            return f"Line {line_num}: Invalid frequency format"
        
        # Validate mode
        mode = parts[2]
        if mode not in PHONE_MODES and mode not in CW_DIGITAL_MODES:
            return f"Line {line_num}: Invalid mode {mode}"
        
        return None
    
    def _prepare_qsos(self, result: Dict) -> List[Dict]:
        """Phase 2: Prepare QSOs (convert freq, expand multi-parish, etc.)"""
        prepared = []
        print(f"Initial prepared: {id(prepared)}")
        
        for line_num, qso_line in result['_qso_lines']:
            parts = qso_line.split()
            if len(parts) < 11:
                continue
            
            # pprint(f"Processing QSO Line {line_num}: {parts}")
            # print("BREAKPOINT")
            # Parse QSO fields
            freq_khz = int(parts[1])
            mode = parts[2]
            date = parts[3]
            time = parts[4]
            sent_call = parts[5].split('/')[0]  # Remove mobile indicator
            sent_rst = parts[6]
            sent_qth = parts[7]
            rcvd_call = parts[8].split('/')[0]  # Remove mobile indicator
            rcvd_rst = parts[9]
            rcvd_qth = parts[10]
            
            # Convert frequency to band
            band = str(freq_to_band(freq_khz))
            
            # Normalize mode
            if mode in PHONE_MODES:
                mode_cat = 'Phone'
            else:
                mode_cat = 'CW/Digital'
            
            # Handle multi-parish QTH (split on /)
            rcvd_qth_list = rcvd_qth.split('/')
            
            for qth in rcvd_qth_list:
                qth = qth.strip()
                
                # Check if DX suffix needed
                sent_qth_final = sent_qth
                rcvd_qth_final = qth
                
                if self._is_dx_callsign(sent_call) and sent_qth in self.ambiguous_dx_qth:
                    sent_qth_final = sent_qth + 'DX'
                if self._is_dx_callsign(rcvd_call) and qth in self.ambiguous_dx_qth:
                    rcvd_qth_final = qth + 'DX'
                
            prepared.append({
                'band': band,
                'mode': mode,
                'mode_category': mode_cat,
                'date': date,
                'time': time,
                'sent_call': sent_call,
                'sent_rst': sent_rst,
                'sent_qth': sent_qth_final,
                'rcvd_call': rcvd_call,
                'rcvd_rst': rcvd_rst,
                'rcvd_qth': rcvd_qth_final,
                'line_num': line_num
            })
            # print(f"After append #{len(prepared)}:")
            # print(f"  - prepared id: {id(prepared)}")
            # print(f"  - Last item id: {id(prepared[-1])}")
            # print(f"  - Last item: {prepared[-1]}")
            # print(f"  - band={band}, mode={mode}")


            # pprint(f"Prepared QSO Line {line_num}: {prepared}")
            # pprint("-----")
        
        # Get info that is NOT specific to each QSO but is needed for scoring (e.g., location type)
        # Determine location type from prepared QSOs
        result['location_type'] = self._determine_location_type(prepared, result['_header'])
        result['is_rover'] = (result['location_type'] == 'LA-ROVER')
        
        # Generate category short name
        loc_abbrev = {
            'DX': 'dx',
            'NON-LA': 'nl',
            'LA-FIXED': 'lf',
            'LA-ROVER': 'lr'
        }[result['location_type']]
        
        mode_abbrev = {
            'PHONE': 'ph',
            'CW-DIGITAL': 'cw',
            'MIXED': 'mx'
        }[result['mode_category']]
        
        power_abbrev = {
            'QRP': 'qp',
            'LOW': 'lo',
            'HIGH': 'hi'
        }[result['power_level']]
        
        result['category'] = f"{loc_abbrev}_{mode_abbrev}_{power_abbrev}"


        # pprint(f"location_type: {result['location_type']}, category: {result['category']}\nPrepared {len(prepared)} QSOs; QSO Line {line_num}: Prepared {prepared}")
        # print("BREAKPOINT")
        
        return prepared
    
    ## END of prepare_qsos
    
    def _determine_location_type(self, qsos: List[Dict], header: Dict) -> str:
        """Determine location type from QSOs"""
        sent_qths = []
        
        for qso in qsos:
            sent_qth = qso['sent_qth'].replace('DX', '')
            sent_call = qso['sent_call']
            
            # Check if DX
            if self._is_dx_callsign(sent_call):
                return 'DX'
            
            # Check if non-LA
            if sent_qth in self.states_provinces:
                return 'NON-LA'
            
            # Must be LA
            if sent_qth in self.parishes:
                sent_qths.append(sent_qth)
        
        # Determine if fixed or rover
        unique_parishes = list(set(sent_qths))
        station = header.get('station', 'FIXED')
        
        if station in ('MOBILE', 'ROVER'):
            return 'LA-ROVER'
        elif station in ('FIXED', 'PORTABLE'):
            return 'LA-FIXED'
        elif len(unique_parishes) > 1:
            return 'LA-ROVER'
        else:
            return 'LA-FIXED'
    
    def _score_qsos(self, qsos: List[Dict], result: Dict):
        """Phase 3: Score QSOs and calculate multipliers"""
        
        # for checking duplicate qsos: same band, mode, and rcvd_qth is a duplicate
        dup_check = []

        for qso in qsos:
            band = qso['band']
            mode_cat = qso['mode_category']
            sent_call = qso['sent_call']
            rcvd_call = qso['rcvd_call']
            rcvd_qth = qso['rcvd_qth'].replace('DX', '')

            # Ignore if a duplicate -- no points
            dup_key = band + mode_cat + rcvd_qth
            if dup_key in dup_check:
                pprint(f"Duplicate QSO detected: Line {qso['line_num']} QSO: {rcvd_qth}  {rcvd_call} on {band} {mode_cat}")
                result['warnings'].append(f"Duplicate QSO: Band {band}, Mode {mode_cat}, Rcvd QTH {rcvd_qth} (Line {qso['line_num']})")
                if rcvd_call == 'N5LCC':
                    result['worked_n5lcc'] = True
                    result['num_n5lcc_contacts'] += 1
                continue
            else:
                pprint(f"NOT Duplicate QSO: Line {qso['line_num']} QSO: {rcvd_qth}  {rcvd_call} on {band} {mode_cat}")
                dup_check.append(dup_key)
                    

            # Track bands worked and QSO by band (for display only, does not impact score)
            result['bands_worked'].add(band)
            result['qsos_by_band'][band] += 1

            # Track qsos by hour (2-hour blocks)
            try:
                hour = int(qso['time'][:2])  # hour of the qso
                if hour in result['qsos_by_hour']:
                    result['qsos_by_hour'][hour] += 1
            except:
                pass
            
            # Award points
            if mode_cat == 'Phone':
                result['qso_points'] += PHONE_QSO_POINTS
                result['qsos_by_mode']['Phone'] += 1
            else:  # CW/Digital
                result['qso_points'] += CW_DIGITAL_QSO_POINTS
                result['qsos_by_mode']['CW/Digital'] += 1

            # Check for N5LCC
            if rcvd_call == 'N5LCC':
                result['worked_n5lcc'] = True
                result['num_n5lcc_contacts'] += 1
                pprint(f"Found N5LCC contact, total now: {result['num_n5lcc_contacts']}")

            ## Everyone gets parish multiplier for parishes, but only LA stations get state/province/DX multipliers
            if rcvd_qth in self.parishes:
                    result['parishes_worked'].add(rcvd_qth)
                    result['parishes_worked_multiplier'] += 1
            
            # LA stations get state, province, and DX multipliers
            elif result['location_type'] == 'LA-FIXED' or result['location_type'] == 'LA-ROVER':
                # LA: states, provinces, DX are multipliers
                if rcvd_qth in self.states_provinces:
                    if rcvd_qth in PROVINCES:
                        result['provinces_worked'].add(rcvd_qth)
                        result['provinces_worked_multiplier'] += 1
                    else:
                        result['states_worked'].add(rcvd_qth)
                        result['states_worked_multiplier'] += 1

                else:
                    result['dx_worked'].add(rcvd_qth)
                    result['dx_worked_multiplier'] += 1
                
                # Track parish activations for rovers
                if result['is_rover'] and qso['sent_qth'] in self.parishes:
                    result['parishes_activated'].add(qso['sent_qth'])

            pprint(f"QSO_points: {result['qso_points']}")

        pprint(f"Done qso_points: {result['qso_points']}")
        print("BREAKPOINT")

        # Finished with points, now sum the individual multipliers
        for i in ['parishes', 'states', 'provinces', 'dx']:
            result['total_multipliers'] += result[f'{i}_worked_multiplier']
          
        pprint(f"L TOTAL MULT: {result['total_multipliers']} basic multipliers: Parishes {result['parishes_worked_multiplier']}, States {result['states_worked_multiplier']}, Provinces {result['provinces_worked_multiplier']}, DX {result['dx_worked_multiplier']}")
        print("BREAKPOINT")

        ## score before bonuses
        result['final_score'] = result['qso_points'] * max(1, result['total_multipliers'])

        pprint(f'Final score before bonuses: {result["final_score"]}')
        print('BREAKPOINT')

        ## add bonus points for one or more N5LCC contacts
        if result['worked_n5lcc']:
            result['final_score'] += N5LCC_BONUS

        ## Add rover bonus points for activated parishes
        if result['location_type'] == 'LA-ROVER':
            result['rover_bonus_points'] = len(result['parishes_activated']) * ROVER_PARISH_BONUS
            result['final_score'] += result['rover_bonus_points']
            
        pprint(f'Final score with bonuses: {result["final_score"]}')
        print('BREAKPOINT')

    ## END of score_qsos
    
    def _is_dx_callsign(self, call: str) -> bool:
        """Check if callsign is DX (not US or VE)"""
        prefix = self._get_callsign_prefix(call)
        if not prefix:
            return False
        
        # US callsigns
        if prefix[0] in ('K', 'N', 'W'):
            return False
        if prefix in US_PREFIXES:
            return False
        
        # Canadian callsigns
        if prefix in CANADIAN_PREFIXES:
            return False
        
        return True
    
    def _get_callsign_prefix(self, call: str) -> str:
        """Extract prefix from callsign"""
        for i, char in enumerate(call):
            if char.isdigit():
                return call[:i]
        return call
    
## End of UnifiedLogProcessor class

# Convenience functions for single log and batch processing

def process_single_log(log_path: Path, 
                      parish_file: Path = None,
                      state_province_file: Path = None,
                      **form_data) -> Dict:
    """
    Process a single log file (for web uploads).
    
    Args:
        log_path: Path to log file
        parish_file: Path to parish abbreviations (optional, uses default)
        state_province_file: Path to state/province abbreviations (optional, uses default)
        **form_data: Optional form fields (email, mode, power, station, overlay)
    
    Returns:
        Result dictionary
    """
    if parish_file is None:
        parish_file = Path(LA_PARISHES_FILE)
    if state_province_file is None:
        state_province_file = Path(WVE_ABBREVS_FILE)
    
    processor = UnifiedLogProcessor(parish_file, state_province_file)
    return processor.process_log(
        log_path,
        form_email=form_data.get('email'),
        form_mode=form_data.get('mode'),
        form_power=form_data.get('power'),
        form_station=form_data.get('station'),
        form_overlay=form_data.get('overlay')
    )


def process_batch_logs(log_dir: Path,
                      parish_file: Path = None,
                      state_province_file: Path = None) -> List[Dict]:
    """
    Process multiple log files (for batch processing).
    
    Args:
        log_dir: Directory containing log files
        parish_file: Path to parish abbreviations (optional, uses default)
        state_province_file: Path to state/province abbreviations (optional, uses default)
    
    Returns:
        List of result dictionaries
    """
    if parish_file is None:
        parish_file = Path(LA_PARISHES_FILE)
    if state_province_file is None:
        state_province_file = Path(WVE_ABBREVS_FILE)
    
    processor = UnifiedLogProcessor(parish_file, state_province_file)
    results = []
    
    for log_file in log_dir.glob('*.log'):
        result = processor.process_log(log_file)
        results.append(result)
    
    return results


if __name__ == "__main__":
    print("LAQP Unified Log Processor")
    print("This module should be imported, not run directly.")
    print()
    print("For web upload: from processor import process_single_log")
    print("For batch: from processor import process_batch_logs")
