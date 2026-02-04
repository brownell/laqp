"""
Louisiana QSO Party Statistics Module

Generates overall contest statistics from all logs:
- Logs received by category
- QSO counts by band/mode
- Parish activity
- Participation statistics

Adapted from TQP statistics.py for LA rules created by Charles Sanders, NO5W

"""
import sys
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.config import (
    LA_PARISHES_FILE, WVE_ABBREVS_FILE
)


class ParishActivity:
    """Track activity for a single parish"""
    def __init__(self, name: str):
        self.name = name
        self.sent_qsos = 0  # QSOs sent from this parish
        self.rcvd_qsos = 0  # QSOs received with this parish
        
    def __repr__(self):
        return f"Parish({self.name}, sent={self.sent_qsos}, rcvd={self.rcvd_qsos})"


class StatisticsGenerator:
    """Generates contest statistics from all logs"""
    
    def __init__(self, parish_file: Path):
        # Load parishes
        with open(parish_file, 'r') as f:
            parish_names = [line.strip().upper() for line in f if line.strip()]
        
        # Create parish tracking
        self.parishes = {name: ParishActivity(name) for name in parish_names}
    
    def is_la_parish(self, qth: str) -> bool:
        """Check if QTH is LA parish"""
        return qth in self.parishes
    
    def generate_statistics(self, log_paths: List[Path]) -> Dict:
        """
        Generate contest statistics from all prepared logs.
        
        Returns dictionary with statistics.
        """
        stats = {
            # Overall counts
            'total_logs': 0,
            'dx_logs': 0,
            'non_la_logs': 0,
            'la_fixed_logs': 0,
            'la_rover_logs': 0,
            
            # Category breakdown
            'category_counts': defaultdict(int),
            
            # QSO counts by mode
            'total_qsos': 0,
            'cw_qsos': 0,
            'phone_qsos': 0,
            'digital_qsos': 0,
            
            # QSO counts by band
            'qsos_160m': 0,
            'qsos_80m': 0,
            'qsos_40m': 0,
            'qsos_20m': 0,
            'qsos_15m': 0,
            'qsos_10m': 0,
            'qsos_6m': 0,
            'qsos_2m': 0,
            
            # Parish activity
            'parishes_with_activity': 0,
            'parishes_sent_from': 0,
            'parishes_worked': 0,
        }
        
        # Process each log
        for log_path in log_paths:
            with open(log_path, 'r', encoding='utf-8') as f:
                current_category = ""
                
                for line in f:
                    line = line.strip().upper()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    tag = parts[0]
                    
                    # Track categories
                    if tag == "LAQP-CATEGORY:":
                        current_category = ' '.join(parts[1:])
                        stats['category_counts'][current_category] += 1
                        stats['total_logs'] += 1
                        
                        # Categorize by location
                        if "DX" in current_category:
                            stats['dx_logs'] += 1
                        elif "NON-LA" in current_category:
                            stats['non_la_logs'] += 1
                        elif "LA ROVER" in current_category:
                            stats['la_rover_logs'] += 1
                        elif "LA" in current_category:
                            stats['la_fixed_logs'] += 1
                    
                    # Count QSOs
                    elif tag == "QSO:":
                        if len(parts) < 11:
                            continue
                        
                        band = parts[1]
                        mode = parts[2]
                        sent_qth = parts[7]
                        rcvd_qth = parts[10]
                        
                        stats['total_qsos'] += 1
                        
                        # Count by mode
                        if mode == "CW":
                            stats['cw_qsos'] += 1
                        elif mode in ("PH", "FM"):
                            stats['phone_qsos'] += 1
                        elif mode in ("DG", "RY"):
                            stats['digital_qsos'] += 1
                        
                        # Count by band
                        band_key = f'qsos_{band}m'
                        if band_key in stats:
                            stats[band_key] += 1
                        
                        # Track parish activity
                        if self.is_la_parish(sent_qth):
                            self.parishes[sent_qth].sent_qsos += 1
                        
                        if self.is_la_parish(rcvd_qth):
                            self.parishes[rcvd_qth].rcvd_qsos += 1
        
        # Calculate parish statistics
        for parish in self.parishes.values():
            if parish.sent_qsos > 0 or parish.rcvd_qsos > 0:
                stats['parishes_with_activity'] += 1
            if parish.sent_qsos > 0:
                stats['parishes_sent_from'] += 1
            if parish.rcvd_qsos > 0:
                stats['parishes_worked'] += 1
        
        return stats, self.parishes


