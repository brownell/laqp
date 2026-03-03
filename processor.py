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
    PHONE_MODES, CW_DIGITAL_MODES, PROVINCES, CONTEST_YEAR
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
    
    def process_log_details(self,
        log_path: Path = None,
        form_data: Dict = None) -> Dict:

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
            self._validate_and_parse(log_path, result, form_data)
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
            result['errors'].append(f": {str(e)}")

            # pprint(f"Done preparing: {result}")
            # print("BREAKPOINT")
            return result
        
        # Phase 3: Score
        try:
            self._score_qsos(prepared_qsos, result)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Scoring failed: {str(e)}")

            # pprint(f"Done scoring: {result}")
            # print("BREAKPOINT")
            return result
        
        return result
    
    def _init_result(self) -> Dict:
        """Initialize result dictionary with standardized structure"""
        return {
            'year': CONTEST_YEAR,
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
    
    def _validate_and_parse(self,
            log_path: Path,
            result: Dict,
            form_data: Dict) -> None:

        """Phase 1: Validate and parse header/QSOs"""
        qso_modes = set()
        
        if log_path:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                has_start, has_end = self._log_line_by_line(f, result)

        # pprint(f' AFTER process log headers: result: {result}')
        # print("BREAKPOINT")   
        
        # Check required fields
        if not has_start:
            result['errors'].append("Missing START-OF-LOG: 3.0")
            result['is_valid'] = False
        
        if not has_end:
            result['errors'].append("Missing END-OF-LOG:")
            result['is_valid'] = False
            
        if form_data:
            if form_data['callsign'] and result['callsign'] and result['callsign'] != form_data['callsign']:
                    result['errors'].append(f"CALLSIGN mismatch: log has {result['callsign']}, form has {form_data['callsign']}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Missing CALLSIGN:")
                result['is_valid'] = False
            
            if form_data['power'] and result['power_level'] and result['power_level'] != form_data['power']:
                    result['errors'].append(f"POWER mismatch: log has {result['power_level']}, form has {form_data['power']}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Missing CATEGORY-POWER:")
                result['is_valid'] = False
            
            if form_data['email'] and result['has_email'] and result['_header']['email'].lower() != form_data['email'].lower():
                result['errors'].append(f"Email mismatch: log has {result['_header']['email']}, form has {form_data['email']}")
                result['is_valid'] = False
            else:
                result['errors'].append("Missing EMAIL")
                result['is_valid'] = False

            if result['mode_category']:
                if form_data['mode'] and result['_header']['mode_category'].lower() != form_data['mode'].lower():
                    result['errors'].append(f"Mode mismatch: log has {result['_header']['mode_category']}, form has {form_data['mode']}")
                    result['is_valid'] = False
                else:
                    result['errors'].append("Missing MODE")
                    result['is_valid'] = False

            if form_data['email'] and result['email']:
                if form_data['email'] and result['_header']['email'].lower() != form_data['email'].lower():
                    result['errors'].append(f"Email mismatch: log has {result['_header']['email']}, form has {form_data['email']}")
                    result['is_valid'] = False
                else:
                    result['errors'].append("Missing EMAIL")
                    result['is_valid'] = False
        
        if result['total_qsos'] == 0:
            result['errors'].append("No QSOs found in log")
            result['is_valid'] = False

        if not result['is_valid']:
            return
        
        # Determine mode category from actual QSOs
        ###################FIXIT NOOOOO do not want to do it this way, we want to get the mode category from the header and then check for consistency with the modes in the QSOs.  If there is a violation, we should mark this as an error and reject the log.  We do not want to categorize a log as MIXED just because it has some phone and some cw/digital QSOs if the header says it is PHONE or CW-DIGITAL.  The header should be the source of truth for categorization, and the QSOs should be checked against that for consistency.
        
        ## I think we would rather just get the mode from the stated mode in the Cabrillo File
        ## if a QSO has a mode that violates this, I think we mark this as an error and reject the log

        # if has_phone and has_cw_digital:
        #     result['mode_category'] = 'MIXED'
        # elif has_phone:
        #     result['mode_category'] = 'PHONE'
        # elif has_cw_digital:
        #     result['mode_category'] = 'CW-DIGITAL'
        
        # Set power level from header
        result['power_level'] = result['_header'].get('power', 'LOW')
        
        # Set overlay from header
        result['overlay'] = result['_header'].get('overlay', None)

        # print("BREAKPOINT")

    # END of _validate_and_parse

    def _log_line_by_line(self, log_path, result: Dict):
        
        has_start = False
        has_end = False
        
        for line_num, line in enumerate(log_path, 1):
            # print(f'Processing line {line_num}: {line.strip()}')
            line = line.strip()
            if not line:
                continue
            
            # Check for START-OF-LOG and END-OF-LOG
            if line.startswith('START-OF-LOG:'):
                has_start = True
                continue
            if line.startswith('END-OF-LOG:'):
                has_end = True
                continue
            
            # Parse header fields (CALLSIGN, EMAIL, CATEGORY-POWER, etc.)
            if ':' in line and not line.startswith('QSO:'):
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                result['_header'][key] = value
                
                if key == 'callsign':
                    result['callsign'] = value.upper()
                elif key == 'name':
                    result['name'] = value
                elif key == 'category-mode':
                    result['mode_category'] = value.upper()
                elif key == 'email':
                    result['has_email'] = True
                    result['email'] = value
                elif key == 'category-power':
                    power_value = value.upper()
                    if power_value in ('QRP', 'LOW', 'HIGH'):
                        result['has_valid_power'] = True
                        result['_header']['power'] = power_value
                        result['power_level'] = power_value
                    else:
                        result['has_valid_power'] = False
                        result['errors'].append(f"Unrecognized power level: {value}")
                elif key == 'category-station':
                    station_value = value.upper()
                    if station_value in ('FIXED', 'PORTABLE', 'MOBILE', 'ROVER'):
                        result['_header']['station'] = station_value
                        result['mode_category'] = station_value
                    else:
                        result['warnings'].append(f"Unrecognized station type: {value}")
                elif key == 'category-overlay':
                    overlay_value = value.upper()
                    if overlay_value in ('WIRES', 'TB-WIRES', 'POTA'):
                        result['_header']['overlay'] = overlay_value
                    else:
                        result['warnings'].append(f"Unrecognized overlay: {value}")
                elif key == 'claimed-score':
                    try:
                        result['claimed_score'] = int(value)
                    except ValueError:
                        result['claimed_score'] = 0
                        result['warnings'].append(f"Invalid claimed score format: {value}")
                
                continue
            
            # Validate QSO lines and collect them for later processing
            if line.startswith('QSO:'):
                qso_error = self._validate_qso_line(line, line_num)
                if qso_error:
                    result['errors'].append(qso_error)
                    result['is_valid'] = False
                else:
                    result['_qso_lines'].append((line_num, line))
                    result['total_qsos'] += 1

        return has_start, has_end

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
            result['errors'].append(f"QSO at line {line_num}: Unrecognized mode {mode}")
            result['is_valid'] = False
            return f"Line {line_num}: Invalid mode {mode}"
        
        return None
    
    def _prepare_qsos(self, result: Dict) -> List[Dict]:
        """Phase 2: Prepare QSOs (convert freq, expand multi-parish, etc.)"""
        prepared = []
        # print(f"Initial prepared: {id(prepared)}")
        
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

                # check if sender in state or province
                
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
        pprint(f"mode_category = {result['mode_category']}")
        mode_abbrev = {
            'SSB': 'ph',
            'PHONE': 'ph',
            'CW/DIGITAL': 'cw',
            'MIXED': 'mx'
        }[result['mode_category']]
        
        power_abbrev = {
            'QRP': 'qp',
            'LOW': 'lo',
            'HIGH': 'hi'
        }[result['power_level']]
        
        result['category'] = f"{loc_abbrev}_{mode_abbrev}_{power_abbrev}"


        pprint(f"location_type: {result['location_type']}, category: {result['category']}\nPrepared {len(prepared)} QSOs; QSO Line {line_num}: Prepared {prepared}")
        # print("BREAKPOINT")
        
        return prepared
    
    ## END of prepare_qsos
    
    # get location type of a QSO's sender
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
        
        # a mult dup is when a QSO is a duplicate for multiplier purposes (same band/mode/rcvd_qth) but not a point dup (different rcvd_call).  These should be allowed but not count for multipliers.  A qso dup is when all of band/mode/rcvd_call are the same, in which case it should not count for points.
        mult_dups = []
        qso_dups = []
        # pprint(f"QSO Scoring for {result['callsign'].upper()}")
        for qso in qsos:
            band = qso['band']
            mode_cat = qso['mode_category']
            sent_call = qso['sent_call']
            rcvd_call = qso['rcvd_call']
            rcvd_qth = qso['rcvd_qth'].replace('DX', '')

            # Create checks for both types of duplicates - one for points (band/mode/rcvd_call) and one for multipliers (band/mode/rcvd_qth)
            mult_check = band + mode_cat + rcvd_qth
            qso_check = band + mode_cat + rcvd_call
            
            # if not a duplicate for QSO points purposes, get the points. Else add to the dup list and skip points
            qso_check = band + mode_cat + rcvd_call
            if qso_check in qso_dups:
                index = qso_dups.index(qso_check)
                # pprint(f"in qso_dups {index} / {qso_dups[index]} / {qso_check}")
                # pprint(f"Duplicate QSO detected band/mode/call worked: Line {qso['line_num']} band {band} mode {mode_cat} call worked {rcvd_call}")
                # pprint(f"QSO Dup Line {qso['line_num']} {qso['band']} {qso['mode_category']} {rcvd_call} {rcvd_qth}")
                result['warnings'].append(f"Duplicate QSO line {qso['line_num']} band/mode/call worked:  {band}/{mode_cat}/{rcvd_call}")
            else:  ## not a duplicate for points, so get points
                qso_dups.append(qso_check)

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
                    # pprint(f"Found N5LCC contact, total now: {result['num_n5lcc_contacts']}")

            ## add to correct multiplier list even if a dup for points, but check for mult dup first and warn if so.  This allows the multiplier to be counted for the first QSO but not for subsequent dup QSOs.
            if mult_check in mult_dups:
                # index = mult_dups.index(mult_check)
                # pprint(f"in mult_dups {index} / {mult_dups[index]} / {mult_check}")
                # pprint(f"Duplicate Multiplier detected band/mode/qth worked: Line {qso['line_num']} band {band} mode {mode_cat} qth worked {rcvd_qth}")
                # pprint(f"Mult Dup Line {qso['line_num']} {qso['band']} {qso['mode_category']} {rcvd_call} {rcvd_qth}")
                result['warnings'].append(f"Duplicate Multiplier line {qso['line_num']} band/mode/qth worked: {band}/{mode_cat}/{rcvd_qth}")
                # pprint(f"warnings: {result['warnings']}")
                # print("BREAKPOINT")

            else:
                mult_dups.append(mult_check)
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

        # pprint(f"Done qso_points: {result['qso_points']}")
        # print("BREAKPOINT")

        # Finished with points, now sum the individual multipliers
        for i in ['parishes', 'states', 'provinces', 'dx']:
            result['total_multipliers'] += result[f'{i}_worked_multiplier']
          
        # pprint(f"L TOTAL MULT: {result['total_multipliers']} basic multipliers: Parishes {result['parishes_worked_multiplier']}, States {result['states_worked_multiplier']}, Provinces {result['provinces_worked_multiplier']}, DX {result['dx_worked_multiplier']}")
        # print("BREAKPOINT")

        ## score before bonuses
        result['final_score'] = result['qso_points'] * max(1, result['total_multipliers'])

        # pprint(f'Final score before bonuses: {result["final_score"]}')
        # print('BREAKPOINT')

        ## add bonus points for one or more N5LCC contacts
        if result['worked_n5lcc']:
            result['final_score'] += N5LCC_BONUS

        ## Add rover bonus points for activated parishes
        if result['location_type'] == 'LA-ROVER':
            result['rover_bonus_points'] = len(result['parishes_activated']) * ROVER_PARISH_BONUS
            result['final_score'] += result['rover_bonus_points']
            
        # pprint(f'Final score with bonuses: {result["final_score"]}')
        # print('BREAKPOINT')

    ## END of score_qsos
    
    ## Utility functions

    # def _callsign_analyze(self, call: str)

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
                if i < 1:
                    return call[:1]
                else:
                    return call[:i]
        return call
    
## End of UnifiedLogProcessor class

# Convenience functions for single log processing in WEB app ONLY (not used for batch processing
def process_single_log(
        log_path: Path = None,
        form_data: Dict = None,
        log_content: str = None,
        parish_file: Path = Path(LA_PARISHES_FILE),
        state_province_file: Path = Path(WVE_ABBREVS_FILE)) -> Dict:
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
    # for debugging error messages
    # result = {
    #     'errors': ["This is a test error message", 'second message', 'third message'],
    #     'callsign': 'KJ5BYZ',
    # }
    # return result


    processor = UnifiedLogProcessor(parish_file, state_province_file)

    return processor.process_log_details(
        log_path,
        form_data)

def print_result(result):
    """Utility function to print result in a readable format"""
    print(f"Callsign: {result['callsign']} Errors: {len(result['errors'])}  Warnings: {len(result['warnings'])}")
    print(f"Category: {result['category']}")
    print(f"Location Type: {result['location_type']}")
    print(f"Mode Category: {result['mode_category']}")
    print(f"Power Level: {result['power_level']}")
    print(f"Overlay: {result['overlay']}")
    print(f"Final Score: {result['final_score']} (Claimed: {result['claimed_score']})")
    print(f"Total QSOs: {result['total_qsos']}  Valid QSOs: {result['valid_qsos']}  QSO Points: {result['qso_points']}")
    print(f"Total Multipliers: {result['total_multipliers']} (Parishes: {result['parishes_worked_multiplier']}, States: {result['states_worked_multiplier']}, Provinces: {result['provinces_worked_multiplier']}, DX: {result['dx_worked_multiplier']})")
    if result['is_rover']:
        print(f"Rover Bonus Points: {result['rover_bonus_points']} for activating parishes: {', '.join(result['parishes_activated'])}")
    if result['worked_n5lcc']:
        print(f"N5LCC Contacts: {result['num_n5lcc_contacts']} (Bonus points applied)")
    if result['warnings']:
        if len(result['warnings']) < 10:
            print("Warnings:")
            for w in result['warnings']:
                print(f"{w}")
        else:
            q = 0
            m = 0
            for w in result['warnings']:
                if w.startswith("Duplicate Q"):
                    q += 1
                else:
                    m += 1
            print(f"Warnings: {q} duplicate QSOs, {m} duplicate multipliers")

    if result['errors'] and len(result['errors']) < 10:
        if len(result['errors']) < 10:
            print("Errors:")
            for e in result['errors']:
                print(f"{e}")

def process_batch_logs(log_dir: Path,
    parish_file: Path = None,
    state_province_file: Path = None) -> Dict:
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
    for log_path in log_dir.glob('*.log'):
        result = processor.process_log_details(log_path)
        if result['claimed_score'] != result['final_score']:
            pprint(f"\n================================================\nScore mismatch for {str(log_path).split('/')[-1].split('.')[0].upper()}: claimed / calculated {result['claimed_score']} / {result['final_score']}")
            print_result(result)
            pprint("BREAKPOINT")
            result['warnings'].append(f"Score mismatch: claimed: {result['claimed_score']}  calculated: {result['final_score']}")
        else:
            pprint(f"\n================================================  SUCCESS!!! for {str(log_path).split('/')[-1].split('.')[0].upper()} Err: {len(result['errors'])} Wrn: {len(result['warnings'])}")
            pprint("BREAKPOINT")
            
        results.append(result)
    
    return results


if __name__ == "__main__":
    print("LAQP Unified Log Processor")
    print("This module should be imported, not run directly.")
    print()
    print("For web upload: from processor import process_single_log")
    print("For batch: from processor import process_batch_logs")
