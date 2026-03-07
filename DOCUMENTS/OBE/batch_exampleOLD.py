#!/usr/bin/env python3
"""
Louisiana QSO Party - Batch Processing Example

Example script showing how to:
1. Process multiple logs in a directory
2. Generate HTML results for each contestant
"""

import sys
from pathlib import Path
from config.config import HTML_RESULTS, INCOMING_LOGS
from processor import process_batch_logs
from html_results import generate_all_html_results
# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def process_and_generate_html(log_dir: str = INCOMING_LOGS,
                              html_dir: str = HTML_RESULTS):
    """
    Process all logs and generate HTML results.
    
    Args:
        log_dir: Directory containing log files
        html_dir: Directory for HTML output
    """
    log_dir = Path(log_dir)
    html_dir = Path(html_dir)
    
    print("=" * 60)
    print("Louisiana QSO Party - Batch Processing")
    print("=" * 60)
    print()
    
    # Step 1: Process all logs
    print("Processing logs...")
    results = process_batch_logs(INCOMING_LOGS)
    
    print(f"✓ Processed {len(results)} logs")
    print()
    
    # Step 2: Separate valid and invalid
    valid_results = [r for r in results if r['callsign']]
    invalid_results = [r for r in results if not r['callsign']]
    
    print(f"Valid logs: {len(valid_results)}")
    print(f"Invalid logs: {len(invalid_results)}")
    print()
    
    # Step 3: Show invalid logs
    if invalid_results:
        print("Invalid Logs:")
        print("-" * 60)
        for result in invalid_results:
            print(f"\n{result['callsign']}:")
            for error in result['errors']:
                print(f"  ERROR: {error}")
            for warning in result['warnings']:
                print(f"  WARNING: {warning}")
        print()
    
    # Step 4: Generate HTML for valid logs
    if valid_results:
        print("Generating HTML results...")
        html_files = generate_all_html_results(valid_results, html_dir)
        print(f"\n✓ Generated {len(html_files)} HTML files in {html_dir}/")
        print()
    
    # Step 5: Show summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if valid_results:
        # Sort by score
        sorted_results = sorted(valid_results, 
                              key=lambda x: x['final_score'], 
                              reverse=True)
        
        print(f"\n{'Rank':<6} {'Callsign':<12} {'Category':<15} {'Score':<10}")
        print("-" * 60)
        for rank, result in enumerate(sorted_results, 1):
            print(f"{rank:<6} {result['callsign']:<12} "
                  f"{result['category']:<15} {result['final_score']:>9,}")
    
    print()
    print("Done!")


if __name__ == "__main__":
    # Process logs in 'logs/incoming' and generate HTML in 'HTML_RESULTS'
    process_and_generate_html()
