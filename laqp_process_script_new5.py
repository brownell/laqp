#!/usr/bin/env python3
"""
Louisiana QSO Party - Batch Log Processor

Main command-line script to process all contest logs through:
1. Validation
2. Preparation
3. Scoring
4. Statistics generation
5. Database storage

Usage:
    python process_all_logs.py [--validate-only] [--skip-db]
"""
import sys
import argparse
import shutil
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    INCOMING_LOGS, VALIDATED_LOGS, PREPARED_LOGS,
    PROBLEM_LOGS, PROBLEM_REPORTS,
    LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    OUTPUT_DIR, ensure_directories
)
from laqp.core.validator import validate_single_log
from laqp.core.preparation import prepare_single_log
# TODO: Import scoring, statistics modules when created
# from laqp.core.scoring import score_log
# from laqp.core.statistics import generate_statistics
from laqp.models.database import Database, Contestant


class LogProcessor:
    """Orchestrates the complete log processing pipeline"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self.db = None
        
        if use_database:
            from config.config import DATABASE_URL
            self.db = Database(DATABASE_URL)
            self.db.create_tables()
        
        # Ensure all directories exist
        ensure_directories()
        
        # Load reference data
        self.load_reference_data()
        
        # Processing statistics
        self.stats = {
            'total_logs': 0,
            'valid_logs': 0,
            'invalid_logs': 0,
            'total_qsos': 0,
            'invalid_qsos': 0
        }
    
    def load_reference_data(self):
        """Load parish and state/province lists"""
        with open(LA_PARISHES_FILE, 'r') as f:
            self.parishes = [line.strip().upper() for line in f if line.strip()]
        
        with open(WVE_ABBREVS_FILE, 'r') as f:
            self.states_provinces = [line.strip().upper() for line in f if line.strip()]
    
    def get_log_files(self, directory: Path) -> List[Path]:
        """Get all log files from directory"""
        log_files = []
        for ext in ['*.log', '*.LOG', '*.txt', '*.TXT', '*.cbr', '*.CBR']:
            log_files.extend(directory.glob(ext))
        return sorted(log_files)
    
    def validate_logs(self) -> List[Path]:
        """
        Validate all logs in incoming directory.
        Move valid logs to validated directory, invalid to problems.
        
        Returns list of valid log paths.
        """
        print("\n" + "=" * 60)
        print("STEP 1: VALIDATION")
        print("=" * 60)
        
        incoming_logs = self.get_log_files(INCOMING_LOGS)
        
        if not incoming_logs:
            print(f"No logs found in {INCOMING_LOGS}")
            return []
        
        print(f"Found {len(incoming_logs)} log files to validate\n")
        
        valid_logs = []
        
        for log_path in incoming_logs:
            print(f"Validating {log_path.name}...", end=" ")
            
            # Validate the log
            result = validate_single_log(
                log_path,
                LA_PARISHES_FILE,
                WVE_ABBREVS_FILE
            )
            # Validate the log
            result = validate_single_log(
                log_path,
                LA_PARISHES_FILE,
                WVE_ABBREVS_FILE
            )
            
            self.stats['total_logs'] += 1
            self.stats['total_qsos'] += result.qso_count
            self.stats['invalid_qsos'] += result.invalid_qso_count
            
            if result.is_valid:
                print("✓ VALID")
                self.stats['valid_logs'] += 1
                
                # Move to validated directory
                dest = VALIDATED_LOGS / log_path.name
                shutil.move(str(log_path), str(dest))
                valid_logs.append(dest)
            else:
                print("✗ INVALID")
                self.stats['invalid_logs'] += 1
                
                # Move to problems directory
                dest = PROBLEM_LOGS / log_path.name
                shutil.move(str(log_path), str(dest))
                
                # Write error report to problems/reports directory
                report_path = PROBLEM_REPORTS / f"{log_path.stem}-errors.txt"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(result.to_report()))
                
                print(f"  Error report: {report_path}")
        
        print(f"\nValidation complete: {self.stats['valid_logs']} valid, {self.stats['invalid_logs']} invalid")
        
        return valid_logs
    
    def prepare_logs(self, validated_logs: List[Path]) -> List[Path]:
        """
        Prepare validated logs for scoring.
        
        Preparation includes:
        - Convert frequency to band
        - Remove slashes from callsigns
        - Split multi-parish QSOs into separate lines
        - Mark DX QTH indicators
        - Determine contest category
        
        Returns list of prepared log paths.
        """
        print("\n" + "=" * 60)
        print("STEP 2: PREPARATION")
        print("=" * 60)
        
        if not validated_logs:
            print("No validated logs to prepare")
            return []
        
        print(f"Preparing {len(validated_logs)} validated logs\n")
        
        prepared_logs = []
        
        for log_path in validated_logs:
            print(f"Preparing {log_path.name}...", end=" ")
            
            # Prepare the log
            output_path = PREPARED_LOGS / f"{log_path.stem}-prep.log"
            
            try:
                category_info = prepare_single_log(
                    log_path,
                    output_path,
                    LA_PARISHES_FILE,
                    WVE_ABBREVS_FILE
                )
                
                print(f"✓ {category_info['category_name']}")
                prepared_logs.append(output_path)
                
            except Exception as e:
                print(f"✗ ERROR: {e}")
                continue
        
        print(f"\nPreparation complete: {len(prepared_logs)} logs prepared")
        
        return prepared_logs
    
    def score_logs(self, prepared_logs: List[Path]):
        """
        Score all prepared logs.
        
        Calculates:
        - QSO points (2 for phone, 4 for CW/digital)
        - Multipliers (parishes per band/mode for Non-LA, parishes + states + provinces + DXCC for LA)
        - Bonuses (N5LCC, rover parish activation)
        - Final scores
        """
        print("\n" + "=" * 60)
        print("STEP 3: SCORING")
        print("=" * 60)
        print("TODO: Implement scoring module")
        print("This will adapt scoring.py for LA rules\n")
        
        # Placeholder
        print(f"Would score {len(prepared_logs)} logs")
    
    def generate_statistics(self, prepared_logs: List[Path]):
        """
        Generate contest statistics.
        
        Statistics include:
        - Logs by category
        - QSOs by band/mode
        - Parish activity
        - Hourly QSO distribution
        """
        print("\n" + "=" * 60)
        print("STEP 4: STATISTICS")
        print("=" * 60)
        print("TODO: Implement statistics module")
        print("This will adapt statistics.py for LA rules\n")
        
        # Placeholder
        print(f"Would generate statistics from {len(prepared_logs)} logs")
    
    def store_to_database(self):
        """
        Store processed data to database.
        """
        if not self.use_database:
            print("\nDatabase storage skipped (--skip-db)")
            return
        
        print("\n" + "=" * 60)
        print("STEP 5: DATABASE STORAGE")
        print("=" * 60)
        print("TODO: Implement database storage")
        print("This will populate the database from scored logs\n")
    
    def print_summary(self):
        """Print processing summary"""
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Total logs processed: {self.stats['total_logs']}")
        print(f"Valid logs: {self.stats['valid_logs']}")
        print(f"Invalid logs: {self.stats['invalid_logs']}")
        print(f"Total QSOs: {self.stats['total_qsos']}")
        print(f"Invalid QSOs: {self.stats['invalid_qsos']}")
        print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Louisiana QSO Party Log Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all logs (validate, prepare, score, statistics, database)
  python process_all_logs.py
  
  # Only validate logs
  python process_all_logs.py --validate-only
  
  # Process logs but skip database storage
  python process_all_logs.py --skip-db
        """
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate logs, do not prepare or score'
    )
    
    parser.add_argument(
        '--skip-db',
        action='store_true',
        help='Skip database storage'
    )
    
    args = parser.parse_args()
    
    # Create processor
    processor = LogProcessor(use_database=not args.skip_db)
    
    try:
        # Step 1: Validate
        valid_logs = processor.validate_logs()
        
        if not valid_logs:
            print("\nNo valid logs to process. Exiting.")
            return
        
        if args.validate_only:
            print("\nValidation complete (--validate-only specified)")
            processor.print_summary()
            return
        
        # Step 2: Prepare
        prepared_logs = processor.prepare_logs(valid_logs)
        
        # Step 3: Score
        processor.score_logs(prepared_logs)
        
        # Step 4: Statistics
        processor.generate_statistics(prepared_logs)
        
        # Step 5: Database
        processor.store_to_database()
        
        # Summary
        processor.print_summary()
        
        print("\nProcessing complete!")
        print(f"Results in: {OUTPUT_DIR}")
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
