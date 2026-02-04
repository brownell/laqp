"""
Louisiana QSO Party - Scoring Module (Updated for 36 categories)

Calculates scores for validated and prepared logs.
Tracks detailed statistics for individual result files.

Changes from original:
- Uses 36-category system (location × mode × power)
- Tracks overlay information separately
- Gathers detailed statistics (parishes, states, provinces, DX)
- Tracks QSOs by band and mode
- Calculates category placements
"""
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from laqp.categories import get_category_names, get_overlay_name

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import (
    LA_ROVER, OUTSIDE_LA, PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    N5LCC_BONUS, ROVER_PARISH_BONUS,
    PHONE_MODES, CW_DIGITAL_MODES,
    LOC_DX, LOC_NON_LA, LOC_LA_FIXED, LOC_LA_ROVER, PROVINCES,
    MODE_PHONE_ONLY, MODE_CW_DIGITAL_ONLY, MODE_MIXED,
    POWER_QRP, POWER_LOW, POWER_HIGH,
    OVERLAY_NONE, OVERLAY_WIRES, OVERLAY_TB_WIRES, OVERLAY_POTA,
    PREPARED_LOGS, LA_FIXED, LA_ROVER
)

class ScoreCalculator:
    """Calculate scores for LAQP logs"""
    
    def __init__(self, parishes: List[str], states_provinces: List[str]):
        """
        Initialize score calculator.
        
        Args:
            parishes: List of valid LA parish abbreviations
            states_provinces: List of valid state/province abbreviations
        """
        self.parishes = set(p.upper() for p in parishes)
        self.states_provinces = set(s.upper() for s in states_provinces)
    
    def score_log(self, log_path: Path) -> Dict:
        """
        Calculate score for a prepared log file.
        
        Returns result dict
        """
            
        # Define and initialize result
        result = {
            'callsign': '',  #  Station callsign
            'category': '',  #  Short category name (e.g., 'nl_ph_lo')
            'overlay': None,  # Overlay name ('WIRES', 'TB-WIRES', 'POTA', or None)
            'location_type': LOC_NON_LA,  #  
            'mode_category': MODE_MIXED,  #  
            'power_level': POWER_LOW,  #  
            'final_score': 0,  # Total calculated score WITH bonuses 
            'qso_points': 0,  #  Points from QSOs only (absent multipliers, dups INCLUDED)
            'total_qsos': 0,  #  Total number of QSOs
            'valid_qsos': 0,  #  Number of valid QSOs (for scoring, absent multipliers, dups EXCLUDED)
            'total_multiplier': 0,  # Total multiplier count (multiplied by QSO points for final score) 
            'parishes_worked': set(),  #  Unique parishes worked by NON LA stations
            'parishes_worked_multiplier': 0,  # Count of non-dup parishes multipliers
            'states_worked': set(),  #  Unique states worked by LA resident  stationss
            'states_worked_multiplier': 0,  #  Count of non-dup state multipliers
            'provinces_worked': set(),  #  Unique  provinces worked by LA resident  stations
            'provinces_worked_multiplier': 0,  #  Count of non-dup provinces multipliers
            'dx_worked': set(),  #  Unique DX worked by LA resident  stations
            'dx_worked_multiplier': 0,  #  Count of non-dup DX multipliers
            'parishes_activated': set(),  #  Unique parishes activated (rovers and others)
            'rover_bonus_points': 0,  #  
            'worked_n5lcc': False,  #  
            'num_n5lcc_contacts': 0,  #  
            'qsos_by_band': { '160': 0, '80': 0, '40': 0, '20': 0, '15': 0, '10': 0, '6': 0, '2': 0 },  #  
            'qsos_by_mode': {'Phone': 0, 'CW/Digital': 0},  #  
            'qsos_by_hour': {i: 0 for i in range(12)},  #  
            'bands_worked': [],  #  
            'multipliers_by_band_mode': {},  #  
            'name': '',  #  
            'claimed_score': 0,  #  
        
        }
        

        # for allowing duplicate conttacts with same mode, same contact, but different band
        dups = []
        # Parse log file
        # print(f'*******Processing log: {log_path}******')
        # print(f'checkpoint')
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip().upper()
                if not line:
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                tag = parts[0]

                # Get header information
                if tag == 'CALLSIGN:':
                    result['callsign'] = parts[1] if len(parts) > 1 else ''
                    # print(f'\n*******Processing log for callsign: {result["callsign"]}******')
                    if result['callsign'] == '':
                        raise ValueError(f"Missing callsign in log: {log_path}")

                elif tag == 'NAME:':
                    result['name'] = ' '.join(parts[1:]) if len(parts) > 1 else ''

                elif tag == 'CLAIMED-SCORE:':
                    if len(parts) > 1:
                        try:
                            result['claimed_score'] = int(parts[1])
                        except ValueError:
                            result['claimed_score'] = 0
                
                elif tag == 'LAQP-CATEGORY:':
                    # Format: "location,mode,power"
                    if len(parts) > 1:
                        result['category'] = parts[1]
                        cat_parts = parts[1].split('_')
                        result['location_type'] = cat_parts[0] if len(cat_parts) >= 1 else LOC_NON_LA    

                elif tag == "CATEGORY-OVERLAY":
                    result['overlay'] = parts[1] if len(parts) > 1 else None

                elif tag == "CATEGORY-POWER":
                    result['power_level'] = parts[1] if len(parts) > 1 else None

                elif tag == "CATEGORY-MODE":
                    result['mode_category'] = parts[1] if len(parts) > 1 else None
                               
                # Count QSOs and calculate points
                elif tag == 'QSO:':
                    result['total_qsos'] += 1
                    # print(f'QSO : {line}')
                    
                    if len(parts) >= 11:
                        # Parse QSO line
                        meters = parts[1]
                        mode = parts[2]
                        call_sent = parts[5]
                        qth_sent = parts[7]
                        call_rcvd = parts[8]
                        qth_rcvd = parts[10]
                    else:  # Malformed QSO line
                        continue

                    # if same received call, mode, and band, it is a duplicate and does not count at all
                    # e.g. QSO: 40 CW 2024-04-06 1406 AA2AD 599 PA KZ5D 599 IBER
                    dup_check = call_sent.upper() + call_rcvd.upper() + qth_sent.upper() + qth_rcvd + mode + str(meters)
                    if dup_check in dups:
                        continue
                    else:
                        dups.append(dup_check)
                        
                    # Check if worked N5LCC
                    if call_rcvd.upper() == 'N5LCC':
                        result['worked_n5lcc'] = True
                        result['num_n5lcc_contacts'] += 1
                    
                    # Count by mode
                    if mode in PHONE_MODES:
                        result['qsos_by_mode']['Phone'] += 1
                        qso_points = PHONE_QSO_POINTS
                    elif mode in CW_DIGITAL_MODES:
                        result['qsos_by_mode']['CW/Digital'] += 1
                        qso_points = CW_DIGITAL_QSO_POINTS
                    else:
                        qso_points = PHONE_QSO_POINTS  # Default
                    
                    result['qso_points'] += qso_points
                    result['valid_qsos'] += 1
                    
                    # Track multipliers (QTH worked)
                    qth_rcvd_upper = qth_rcvd.upper()
                       
                    # ALL stations can  work LA stations
                    
                    if qth_rcvd_upper in self.parishes:
                        result['parishes_worked'].add(qth_rcvd_upper)
                        result['parishes_worked_multiplier'] += 1

                    # if sender station is LA - count parishes sent from
                    if (result['location_type'] == LA_FIXED or result['location_type'] == LA_ROVER):
                        result['parishes_activated'].add(qth_sent.upper())

                        if qth_rcvd_upper in self.states_provinces:
                            # Distinguish between states and provinces
                            if qth_rcvd_upper in PROVINCES:
                                result['provinces_worked'].add(qth_rcvd_upper)
                                result['provinces_worked_multiplier'] += 1
                            else:
                                result['states_worked'].add(qth_rcvd_upper)
                                result['states_worked_multiplier'] += 1
                        elif qth_rcvd_upper not in self.parishes:
                            # Not a state, province, or parish: assume DX
                            result['dx_worked'].add(qth_rcvd_upper)
                            result['dx_worked_multiplier'] += 1
        
        # Calculate multipliers
        # caller is NOT LA station
        if result['location_type'] == OUTSIDE_LA:
            result['total_multiplier'] = result['parishes_worked_multiplier']
        
        # caller is LA stations: parishes + states + provinces + DX, per band/mode
        # For now, simplified: total unique entities
        else:
            result['total_multiplier'] = (
                result['parishes_worked_multiplier'] +
                result['states_worked_multiplier'] +
                result['provinces_worked_multiplier'] +
                result['dx_worked_multiplier']
            )
        
        # Calculate final score
        result['final_score'] = result['qso_points'] * result['total_multiplier']
        
        # Add N5LCC bonus
        if result['worked_n5lcc']:
            result['final_score'] += N5LCC_BONUS
        
        if result['location_type'] == LOC_LA_ROVER:
            result['final_score'] += result['parishes_activated'] * ROVER_PARISH_BONUS

        # Get list of bands worked
        result['bands_worked'] = sorted(result['qsos_by_band'].keys())

        if result['claimed_score'] != 0 and result['claimed_score'] != result['final_score']:
            print(f"\n**************  E R R O R: {result['callsign']} claimed score {result['claimed_score']} does not match calculated score {result['final_score']}\n**************  {result['num_n5lcc_contacts']} contacts with N5LCC")
            print(result)
                
        return result
    
    def _meters_to_index(self, meters: int):
        return {
            160: 0,
            80: 1,
            40: 2,
            20: 3,
            15: 4,
            10: 5,
            6: 6,
            2: 7
        }[meters]

