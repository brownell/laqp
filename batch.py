#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Batch Control program to process ALL the logs in the incoming directory
"""

from database import save_result
from cross_check import cross_check_all_logs
from generate_rankings import generate_rankings
from generate_final_report import generate_final_report_html

def main(contest_year: str):
    import sys
    from pathlib import Path

    # Import the unified processor
    from processor import process_batch_logs

    from config.config import BATCH_INPUT_DIR

    # Add project to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    input_dir = Path(f"{BATCH_INPUT_DIR}/{contest_year}")

    # Process all logs
    # print(f"before process_batch_logs, input_dir: {input_dir}")
    results = process_batch_logs(input_dir)

    stats = cross_check_all_logs(results)


    # Save results to database (valid and invalid)
    valid_count = 0
    invalid_count = 0
    saved_count = 0
    errors_count = 0
    
    for result in results:

        # Initialize empty rankings dict
        result['rankings'] = {}
        
        if result['is_valid']:
            valid_count += 1
        else:
            invalid_count += 1
            print(f"✗ {result['callsign']}: Invalid log")
            for error in result.get('errors', [])[:10]:  # Show first 10 errors
                print(f"    ERROR: {error}")
        
        # # Save to database (both valid and invalid for record-keeping)

        try:
            if save_result(result):
                saved_count += 1
                status = "✓" if result['is_valid'] else "✗"
                # print(f"{status} {result['callsign']}: Saved to database")
            else:
                print(f"✗ {result['callsign']}: Database save failed")
        except Exception as e:
            print(f"✗ {result['callsign']}: Database error - {e}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total processed: {len(results)}")
    print(f"Valid logs: {valid_count}")
    print(f"Invalid logs: {invalid_count}")
    print(f"Saved to database: {saved_count}")
    print()
    print("Next step: Calculate rankings and generate HTML reports")
    print()

    # generate rankings from the database results
    generate_rankings(contest_year)

    generate_final_report_html(contest_year)
    
if __name__ == "__main__":
    import os, sys
    from datetime import datetime
    from config.config import CONTEST_YEAR
    
    # Get year from environment or command line
    if len(sys.argv) > 1:
        year = sys.argv[1]
    else:
        year = CONTEST_YEAR
    main(year)
