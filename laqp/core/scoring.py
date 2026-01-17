"""
Louisiana QSO Party Scoring Module

Scores prepared logs according to LA rules:
- QSO Points: 2 for phone, 4 for CW/digital
- Multipliers: Per band AND per mode type (CW/Digital vs Phone)
  - Non-LA: LA parishes only
  - LA: Parishes + States + Provinces + DXCC
- Bonuses:
  - N5LCC: 100 pts one-time for working club station
  - Rover activation: 50 pts per parish activated (rovers only)

Adapted from TQP scoring.py for LA rules.
"""
import sys
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import (
    PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    N5LCC_BONUS, ROVER_PARISH_ACTIVATION_BONUS,
    LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    CW_DIGITAL_MODES, PHONE_MODES,
    LOC_NON_LA, LOC_LA_FIXED, LOC_LA_ROVER
)


class ScoreCalculator:
    """Calculates scores for LAQP logs"""
    
    def __init__(self, parish_file: Path, state_province_file: Path):
        # Load reference data
        with open(parish_file, 'r') as f:
            self.parish_list = [line.strip().upper() for line in f if line.strip()]
        
        with open(state_province_file, 'r') as f:
            self.state_province_list = [line.strip().upper() for line in f if line.strip()]
    
    def is_la_parish(self, qth: str) -> bool:
        """Check if QTH is LA parish"""
        return qth in self.parish_list
    
    def is_non_la_state_province(self, qth: str) -> bool:
        """Check if QTH is non-LA state or province"""
        return qth in self.state_province_list
    
    def get_mode_type(self, mode: str) -> str:
        """Get mode type for multiplier tracking"""
        if mode in CW_DIGITAL_MODES:
            return "CW/Digital"
        else:
            return "Phone"
    
    def calculate_qso_points(self, mode: str) -> int:
        """Calculate points for a single QSO"""
        if mode in CW_DIGITAL_MODES:
            return CW_DIGITAL_QSO_POINTS  # 4 points
        else:
            return PHONE_QSO_POINTS  # 2 points
    
    def score_log(self, log_path: Path) -> Dict:
        """
        Score a prepared log file.
        
        Returns dictionary with complete scoring breakdown.
        """
        result = {
            'callsign': '',
            'email': '',
            'category': '',
            'club': '',
            'operators': '',
            'claimed_score': 0,
            
            # QSO counts
            'total_qsos': 0,
            'cw_qsos': 0,
            'phone_qsos': 0,
            'digital_qsos': 0,
            
            # Band counts
            'qsos_160m': 0,
            'qsos_80m': 0,
            'qsos_40m': 0,
            'qsos_20m': 0,
            'qsos_15m': 0,
            'qsos_10m': 0,
            'qsos_6m': 0,
            'qsos_2m': 0,
            
            # Points
            'raw_qso_points': 0,
            
            # Multipliers
            'total_multipliers': 0,
            'multiplier_list': [],
            
            # Score before bonus
            'score_before_bonus': 0,
            
            # Bonuses
            'n5lcc_bonus': 0,
            'rover_bonus': 0,
            'total_bonus': 0,
            
            # Final score
            'final_score': 0,
            'score_reduction': 0,
            
            # Rover details
            'parishes_activated': [],
            
            # Location type (for multiplier logic)
            'location_type': LOC_NON_LA,
            'is_rover': False
        }
        
        # Track dupes: key = "call_band_mode_sent_qth_rcvd_qth"
        dupe_tracker = set()
        
        # Track multipliers: key = "band_modetype_qth"
        # LA rules: multipliers are per band AND per mode type
        multiplier_tracker = set()
        
        # Track parishes activated (for rovers)
        sent_parishes = set()
        
        # Track if N5LCC was worked
        worked_n5lcc = False
        
        # Parse log
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip().upper()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                tag = parts[0]
                
                # Parse header
                if tag == "CALLSIGN:":
                    result['callsign'] = parts[1] if len(parts) > 1 else ''
                
                elif tag == "EMAIL:":
                    result['email'] = parts[1].lower() if len(parts) > 1 else ''
                
                elif tag == "TQP-CATEGORY:":
                    # Category added by preparation
                    result['category'] = ' '.join(parts[1:])
                    # Determine location type from category
                    if "LA ROVER" in result['category']:
                        result['location_type'] = LOC_LA_ROVER
                        result['is_rover'] = True
                    elif "LA" in result['category'] and "NON-LA" not in result['category']:
                        result['location_type'] = LOC_LA_FIXED
                    else:
                        result['location_type'] = LOC_NON_LA
                
                elif tag == "CLUB:":
                    result['club'] = ' '.join(parts[1:])
                
                elif tag == "OPERATORS:":
                    result['operators'] = ' '.join(parts[1:]).replace(',', '')
                
                elif tag == "CLAIMED-SCORE:":
                    try:
                        result['claimed_score'] = int(parts[1].replace(',', '')) if len(parts) > 1 else 0
                    except ValueError:
                        result['claimed_score'] = 0
                
                # Parse QSO
                elif tag == "QSO:":
                    if len(parts) < 11:
                        continue
                    
                    band = parts[1]
                    mode = parts[2]
                    sent_call = parts[5]
                    sent_qth = parts[7]
                    rcvd_call = parts[8]
                    rcvd_qth = parts[10]
                    
                    # Build dupe key
                    dupe_key = f"{rcvd_call}_{band}_{mode}_{sent_call}_{sent_qth}_{rcvd_qth}"
                    
                    # Skip if dupe
                    if dupe_key in dupe_tracker:
                        continue
                    
                    dupe_tracker.add(dupe_key)
                    
                    # Count QSO
                    result['total_qsos'] += 1
                    
                    # Count by mode
                    if mode == "CW":
                        result['cw_qsos'] += 1
                    elif mode in ("PH", "FM"):
                        result['phone_qsos'] += 1
                    elif mode in ("DG", "RY"):
                        result['digital_qsos'] += 1
                    
                    # Count by band
                    band_key = f'qsos_{band}m'
                    if band_key in result:
                        result[band_key] += 1
                    
                    # Calculate QSO points
                    qso_pts = self.calculate_qso_points(mode)
                    result['raw_qso_points'] += qso_pts
                    
                    # Track multipliers
                    mode_type = self.get_mode_type(mode)
                    
                    # Non-LA stations: only LA parishes count as multipliers
                    # LA stations: parishes + states + provinces + DXCC count
                    if result['location_type'] == LOC_NON_LA:
                        # Only count LA parishes
                        if self.is_la_parish(rcvd_qth):
                            mult_key = f"{band}_{mode_type}_{rcvd_qth}"
                            multiplier_tracker.add(mult_key)
                    else:
                        # LA station: count everything
                        mult_key = f"{band}_{mode_type}_{rcvd_qth}"
                        multiplier_tracker.add(mult_key)
                    
                    # Track parishes sent from (for rovers)
                    if self.is_la_parish(sent_qth):
                        sent_parishes.add(sent_qth)
                    
                    # Check if worked N5LCC
                    if rcvd_call == "N5LCC":
                        worked_n5lcc = True
        
        # Calculate multipliers
        result['total_multipliers'] = len(multiplier_tracker)
        result['multiplier_list'] = sorted(list(multiplier_tracker))
        
        # Calculate score before bonus
        result['score_before_bonus'] = result['raw_qso_points'] * result['total_multipliers']
        
        # Calculate bonuses
        if worked_n5lcc:
            result['n5lcc_bonus'] = N5LCC_BONUS
        
        if result['is_rover']:
            result['parishes_activated'] = sorted(list(sent_parishes))
            result['rover_bonus'] = len(sent_parishes) * ROVER_PARISH_ACTIVATION_BONUS
        
        result['total_bonus'] = result['n5lcc_bonus'] + result['rover_bonus']
        
        # Calculate final score
        result['final_score'] = result['score_before_bonus'] + result['total_bonus']
        
        # Calculate score reduction from claimed
        result['score_reduction'] = max(0, result['claimed_score'] - result['final_score'])
        
        return result