def score_single_log(log_path: Path, 
                    parish_file: Path,
                    state_province_file: Path,
                    output_dir: Path = None) -> Dict:
    """
    Score a single prepared log file.
    
    Args:
        log_path: Path to prepared log file
        parish_file: Path to parish abbreviations file
        state_province_file: Path to state/province abbreviations file
        output_dir: Optional output directory (not used, kept for compatibility)
    
    Returns:
        Dict with scoring results
    """
    # Load reference data
    with open(parish_file, 'r') as f:
        parishes = [line.strip() for line in f if line.strip()]
    
    with open(state_province_file, 'r') as f:
        states_provinces = [line.strip() for line in f if line.strip()]
    
    # Create calculator and score
    calculator = ScoreCalculator(parishes, states_provinces)
    result = calculator.score_log(log_path)
    
    return result


def score_all_logs(prepared_logs_dir: Path,
                   parish_file: Path,
                   state_province_file: Path) -> Tuple[List[Dict], Dict[str, List[Dict]]]:
    """
    Score all prepared logs and organize by category.
    
    Args:
        prepared_logs_dir: Directory containing prepared logs
        parish_file: Path to parish abbreviations file
        state_province_file: Path to state/province abbreviations file
    
    Returns:
        Tuple of:
            - List of all score dicts (sorted by score, highest first)
            - Dict of {category: [score dicts]} for each category
    """
    # Load reference data
    with open(parish_file, 'r') as f:
        parishes = [line.strip() for line in f if line.strip()]
    
    with open(state_province_file, 'r') as f:
        states_provinces = [line.strip() for line in f if line.strip()]
    
    calculator = ScoreCalculator(parishes, states_provinces)
    
    # Score all logs
    all_scores = []
    category_scores = defaultdict(list)
    
    log_files = sorted(prepared_logs_dir.glob('*.log'))
    
    print(f"Scoring {len(log_files)} logs...")
    
    for log_file in log_files:
        result = calculator.score_log(log_file)
        
        # Store in all_scores
        all_scores.append(result)
        
        # Store in category
        category_scores[result['category']].append(result)
        
        # If has overlay, also store in base category with note
        # if result['overlay']:
        #     # Make a copy for base category
        #     base_result = result.copy()
        #     category_scores[result['base_category']].append(base_result)
        
        # print(f"  {result['callsign']}: {result['final_score']:,} points ({result['category']})")
    
    # Sort all scores by score (highest first)
    all_scores.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Sort each category by score
    for category in category_scores:
        category_scores[category].sort(key=lambda x: x['final_score'], reverse=True)
    
    return all_scores, dict(category_scores)


