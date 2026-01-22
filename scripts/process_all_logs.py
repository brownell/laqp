#!/usr/bin/env python3
"""
Louisiana QSO Party - Process All Logs Script (Updated v2)

Complete pipeline: Validate → Prepare → Score → Generate Reports

Updated to:
- Clear validated/prepared directories before starting
- Better error handling
- Work with new 36-category system
"""
import sys
import shutil
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    INCOMING_LOGS,
    VALIDATED_LOGS,
    PREPARED_LOGS,
    PROBLEMS_LOGS,
    LA_PARISHES_FILE,
    WVE_ABBREVS_FILE,
    INDIVIDUAL_RESULTS_DIR,
    DATA_OUTPUT_DIR,
    ensure_initial_directories,
)

# Import processing modules
from laqp.core.validator import validate_single_log
from laqp.core.preparation import prepare_single_log
from laqp.core.scoring import score_all_logs, generate_score_report

# Individual results
try:
    from laqp.core.individual_results import generate_all_individual_results
    HAS_INDIVIDUAL_RESULTS = True
except ImportError:
    print("Warning: individual_results module not yet in __init__.py")
    HAS_INDIVIDUAL_RESULTS = False

# Summary report
try:
    from laqp.core.summary_report import generate_summary_report
    HAS_SUMMARY_REPORT = True
except ImportError:
    print("Warning: summary_report module not yet in __init__.py")
    HAS_SUMMARY_REPORT = False


