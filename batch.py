#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Batch Control program to process ALL the logs in the incoming directory
"""

def main():
    import os, sys
    from datetime import datetime
    from pathlib import Path
    from pprint import pprint

    # Import the unified processor
    from processor import process_batch_logs

    from config.config import (
        INCOMING_LOGS,

    )

    # Add project to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    result = process_batch_logs(INCOMING_LOGS)
    pprint("Batch processing complete. Results:")
    pprint(result)

if __name__ == "__main__":
    main()