def generate_statistics_report(stats: Dict, parishes: Dict[str, ParishActivity]) -> List[str]:
    """Generate a text report from statistics"""
    report = []
    report.append("=" * 60)
    report.append("LOUISIANA QSO PARTY - CONTEST STATISTICS")
    report.append("=" * 60)
    report.append("")
    
    # Overall participation
    report.append("PARTICIPATION SUMMARY")
    report.append("-" * 60)
    report.append(f"Total logs received: {stats['total_logs']}")
    report.append(f"  DX logs: {stats['dx_logs']}")
    report.append(f"  Non-LA (US/VE) logs: {stats['non_la_logs']}")
    report.append(f"  LA Fixed logs: {stats['la_fixed_logs']}")
    report.append(f"  LA Rover logs: {stats['la_rover_logs']}")
    report.append("")
    
    # Category breakdown
    report.append("LOGS BY CATEGORY")
    report.append("-" * 60)
    for category in sorted(stats['category_counts'].keys()):
        count = stats['category_counts'][category]
        report.append(f"  {category}: {count}")
    report.append("")
    
    # QSO statistics
    report.append("QSO STATISTICS")
    report.append("-" * 60)
    report.append(f"Total QSOs: {stats['total_qsos']}")
    report.append("")
    report.append("QSOs by Mode:")
    report.append(f"  CW: {stats['cw_qsos']}")
    report.append(f"  Phone: {stats['phone_qsos']}")
    report.append(f"  Digital: {stats['digital_qsos']}")
    report.append("")
    report.append("QSOs by Band:")
    for band in [160, 80, 40, 20, 15, 10, 6, 2]:
        count = stats[f'qsos_{band}m']
        if count > 0:
            report.append(f"  {band}m: {count}")
    report.append("")
    
    # Parish activity
    report.append("PARISH ACTIVITY")
    report.append("-" * 60)
    report.append(f"Parishes with any activity: {stats['parishes_with_activity']}")
    report.append(f"Parishes operated from: {stats['parishes_sent_from']}")
    report.append(f"Parishes worked: {stats['parishes_worked']}")
    report.append("")
    
    # Most active parishes
    report.append("MOST ACTIVE PARISHES (Sent From)")
    report.append("-" * 60)
    active_sent = [(p.name, p.sent_qsos) for p in parishes.values() if p.sent_qsos > 0]
    active_sent.sort(key=lambda x: x[1], reverse=True)
    for name, count in active_sent[:20]:  # Top 20
        report.append(f"  {name}: {count} QSOs")
    report.append("")
    
    # Most worked parishes
    report.append("MOST WORKED PARISHES (Received)")
    report.append("-" * 60)
    active_rcvd = [(p.name, p.rcvd_qsos) for p in parishes.values() if p.rcvd_qsos > 0]
    active_rcvd.sort(key=lambda x: x[1], reverse=True)
    for name, count in active_rcvd[:20]:  # Top 20
        report.append(f"  {name}: {count} QSOs")
    report.append("")
    
    # Inactive parishes
    inactive = [p.name for p in parishes.values() if p.sent_qsos == 0 and p.rcvd_qsos == 0]
    if inactive:
        report.append("INACTIVE PARISHES (No Activity)")
        report.append("-" * 60)
        report.append(f"Total: {len(inactive)}")
        report.append(f"Parishes: {', '.join(sorted(inactive))}")
        report.append("")
    
    report.append("=" * 60)
    report.append("END OF STATISTICS REPORT")
    report.append("=" * 60)
    
    return report


def generate_parish_detail_csv(parishes: Dict[str, ParishActivity]) -> List[str]:
    """Generate CSV with parish details"""
    lines = []
    lines.append("Parish,QSOs_Sent,QSOs_Received,Total_Activity")
    
    for parish in sorted(parishes.values(), key=lambda p: p.name):
        total = parish.sent_qsos + parish.rcvd_qsos
        lines.append(f"{parish.name},{parish.sent_qsos},{parish.rcvd_qsos},{total}")
    
    return lines


def generate_statistics_from_logs(log_paths: List[Path], parish_file: Path, output_dir: Path):
    """
    Generate statistics from prepared logs and write reports.
    
    Args:
        log_paths: List of prepared log file paths
        parish_file: Path to parish abbreviations file
        output_dir: Directory to write statistics reports
    """
    generator = StatisticsGenerator(parish_file)
    stats, parishes = generator.generate_statistics(log_paths)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write text report
    report_path = output_dir / "contest_statistics.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(generate_statistics_report(stats, parishes)))
    
    # Write parish CSV
    csv_path = output_dir / "parish_activity.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(generate_parish_detail_csv(parishes)))
    
    return stats, parishes


if __name__ == "__main__":
    print("LAQP Statistics Module")
    print("This module should be imported, not run directly.")
    print("Use scripts/process_all_logs.py for batch processing.")
