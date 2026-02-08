#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Batch Control program to process ALL the logs in the incoming directory
"""

def main():
    import os, sys
    from datetime import datetime
    from pathlib import Path

    # Import the unified processor
    from processor import process_single_log

    from config.config import (
        INCOMING_LOGS,
        LA_PARISHES_FILE,
        WVE_ABBREVS_FILE,
        DATA_OUTPUT_DIR
    )

    # Add project to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    log_files = sorted(INCOMING_LOGS.glob('*.log'))
    if log_files:

        print(f"Found {len(log_files)} log files to validate\n")

        for log_file in log_files:
            print(f"Validating {log_file.name}...", end=" ")

            log_content = f.read()
            print(f"Processing log: {log_path}")
            result = process_single_log(log_content)
            print(f"Result for {log_path}: {result}")
            print('BREEAKPOINT')
    else:



if __name__ == "__main__":
    main()