class LogProcessor:
    """Process LAQP logs through complete pipeline"""
    
    def __init__(self, upload=False, clean_start=True):
        """
        Initialize processor
        
        Args:
            clean_start: If True, clear validated/prepared directories before starting
        """
        ensure_initial_directories()
        self.clean_start = clean_start
        self.upload = upload
        self.stats = {
            'total_incoming': 0,
            'validated': 0,
            'validation_failed': 0,
            'prepared': 0,
            'scored': 0,
        }
    
    def process_all(self, upload=False, validate_only=False):
        """
        Process all logs through the pipeline.
        
        Args:
            validate_only: If True, only run validation step
        """
        print("=" * 80)
        print("LOUISIANA QSO PARTY - LOG PROCESSING")
        print("=" * 80)
        print()
        
        # Clean directories if requested
        if self.clean_start:
            self.clean_directories()
        
        # Step 1: Validation
        self.validate_logs(False) # False means not uploaded with form data
        
        if validate_only:
            print("\nValidation-only mode. Stopping here.")
            return
        
        # Step 2: Preparation
        self.prepare_logs()
        
        # Step 3: Scoring
        # all_scores, category_scores 
        score_logs_result = self.score_logs()
        all_scores = score_logs_result[0]
        category_scores = score_logs_result[1]
        
        # Step 4: Individual Results
        if HAS_INDIVIDUAL_RESULTS:
            self.generate_individual_results(all_scores, category_scores)
        else:
            print("\nSkipping individual results (module not yet imported)")
        
        # Step 5: Summary Report
        if HAS_SUMMARY_REPORT:
            self.generate_summary_report(all_scores, category_scores)
        else:
            print("\nSkipping summary report (module not yet imported)")
        
        # Final summary
        self.print_summary()
    
    def clean_directories(self):
        """Clean validated and prepared directories before starting"""
        print("Cleaning validated and prepared directories...")
        
        # Clear validated logs
        if VALIDATED_LOGS.exists():
            for file in VALIDATED_LOGS.glob('*.log'):
                file.unlink()
            print(f"  Cleared {VALIDATED_LOGS}")
        
        # Clear prepared logs
        if PREPARED_LOGS.exists():
            for file in PREPARED_LOGS.glob('*.log'):
                file.unlink()
            print(f"  Cleared {PREPARED_LOGS}")
        
        print()
    
    def validate_logs(self, upload=False):
        """Step 1: Validate incoming logs"""
        print("=" * 80)
        print("STEP 1: VALIDATION")
        print("=" * 80)
        
        log_files = sorted(INCOMING_LOGS.glob('*.log'))
        self.stats['total_incoming'] = len(log_files)
        
        if not log_files:
            print("No logs found in incoming directory")
            return
        
        print(f"Found {len(log_files)} log files to validate\n")
        
        for log_file in log_files:
            print(f"Validating {log_file.name}...", end=" ")
            
            try:
                result = validate_single_log(
                    upload,
                    log_file,
                    LA_PARISHES_FILE,
                    WVE_ABBREVS_FILE
                )
                
                if result.is_valid:
                    # Move to validated directory
                    dest = VALIDATED_LOGS / log_file.name
                    shutil.copy2(log_file, dest)  # Copy instead of move to preserve original
                    self.stats['validated'] += 1
                    print("✓ VALID")
                else:
                    # Copy to problems directory with error report
                    dest = PROBLEMS_LOGS / log_file.name
                    shutil.copy2(log_file, dest)
                    
                    # Write error report
                    error_file = PROBLEMS_LOGS / f"{log_file.stem}_errors.txt"
                    with open(error_file, 'w') as f:
                        f.write(f"Validation errors for {log_file.name}\n")
                        f.write("=" * 60 + "\n\n")
                        for error in result.errors:
                            f.write(f"- {error}\n")
                    
                    self.stats['validation_failed'] += 1
                    print(f"✗ INVALID ({len(result.errors)} errors)")
                    
                    # Show first few errors
                    for error in result.errors[:2]:
                        print(f"    - {error}")
                    if len(result.errors) > 2:
                        print(f"    ... and {len(result.errors) - 2} more (see {error_file.name})")
            
            except Exception as e:
                print(f"✗ ERROR: {e}")
                self.stats['validation_failed'] += 1
                
                # Print traceback for debugging
                if "--debug" in sys.argv:
                    import traceback
                    traceback.print_exc()
        
        print(f"\nValidation complete: {self.stats['validated']} valid, " +
              f"{self.stats['validation_failed']} invalid\n")
    
    def prepare_logs(self):
        """Step 2: Prepare validated logs"""
        print("=" * 80)
        print("STEP 2: PREPARATION")
        print("=" * 80)
        
        log_files = sorted(VALIDATED_LOGS.glob('*.log'))
        
        if not log_files:
            print("No validated logs to prepare")
            return
        
        print(f"Found {len(log_files)} validated logs to prepare\n")
        
        for log_file in log_files:
            print(f"Preparing {log_file.name}...", end=" ")
            
            try:
                output_path = PREPARED_LOGS / log_file.name
                
                # Ensure parent directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = prepare_single_log(
                    log_file,           # input_path
                    output_path,        # output_path
                    LA_PARISHES_FILE,   # parish_file
                    WVE_ABBREVS_FILE    # state_province_file
                )
                
                self.stats['prepared'] += 1
                print(f"✓ Category: {result.get('category_name', 'Unknown')}")
            
            except Exception as e:
                print(f"✗ ERROR: {e}")
                if "--debug" in sys.argv:
                    import traceback
                    traceback.print_exc()
        
        print(f"\nPreparation complete: {self.stats['prepared']} logs prepared\n")
    
    def score_logs(self):
        """Step 3: Score prepared logs"""
        print("=" * 80)
        print("STEP 3: SCORING")
        print("=" * 80)
        
        try:
            all_scores, category_scores = score_all_logs(
                PREPARED_LOGS,
                LA_PARISHES_FILE,
                WVE_ABBREVS_FILE
            )
            
            self.stats['scored'] = len(all_scores)
            
            print()
            print(f"Scoring complete: {len(all_scores)} logs scored")
            print(f"Active categories: {len(category_scores)}")
            print()
            
            # Generate simple text report
            report = generate_score_report(all_scores, category_scores)
            print(report)
            
            return [all_scores, category_scores]
        
        except Exception as e:
            print(f"ERROR during scoring: {e}")
            import traceback
            traceback.print_exc()
            return [], {}
    
    def generate_individual_results(self, all_scores, category_scores):
        """Step 4: Generate individual DOCX files"""
        print("=" * 80)
        print("STEP 4: INDIVIDUAL RESULTS")
        print("=" * 80)
        
        if not all_scores:
            print("No scores to generate results for")
            return
        
        try:
            print(f"Generating individual DOCX files for {len(all_scores)} contestants...")
            print()
            
            files = generate_all_individual_results(
                all_scores,
                category_scores,
                INDIVIDUAL_RESULTS_DIR
            )
            
            print()
            print(f"✓ Generated {len(files)} individual result files")
            print(f"  Location: {INDIVIDUAL_RESULTS_DIR}")
            print()
        
        except Exception as e:
            print(f"ERROR generating individual results: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_summary_report(self, all_scores, category_scores):
        """Step 5: Generate Summary Report DOCX"""
        print("=" * 80)
        print("STEP 5: SUMMARY REPORT")
        print("=" * 80)
        
        if not all_scores:
            print("No scores to generate report for")
            return
        
        try:
            print("Generating Summary_Report.docx...")
            print()
            
            # Gather contest statistics
            contest_stats = self._gather_contest_stats(all_scores)
            
            # Generate report
            report_path = generate_summary_report(
                all_scores,
                category_scores,
                contest_stats,
                DATA_OUTPUT_DIR / 'Summary_Report.docx'
            )
            
            print(f"✓ Summary report generated")
            print(f"  Location: {report_path}")
            print()
        
        except Exception as e:
            print(f"ERROR generating summary report: {e}")
            import traceback
            traceback.print_exc()
    
    def _gather_contest_stats(self, all_scores):
        """Gather overall contest statistics"""
        stats = {}
        
        # Unique callsigns
        stats['unique_callsigns'] = len(set(s['callsign'] for s in all_scores))
        
        # Band activity
        band_qsos = {}
        for score in all_scores:
            for band, count in score.get('qsos_by_band', {}).items():
                band_qsos[band] = band_qsos.get(band, 0) + count
        stats['band_activity'] = band_qsos
        
        # Parishes activated
        all_parishes = set()
        for score in all_scores:
            # This would need to be tracked better in scoring
            # For now, just count from scores
            pass
        
        return stats
    
    def print_summary(self):
        """Print final summary"""
        print("=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print()
        print(f"  Incoming logs: {self.stats['total_incoming']}")
        print(f"  Validated: {self.stats['validated']}")
        print(f"  Failed validation: {self.stats['validation_failed']}")
        print(f"  Prepared: {self.stats['prepared']}")
        print(f"  Scored: {self.stats['scored']}")
        print()
        
        if self.stats['validated'] > 0:
            print(f"Output files generated:")
            print(f"  - Individual results: {INDIVIDUAL_RESULTS_DIR}")
            print(f"  - Summary report: {DATA_OUTPUT_DIR / 'Summary_Report.docx'}")
            print(f"  - Problem logs: {PROBLEMS_LOGS}")
            print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Process Louisiana QSO Party logs'
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only run validation step'
    )
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Do not clear validated/prepared directories before starting'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show full error tracebacks'
    )
    
    args = parser.parse_args()
    
    processor = LogProcessor(upload=False, clean_start=not args.no_clean)
    processor.process_all(upload=False, validate_only=args.validate_only)


if __name__ == "__main__":
    main()
