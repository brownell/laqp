#!/usr/bin/env python3
"""
Louisiana QSO Party - Process All Logs Script (Updated)

Complete pipeline: Validate → Prepare → Score → Generate Reports

Updated to work with:
- New 36-category system
- Individual DOCX result files
- Summary Report DOCX generation
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import (
    INCOMING_LOGS,
    VALIDATED_LOGS,
    PREPARED_LOGS,
    PROBLEM_LOGS,
    LA_PARISHES_FILE,
    WVE_ABBREVS_FILE,
    INDIVIDUAL_RESULTS_DIR,
    DATA_OUTPUT_DIR,
    ensure_directories,
)

# Import processing modules
from laqp.core.validator import validate_single_log
from laqp.core.preparation import prepare_single_log
from laqp.core.scoring import score_all_logs, generate_score_report

# Individual results (will be available after we update __init__.py)
try:
    from laqp.core.individual_results import generate_all_individual_results
    HAS_INDIVIDUAL_RESULTS = True
except ImportError:
    print("Warning: individual_results module not yet in __init__.py")
    HAS_INDIVIDUAL_RESULTS = False


class LogProcessor:
    """Process LAQP logs through complete pipeline"""
    
    def __init__(self):
        """Initialize processor"""
        ensure_directories()
        self.stats = {
            'total_incoming': 0,
            'validated': 0,
            'validation_failed': 0,
            'prepared': 0,
            'scored': 0,
        }
    
    def process_all(self, validate_only=False):
        """
        Process all logs through the pipeline.
        
        Args:
            validate_only: If True, only run validation step
        """
        print("=" * 80)
        print("LOUISIANA QSO PARTY - LOG PROCESSING")
        print("=" * 80)
        print()
        
        # Step 1: Validation
        self.validate_logs()
        
        if validate_only:
            print("\nValidation-only mode. Stopping here.")
            return
        
        # Step 2: Preparation
        self.prepare_logs()
        
        # Step 3: Scoring
        all_scores, category_scores = self.score_logs()
        
        # Step 4: Individual Results
        if HAS_INDIVIDUAL_RESULTS:
            self.generate_individual_results(all_scores, category_scores)
        else:
            print("\nSkipping individual results (module not yet imported)")
        
        # Step 5: Summary Report
        # TODO: Will add in next step
        print("\nSummary Report generation: Coming in next step")
        
        # Final summary
        self.print_summary()
    
    def validate_logs(self):
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
                    log_file,
                    LA_PARISHES_FILE,
                    WVE_ABBREVS_FILE
                )
                
                if result.is_valid:
                    # Move to validated directory
                    dest = VALIDATED_LOGS / log_file.name
                    log_file.rename(dest)
                    self.stats['validated'] += 1
                    print("✓ VALID")
                else:
                    # Move to problems directory
                    dest = PROBLEM_LOGS / log_file.name
                    log_file.rename(dest)
                    self.stats['validation_failed'] += 1
                    print(f"✗ INVALID ({len(result.errors)} errors)")
                    
                    # Show first few errors
                    for error in result.errors[:3]:
                        print(f"    - {error}")
                    if len(result.errors) > 3:
                        print(f"    ... and {len(result.errors) - 3} more errors")
            
            except Exception as e:
                print(f"✗ ERROR: {e}")
                self.stats['validation_failed'] += 1
        
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
                
                result = prepare_single_log(
                    log_file,
                    LA_PARISHES_FILE,
                    WVE_ABBREVS_FILE,
                    output_path
                )
                
                self.stats['prepared'] += 1
                print(f"✓ Category: {result.get('category', 'Unknown')}")
            
            except Exception as e:
                print(f"✗ ERROR: {e}")
        
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
            
            return all_scores, category_scores
        
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
    
    args = parser.parse_args()
    
    processor = LogProcessor()
    processor.process_all(validate_only=args.validate_only)


if __name__ == "__main__":
    main()
