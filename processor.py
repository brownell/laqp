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
    BONUS_CALLSIGN, LA_PARISHES_FILE, OVERLAY_VALUE_OPTIONS, POWER_VALUE_OPTIONS, STATION_VALUE_OPTIONS, WVE_ABBREVS_FILE,
    US_PREFIXES, CANADIAN_PREFIXES,
    PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    CALLSIGN_BONUS_POINTS, ROVER_PARISH_BONUS,
    PHONE_MODES, CW_DIGITAL_MODES, PROVINCES, CONTEST_YEAR, BAND_RANGES
)


class UnifiedLogProcessor:
    """
    Unified processor that combines validation, preparation, and scoring.
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
        self.first_call_qth = None  # To track the sent QTH in a log for checking other QSOs against it
    
    def _init_result(self) -> Dict:
        """Initialize result dictionary with standardized structure"""
        return {
            'year': CONTEST_YEAR,
            'callsign': '',
            'name': '',
            'overlay': None,  # 'WIRES', 'TB-WIRES', 'POTA', or None
            'location_type': 'NON-LA',  # 'DX', 'NON-LA', 'LA-FIXED', 'LA-ROVER'
            'mode_category': 'MIXED',  # 'PHONE', 'CW/DIGITAL', 'MIXED'
            'power_level': 'LOW',  # 'QRP', 'LOW', 'HIGH'
            'is_rover': False,
            'final_score': 0,
            'qso_points': 0,
            'total_qsos': 0, # total number validated, whether dups or not
            'valid_qsos': 0, #number of qsos that are not dups and contribute to the score
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
        
        #############################################
        # Phase 2: Prepare QSOs (in memory)
        #############################################
        try:
            prepared_qsos = self._prepare_qsos(result)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f": {str(e)}")
            return result
        
        #############################################
        # Phase 3: Score
        #############################################
        try:
            self._score_qsos(prepared_qsos, result)
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Scoring failed: {str(e)}")

            # pprint(f"Done scoring: {result}")
            # print("BREAKPOINT")
            return result
        
        return result
    
    def _validate_and_parse(self,
            log_path: Path,
            result: Dict,
            form_data: Dict) -> None:


        #############################################
        #Phase 1: Validate and parse header and QSO lines
        #############################################
        qso_modes = set()
        
        if log_path:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                self._log_line_by_line(f, result) 
        
        # Check required fields and cross-check with form data
            
        if form_data and result['is_valid']:
            if form_data['callsign'] and result['callsign']:
                if result['callsign'].upper() != form_data['callsign'].upper():
                    result['errors'].append(f"CALLSIGN mismatch: log has {result['callsign'].upper()}, form has {form_data['callsign'].upper()}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Callsign is missing from log or form:")
                result['is_valid'] = False
            
            if form_data['power'] and result['power_level']:
                if result['power_level'].lower() != form_data['power'].lower():
                    result['errors'].append(f"POWER mismatch: log has {result['power_level'].upper()}, form has {form_data['power'].upper()}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Power is missing from log or form:")
                result['is_valid'] = False
            
            if form_data['email'] and result['email']:
                if result['email'].lower() != form_data['email'].lower():
                    result['errors'].append(f"Email mismatch: log has {result['email'].lower()}, form has {form_data['email'].lower()}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Email is missing from log or form:")
                result['is_valid'] = False

            if form_data['mode'] and result['_header']['category-mode']:
                if form_data['mode'] and result['_header']['category-mode'].lower() != form_data['mode'].lower():
                    result['errors'].append(f"Mode mismatch: log has {result['_header']['category-mode'].upper()}, form has {form_data['mode'].upper()}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Mode is missing from log or form:")
                result['is_valid'] = False

            if form_data['station_type'] and result['location_type']:
                if form_data['station_type'] and result['location_type'].lower() != form_data['station_type'].lower():
                    result['errors'].append(f"Station mismatch: log has {result['location_type'].upper()}, form has {form_data['station_type'].upper()}")
                    result['is_valid'] = False
            else:
                result['errors'].append("Station is missing from log or form:")
                result['is_valid'] = False

            if form_data['overlay'] and result['location_type']:
                if form_data['station_type'] and result['location_type'].lower() != form_data['station_type'].lower():
                    result['errors'].append(f"Station mismatch: log has {result['location_type'].upper()}, form has {form_data['station_type'].upper()}")
                    result['is_valid'] = False

        ## Done with Cabrillo Header, now do QSOs
        
        if result['total_qsos'] == 0:
            result['errors'].append("No QSOs found in log")
            result['is_valid'] = False

        if not result['is_valid']:
            return
        
        # Determine mode category from actual QSOs
        ################### TODO FIXIT NOOOOO do not want to do it this way, we want to get the mode category from the header and then check for consistency with the modes in the QSOs.  If there is a violation, we should mark this as an error and reject the log.  We do not want to categorize a log as MIXED just because it has some phone and some cw/digital QSOs if the header says it is PHONE or CW-DIGITAL.  The header should be the source of truth for categorization, and the QSOs should be checked against that for consistency.
        
        ## I think we would rather just get the mode from the stated mode in the Cabrillo File
        ## if a QSO has a mode that violates this, I think we mark this as an error and reject the log

        # if has_phone and has_cw_digital:
        #     result['mode_category'] = 'MIXED'
        # elif has_phone:
        #     result['mode_category'] = 'PHONE'
        # elif has_cw_digital:
        #     result['mode_category'] = 'CW-DIGITAL'

    # END of _validate_and_parse

    def _log_line_by_line(self, log_path, result: Dict):
        
        has_start = False
        has_end = False
        first_qso_line = True
        
        for line_num, line in enumerate(log_path, 1):
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
            
            # Parse header fields (CALLSIGN, NAME, EMAIL, CATEGORY-POWER, CATEGORY-MODE, CATEGORY-STATION, CATEGORY-OVERLAY, CLAIMED-SCORE)
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
                    result['email'] = value
                elif key == 'category-power':
                    power_value = value.upper()
                    if power_value in POWER_VALUE_OPTIONS:
                        result['power_level'] = power_value
                    else:
                        result['errors'].append(f"Unrecognized power level: {value}")

                elif key == 'category-station':
                    station_value = value.upper()
                    if station_value in STATION_VALUE_OPTIONS:
                        result['location_type'] = station_value
                    else:
                        result['warnings'].append(f"Unrecognized station type: {value}")

                elif key == 'category-overlay':
                    overlay_value = value.upper()
                    if overlay_value in OVERLAY_VALUE_OPTIONS:
                        result['overlay'] = overlay_value
                    else:
                        result['warnings'].append(f"Unrecognized overlay: {value}")

                elif key == 'claimed-score':
                    try:
                        result['claimed_score'] = int(value)
                    except ValueError:
                        result['claimed_score'] = -1
                        result['warnings'].append(f"Invalid claimed score format: {value}")
                
                continue
            
            # Validate QSO lines and collect them for later processing
            if line.startswith('QSO:'):
                qso_ok = self._validate_qso_line(result, line, line_num, first_qso_line)
                if qso_ok:
                    result['_qso_lines'].append((line_num, line))
                    result['total_qsos'] += 1
                first_qso_line = False

        return
    ## END of _log_line_by_line
    
    def _validate_qso_line(self, result, line: str, line_num: int, first_qso_line: bool) -> Optional[bool]:

        parts = line.split()
        if len(parts) < 11:
            result['warnings'].append(f"Line {line_num}: {line} Insufficient number of QSO fields")
            return False
        
        # Validate frequency
        try:
            freq = int(parts[1])
            band = freq_to_band(freq)
            if band == 0:
                result['warnings'].append(f"Line {line_num}: {line} Invalid frequency {freq} kHz")
                return False
        except (ValueError, IndexError):
            result['warnings'].append(f"Line {line_num}: {line} Invalid frequency format")
            return False
        
        # Validate mode
        mode = parts[2]
        if mode not in PHONE_MODES and mode not in CW_DIGITAL_MODES and mode != 'MIXED':
            result['warnings'].append(f"QSO at line {line_num}: {line} Unrecognized mode {mode}")
            return False
            
        if result['mode_category'] == 'SSB' and mode not in PHONE_MODES and mode != 'MIXED':
            result['warnings'].append(f"QSO at line {line_num}: {line} Mode {mode} does not match header CATEGORY-MODE {result['mode_category']}")
            return False
            
        if result['mode_category'] == 'CW/DIGITAL' and mode not in CW_DIGITAL_MODES and mode != 'MIXED':
            result['warnings'].append(f"QSO at line {line_num}: {line} Mode {mode} does not match header CATEGORY-MODE {result['mode_category']}")
            return False
        
        if first_qso_line:
            self.first_call_qth = parts[7]
        else:
            if parts[7] != self.first_call_qth:
                result['warnings'].append(f"QSO at line {line_num}: {line} Sent QTH {parts[7]} does not match first QSO sent QTH {self.first_call_qth}")
                return False
   
        return True
    
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
            
            # TODO check what this means and when it happens
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

                # TODO check if sender in state or province
                
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
        
        # Get info that is NOT specific to each QSO but is needed for scoring (e.g., location type)
        # Determine location type from prepared QSOs
        result['location_type'] = self._determine_location_type(result, prepared, result['_header'])
        result['is_rover'] = (result['location_type'] == 'LA-ROVER')
        
        return prepared
    
    ## END of prepare_qsos
    
    # get location type of a QSO's sender
    def _determine_location_type(self, result, qsos: List[Dict], header: Dict) -> str:
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
        station = result['location_type']  # Get station type
        
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
        
        # A mult dup is when a QSO is a duplicate for multiplier purposes (same band/mode/rcvd_qth) but not a point dup (different rcvd_call).  These sqso points but not  multipliers.  
        # A qso dup is when all of band/mode/rcvd_call are the same, in which case it should not count for points or multipliers.
        mult_dups = []
        qso_dups = []
        # pprint(f"QSO Scoring for {result['callsign'].upper()}")
        for qso in qsos:
            band = qso['band']
            mode_cat = qso['mode_category']
            sent_call = qso['sent_call']
            rcvd_call = qso['rcvd_call']
            rcvd_qth = qso['rcvd_qth'].replace('DX', '')
            
            # if not a duplicate for QSO points purposes, get the points. Else add to the dup list and skip points
            qso_check = band + mode_cat + rcvd_call
            if qso_check in qso_dups:
                # print(f"!!! DUPLICATEte QSO line {qso['line_num']} band/mode/call worked:  {band}/{mode_cat}/{rcvd_call}")
                result['warnings'].append(f"Duplicate QSO line {qso['line_num']} band/mode/call worked:  {band}/{mode_cat}/{rcvd_call}")
            else:  ## not a duplicate for points, so get points
                result['valid_qsos'] += 1
                # print(f"NOT DUP QSO line {qso['line_num']} band/mode/call worked:  {band}/{mode_cat}/{rcvd_call}")
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
                    # print(f"qso_points {result['qso_points']} total_qsos {result['total_qsos']} valid_qsos {result['valid_qsos']}")
                    result['qsos_by_mode']['Phone'] += 1
                else:  # CW/Digital
                    result['qso_points'] += CW_DIGITAL_QSO_POINTS
                    # print(f"qso_points {result['qso_points']} total_qsos {result['total_qsos']} valid_qsos {result['valid_qsos']}")
                    result['qsos_by_mode']['CW/Digital'] += 1

                # Check for N5LCC
                if rcvd_call == 'N5LCC':
                    result['worked_n5lcc'] = True
                    result['num_n5lcc_contacts'] += 1
            ## add to correct multiplier list even if a dup for points, but check for mult dup first and warn if so.  This allows the multiplier to be counted for the first QSO but not for subsequent dup QSOs.
            mult_check = band + mode_cat + rcvd_qth
            if mult_check in mult_dups:
                print(f"!!! DUPLICATEte MULT: line {qso['line_num']} band/mode/QTH worked:  {band}/{mode_cat}/{rcvd_qth}")
                result['warnings'].append(f"Duplicate Multiplier line {qso['line_num']} band/mode/qth worked: {band}/{mode_cat}/{rcvd_qth}")

            else:
                print(f"NOT DUP MULT: line {qso['line_num']} band/mode/QTH worked:  {band}/{mode_cat}/{rcvd_qth}")
                mult_dups.append(mult_check)
                ## Everyone gets parish multiplier for parishes, but only LA stations get state/province/DX multipliers
                if rcvd_qth in self.parishes:
                    result['parishes_worked'].add(rcvd_qth)
                    result['parishes_worked_multiplier'] += 1
                else:  # qth is NOT a parish
                    print(f"have a qth that is NOT a parish: rcvd_qth {rcvd_qth}")
                
                    # LA stations get state, province, and DX multipliers
                    if result['location_type'] == 'LA-FIXED' or result['location_type'] == 'LA-ROVER':
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


        # Finished with points, now sum the individual multipliers
        for i in ['parishes', 'states', 'provinces', 'dx']:
            result['total_multipliers'] += result[f'{i}_worked_multiplier']
          

        ## score before bonuses
        result['final_score'] = result['qso_points'] * result['total_multipliers']

        ## add bonus points for one or more N5LCC contacts
        if result['worked_n5lcc']:
            result['final_score'] += CALLSIGN_BONUS_POINTS

        ## Add rover bonus points for activated parishes
        if result['location_type'] == 'LA-ROVER':
            result['rover_bonus_points'] = len(result['parishes_activated']) * ROVER_PARISH_BONUS
            result['final_score'] += result['rover_bonus_points']

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

# Convenience functions for single log processing in WEB app ONLY (not used for batch processing)
def process_single_log(
        log_path: Path = None,
        form_data: Dict = None,
        log_content: str = None,
        parish_file: Path = Path(LA_PARISHES_FILE),
        state_province_file: Path = Path(WVE_ABBREVS_FILE)) -> Dict:
    """
    Process a single log file (for web uploads ONLY).
    
    Args:
        log_path: Path to log file
        parish_file: Path to parish abbreviations (optional, uses default)
        state_province_file: Path to state/province abbreviations (optional, uses default)
        **form_data: Optional form fields (email, mode, power, station, overlay)
    
    Returns:
        Result dictionary
    """
    processor = UnifiedLogProcessor(parish_file, state_province_file)

    return processor.process_log_details(
        log_path,
        form_data)

def print_result(result):
    """Utility function to print result in a readable format"""
    print(f"Callsign: {result['callsign']} Errors: {len(result['errors'])}  Warnings: {len(result['warnings'])}")
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
    # print(f"ready to process_log_details for logs in {log_dir}")
    for log_path in log_dir.glob('*.log'):
        result = processor.process_log_details(log_path)
        print(f"Finished processing {log_path.name}: Score {result['final_score']} Errors: {len(result['errors'])} Warnings: {len(result['warnings'])}")
        results.append(result)
    
    return results

def freq_to_band(freq_khz: int) -> int:
    """
    Convert frequency in kHz to band in meters.
    
    Args:
        freq_khz: Frequency in kHz
    
    Returns:
        Band in meters (e.g., 20, 40, 80) or None if not in a valid band
    """
    for band, (min_freq, max_freq) in BAND_RANGES.items():
        if min_freq <= freq_khz <= max_freq:
            return band
    return None


if __name__ == "__main__":
    print("LAQP Unified Log Processor")
    print("This module should be imported, not run directly.")
    print()
    print("For web upload: from processor import process_single_log")
    print("For batch: from processor import process_batch_logs")