def score_single_log(log_path: Path, parish_file: Path, state_province_file: Path) -> Dict:
    """
    Score a single prepared log file.
    
    Args:
        log_path: Path to prepared log
        parish_file: Path to parish abbreviations
        state_province_file: Path to state/province abbreviations
    
    Returns:
        Dictionary with complete scoring breakdown
    """
    calculator = ScoreCalculator(parish_file, state_province_file)
    return calculator.score_log(log_path)


def generate_score_report(score_result: Dict) -> List[str]:
    """Generate a text report from score results"""
    report = []
    report.append(f"Score Report for {score_result['callsign']}")
    report.append("=" * 60)
    report.append(f"Category: {score_result['category']}")
    report.append(f"Email: {score_result['email']}")
    if score_result['club']:
        report.append(f"Club: {score_result['club']}")
    if score_result['operators']:
        report.append(f"Operators: {score_result['operators']}")
    report.append("")
    
    report.append("QSO Counts:")
    report.append(f"  Total QSOs: {score_result['total_qsos']}")
    report.append(f"  CW: {score_result['cw_qsos']}")
    report.append(f"  Phone: {score_result['phone_qsos']}")
    report.append(f"  Digital: {score_result['digital_qsos']}")
    report.append("")
    
    report.append("QSOs by Band:")
    for band in [160, 80, 40, 20, 15, 10, 6, 2]:
        count = score_result[f'qsos_{band}m']
        if count > 0:
            report.append(f"  {band}m: {count}")
    report.append("")
    
    report.append("Scoring:")
    report.append(f"  Raw QSO Points: {score_result['raw_qso_points']}")
    report.append(f"  Total Multipliers: {score_result['total_multipliers']}")
    report.append(f"  Score (before bonus): {score_result['score_before_bonus']}")
    report.append("")
    
    if score_result['total_bonus'] > 0:
        report.append("Bonuses:")
        if score_result['n5lcc_bonus'] > 0:
            report.append(f"  N5LCC Bonus: {score_result['n5lcc_bonus']}")
        if score_result['rover_bonus'] > 0:
            report.append(f"  Rover Activation ({len(score_result['parishes_activated'])} parishes): {score_result['rover_bonus']}")
            report.append(f"    Parishes: {', '.join(score_result['parishes_activated'])}")
        report.append(f"  Total Bonus: {score_result['total_bonus']}")
        report.append("")
    
    report.append(f"FINAL SCORE: {score_result['final_score']}")
    report.append("")
    
    if score_result['claimed_score'] > 0:
        report.append(f"Claimed Score: {score_result['claimed_score']}")
        if score_result['score_reduction'] > 0:
            report.append(f"Score Reduction: {score_result['score_reduction']}")
    
    return report


if __name__ == "__main__":
    print("LAQP Scoring Module")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