def generate_score_report(all_scores: List[Dict],
                         category_scores: Dict[str, List[Dict]],
                         output_dir: Path = None) -> str:
    """
    Generate a text summary of scores (for logging/debugging).
    
    This is a simplified report. The full report goes in Summary_Report.docx.
    
    Args:
        all_scores: List of all score dicts
        category_scores: Dict of category scores
        output_dir: Optional output directory
    
    Returns:
        Report text
    """
    lines = []
    lines.append("=" * 80)
    lines.append("LOUISIANA QSO PARTY - SCORING SUMMARY")
    lines.append("=" * 80)
    lines.append("")
    
    # Overall standings
    lines.append("OVERALL STANDINGS (Top 10):")
    lines.append("-" * 80)
    for i, score in enumerate(all_scores[:10], 1):
        lines.append(
            f"{i:3d}. {score['callsign']:10s} "
            f"{score['final_score']:8,d} pts  "
            f"({score['category']})"
        )
    lines.append("")
    
    # Category summaries
    lines.append(f"CATEGORIES WITH ACTIVITY: {len(category_scores)}")
    lines.append("")
    
    for category in sorted(category_scores.keys()):
        logs = category_scores[category]
        lines.append(f"{category}: {len(logs)} logs")
    
    lines.append("")
    lines.append("=" * 80)
    
    return '\n'.join(lines)


if __name__ == "__main__":
    print("LAQP Scoring Module")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
