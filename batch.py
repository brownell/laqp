#!/usr/bin/env python3
"""
Louisiana QSO Party Log Upload Application
Batch Control program to process ALL the logs in the incoming directory
"""

from html_results import generate_html_result

def main():
    import os, sys
    from datetime import datetime
    from pathlib import Path
    from pprint import pprint

    # Import the unified processor
    from processor import process_batch_logs

    from config.config import (
        INCOMING_LOGS, HTML_RESULTS

    )

    # Add project to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    results = process_batch_logs(INCOMING_LOGS)
    # pprint("Batch processing complete. Results:")
    # pprint(result)

    # Generate HTML for all valid results
    for result in results:
        # if result['is_valid']:
            # Generate HTML
        html_file = generate_html_result(result, Path(HTML_RESULTS))
        print(f"✓ {result['callsign']}: {html_file.name}")

if __name__ == "__main__":
    main()