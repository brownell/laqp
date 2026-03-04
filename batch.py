#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Batch Control program to process ALL the logs in the incoming directory
"""

from database import save_result

def main():
    import os, sys
    from datetime import datetime
    from pathlib import Path

    # Import the unified processor
    from processor import process_batch_logs

    from config.config import INCOMING_LOGS

    # Add project to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    # Get year (default to current year)
    year = os.environ.get('CONTEST_YEAR', str(datetime.now().year))
    
    print("=" * 60)
    print(f"Louisiana QSO Party - Batch Processing ({year})")
    print("=" * 60)
    print()

    # Process all logs
    results = process_batch_logs(INCOMING_LOGS)
    
    print(f"Processed {len(results)} logs")
    print()

    # Save results to database (valid and invalid)
    valid_count = 0
    invalid_count = 0
    saved_count = 0
    
    for result in results:
        # Add year to result
        result['year'] = year
        
        # Initialize empty rankings dict
        result['rankings'] = {}
        
        if result['is_valid']:
            valid_count += 1
        else:
            invalid_count += 1
            print(f"✗ {result['callsign']}: Invalid log")
            for error in result.get('errors', [])[:3]:  # Show first 3 errors
                print(f"    ERROR: {error}")
        
        # Save to database (both valid and invalid for record-keeping)
        try:
            if save_result(result):
                saved_count += 1
                status = "✓" if result['is_valid'] else "✗"
                print(f"{status} {result['callsign']}: Saved to database")
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

if __name__ == "__main__":
    main()
