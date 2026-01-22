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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import (
    PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    N5LCC_BONUS, ROVER_PARISH_BONUS,
    PHONE_MODES, CW_DIGITAL_MODES,
    LOC_DX, LOC_NON_LA, LOC_LA_FIXED, LOC_LA_ROVER,
    MODE_PHONE_ONLY, MODE_CW_DIGITAL_ONLY, MODE_MIXED,
    POWER_QRP, POWER_LOW, POWER_HIGH,
    OVERLAY_NONE, OVERLAY_WIRES, OVERLAY_TB_WIRES, OVERLAY_POTA,
    PREPARED_LOGS, INDIVIDUAL_RESULTS_DIR
)
from laqp.categories import (
    get_category_short_name, get_base_category, get_overlay_name
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
        
        Returns dict with:
            - callsign: Station callsign
            - category: Short category name (e.g., 'nl_ph_lo')
            - base_category: Base category (same as category if no overlay)
            - overlay: Overlay name ('WIRES', 'TB-WIRES', 'POTA', or None)
            - location_type: LOC_* constant
            - mode_category: MODE_* constant
            - power_level: POWER_* constant
            - final_score: Total calculated score
            - qso_points: Points from QSOs only
            - total_qsos: Total number of QSOs
            - valid_qsos: Number of valid QSOs (for scoring)
            - multipliers: Total multiplier count
            - parishes_worked: Set of parishes worked
            - states_worked: Set of states worked
            - provinces_worked: Set of provinces worked
            - dx_worked: Set of DX entities worked
            - parishes_activated: Number of parishes activated (rovers)
            - worked_n5lcc: Boolean if worked N5LCC
            - qsos_by_band: Dict of {band: count}
            - qsos_by_mode: Dict of {'Phone': count, 'CW/Digital': count}
            - bands_worked: List of bands worked
            - multipliers_by_band_mode: Detailed multiplier breakdown
        """
        # Initialize result
        result = {
            'callsign': '',
            'category': '',
            'base_category': '',
            'overlay': None,
            'location_type': LOC_NON_LA,
            'mode_category': MODE_MIXED,
            'power_level': POWER_LOW,
            'final_score': 0,
            'qso_points': 0,
            'total_qsos': 0,
            'valid_qsos': 0,
            'multipliers': 0,
            'parishes_worked': set(),
            'states_worked': set(),
            'provinces_worked': set(),
            'dx_worked': set(),
            'parishes_activated': 0,
            'worked_n5lcc': False,
            'qsos_by_band': defaultdict(int),
            'qsos_by_mode': {'Phone': 0, 'CW/Digital': 0},
            'bands_worked': [],
            'multipliers_by_band_mode': {},
        }
        
        # Parse log file
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
                
                elif tag == 'LAQP-CATEGORY:':
                    # Format: "location,mode,power,overlay"
                    # Example: "1,2,1,0" = NON_LA, MIXED, LOW, NONE
                    if len(parts) > 1:
                        cat_parts = parts[1].split(',')
                        if len(cat_parts) >= 4:
                            result['location_type'] = int(cat_parts[0])
                            result['mode_category'] = int(cat_parts[1])
                            result['power_level'] = int(cat_parts[2])
                            overlay_int = int(cat_parts[3])
                            
                            # Determine categories
                            result['category'] = get_category_short_name(
                                result['location_type'],
                                result['mode_category'],
                                result['power_level'],
                                overlay_int
                            )
                            
                            result['base_category'] = get_base_category(
                                result['location_type'],
                                result['mode_category'],
                                result['power_level']
                            )
                            
                            result['overlay'] = get_overlay_name(overlay_int)
                
                # Count QSOs and calculate points
                elif tag == 'QSO:':
                    result['total_qsos'] += 1
                    
                    if len(parts) >= 11:
                        # Parse QSO line
                        freq = int(parts[1])
                        mode = parts[2]
                        call_sent = parts[5]
                        qth_sent = parts[7]
                        call_rcvd = parts[8]
                        qth_rcvd = parts[10]
                        
                        # Determine band from frequency
                        band = self._freq_to_band(freq)
                        if band:
                            result['qsos_by_band'][band] += 1
                        
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
                        if qth_rcvd_upper in self.parishes:
                            result['parishes_worked'].add(qth_rcvd_upper)
                        elif qth_rcvd_upper in self.states_provinces:
                            # Distinguish between states and provinces
                            if qth_rcvd_upper in ['AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT']:
                                result['provinces_worked'].add(qth_rcvd_upper)
                            else:
                                result['states_worked'].add(qth_rcvd_upper)
                        else:
                            # Assume DX
                            result['dx_worked'].add(qth_rcvd_upper)
                        
                        # Check if worked N5LCC
                        if call_rcvd == 'N5LCC':
                            result['worked_n5lcc'] = True
                        
                        # Track parishes activated (for rovers)
                        if result['location_type'] == LOC_LA_ROVER:
                            qth_sent_upper = qth_sent.upper()
                            if qth_sent_upper in self.parishes:
                                # Count unique parishes in sent QTH
                                # (will be counted in final calculation)
                                pass
        
        # Calculate multipliers
        if result['location_type'] in [LOC_DX, LOC_NON_LA]:
            # Non-LA stations: parishes only, per band/mode
            # For now, simplified: total unique parishes
            result['multipliers'] = len(result['parishes_worked'])
        else:
            # LA stations: parishes + states + provinces + DX, per band/mode
            # For now, simplified: total unique entities
            result['multipliers'] = (
                len(result['parishes_worked']) +
                len(result['states_worked']) +
                len(result['provinces_worked']) +
                len(result['dx_worked'])
            )
        
        # Calculate final score
        result['final_score'] = result['qso_points'] * result['multipliers']
        
        # Add N5LCC bonus
        if result['worked_n5lcc']:
            result['final_score'] += N5LCC_BONUS
        
        # Add rover parish activation bonus
        if result['location_type'] == LOC_LA_ROVER:
            parishes_activated = len(result['parishes_worked'])  # Simplified
            result['parishes_activated'] = parishes_activated
            result['final_score'] += parishes_activated * ROVER_PARISH_BONUS
        
        # Get list of bands worked
        result['bands_worked'] = sorted(result['qsos_by_band'].keys())
        
        return result
    
    def _freq_to_band(self, freq_khz: int) -> int:
        """Convert frequency in kHz to band in meters"""
        if 1800 <= freq_khz <= 2000:
            return 160
        elif 3500 <= freq_khz <= 4000:
            return 80
        elif 7000 <= freq_khz <= 7300:
            return 40
        elif 14000 <= freq_khz <= 14350:
            return 20
        elif 21000 <= freq_khz <= 21450:
            return 15
        elif 28000 <= freq_khz <= 29700:
            return 10
        elif 50000 <= freq_khz <= 54000:
            return 6
        elif 144000 <= freq_khz <= 148000:
            return 2
        else:
            return None


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
        
        # Convert sets to counts for storage
        result['parishes_worked'] = len(result['parishes_worked'])
        result['states_worked'] = len(result['states_worked'])
        result['provinces_worked'] = len(result['provinces_worked'])
        result['dx_contacts'] = len(result['dx_worked'])
        
        # Store in all_scores
        all_scores.append(result)
        
        # Store in category
        category_scores[result['category']].append(result)
        
        # If has overlay, also store in base category with note
        if result['overlay']:
            # Make a copy for base category
            base_result = result.copy()
            category_scores[result['base_category']].append(base_result)
        
        print(f"  {result['callsign']}: {result['final_score']:,} points ({result['category']})")
    
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
