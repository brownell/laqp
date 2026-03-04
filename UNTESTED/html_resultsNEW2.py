#!/usr/bin/env python3
"""
Louisiana QSO Party - HTML Results Generator

Generates individual HTML result files for each contestant in batch processing.
Uses the same styling as the web upload page but as static HTML files.
"""

from pathlib import Path
from typing import Dict


def generate_html_result(result: Dict, output_dir: Path, year: str = '2026') -> Path:
    """
    Generate an HTML results file for a single contestant.
    
    Args:
        result: Result dictionary from processor
        output_dir: Base directory to write HTML files (e.g., 'HTML_RESULTS')
        year: Contest year (creates subdirectory)
    
    Returns:
        Path to the generated HTML file
    """
    # Create output directory with year subdirectory
    output_dir = Path(output_dir) / year
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from callsign
    callsign = result.get('callsign', 'UNKNOWN').replace('/', '_')
    html_file = output_dir / f"{callsign}_results.html"
    
    # Generate HTML content
    html_content = _generate_html_content(result)
    
    # Write to file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file


def _generate_html_content(result: Dict) -> str:
    """Generate the complete HTML document"""
    
    # Convert sets to sorted lists for display
    parishes_worked = sorted(list(result.get('parishes_worked', set())))
    states_worked = sorted(list(result.get('states_worked', set())))
    provinces_worked = sorted(list(result.get('provinces_worked', set())))
    dx_worked = sorted(list(result.get('dx_worked', set())))
    parishes_activated = sorted(list(result.get('parishes_activated', set())))
    bands_worked = result.get('bands_worked', [])
    
    # Format multipliers by band/mode
    multipliers_by_band_mode = result.get('multipliers_by_band_mode', {})
    mult_html = _format_multipliers_by_band_mode(multipliers_by_band_mode)
    
    # Generate QSO tables
    qsos_by_band_html = _format_qsos_by_band(result.get('qsos_by_band', {}))
    qsos_by_mode_html = _format_qsos_by_mode(result.get('qsos_by_mode', {}))
    qsos_by_hour_html = _format_qsos_by_hour(result.get('qsos_by_hour', {}))
    
    # Build the HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Louisiana QSO Party Results - {result.get('callsign', 'N/A')}</title>
    <style>
{_get_css_content()}
    </style>
</head>
<body>
    <div class="container">
        <header class="banner">
            <h1>Jefferson Amateur Radio Club</h1>
            <h2>Louisiana QSO Party - Contest Results</h2>
        </header>

        <div class="separator"></div>

        <main>
            <section class="results-section">
                <div class="results-header">
                    <h3>Log Processing Results</h3>
                    <button type="button" class="btn-print" onclick="window.print()">
                        🖨️ Print Results
                    </button>
                </div>

                <div class="results-content">
                    
                    <!-- Station Information -->
                    <div class="result-group">
                        <h4>Station Information</h4>
                        <div class="result-item">
                            <div class="result-label">Callsign:</div>
                            <div class="result-value highlight">{result.get('callsign', 'N/A')}</div>
                        </div>
                        {_format_if_present('Operator Name', result.get('name'))}
                        <div class="result-item">
                            <div class="result-label">Category:</div>
                            <div class="result-value">{result.get('category', 'N/A')}</div>
                        </div>
                        {_format_if_present('Overlay', result.get('overlay'))}
                        <div class="result-item">
                            <div class="result-label">Location Type:</div>
                            <div class="result-value">{result.get('location_type', 'N/A')}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">Mode Category:</div>
                            <div class="result-value">{result.get('mode_category', 'N/A')}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">Power Level:</div>
                            <div class="result-value">{result.get('power_level', 'N/A')}</div>
                        </div>
                    </div>

                    <!-- Score Summary -->
                    <div class="result-group">
                        <h4>Score Summary</h4>
                        <div class="result-item">
                            <div class="result-label">Final Score:</div>
                            <div class="result-value highlight">{result.get('final_score', 0):,}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">QSO Points:</div>
                            <div class="result-value">{result.get('qso_points', 0):,}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">Total Multipliers:</div>
                            <div class="result-value">{result.get('total_multipliers', 0)}</div>
                        </div>
                        {_format_if_present('Claimed Score', result.get('claimed_score'), format_number=True)}
                    </div>

                    <!-- QSO Statistics -->
                    <div class="result-group">
                        <h4>QSO Statistics</h4>
                        <div class="result-item">
                            <div class="result-label">Total QSOs:</div>
                            <div class="result-value">{result.get('total_qsos', 0)}</div>
                        </div>
                        <div class="result-item">
                            <div class="result-label">Valid QSOs:</div>
                            <div class="result-value">{result.get('valid_qsos', 0)}</div>
                        </div>
                    </div>

                    <!-- QSOs by Band -->
                    {qsos_by_band_html}

                    <!-- QSOs by Mode -->
                    {qsos_by_mode_html}

                    <!-- QSOs by Hour -->
                    {qsos_by_hour_html}

                    <!-- Multipliers -->
                    <div class="result-group">
                        <h4>Multipliers</h4>
                        
                        {_format_multiplier_section('Parishes Worked', parishes_worked, result.get('parishes_worked_multiplier', 0))}
                        {_format_multiplier_section('States Worked', states_worked, result.get('states_worked_multiplier', 0))}
                        {_format_multiplier_section('Provinces Worked', provinces_worked, result.get('provinces_multiplier', 0))}
                        {_format_multiplier_section('DX Worked', dx_worked, result.get('dx_worked_multiplier', 0))}
                    </div>

                    <!-- Multipliers by Band/Mode -->
                    {mult_html}

                    <!-- Bonuses -->
                    {_format_bonuses_section(result, parishes_activated)}

                    <!-- Bands Worked -->
                    {_format_bands_worked_section(bands_worked)}

                </div>
            </section>
        </main>

        <footer>
            <p>&copy; 2026 Jefferson Amateur Radio Club | Louisiana QSO Party</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html


def _get_css_content() -> str:
    """Return the CSS styling (same as upload.css but embedded)"""
    return """/* Louisiana QSO Party Results - Embedded CSS */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Georgia, 'Times New Roman', serif;
    background-color: #f5f5dc;
    color: #333;
    line-height: 1.6;
    padding: 20px;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    background: #fff;
    padding: 30px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    border-radius: 5px;
}

.banner {
    text-align: center;
    margin-bottom: 20px;
}

.banner h1 {
    font-size: 2.5rem;
    color: #8B0000;
    margin-bottom: 5px;
}

.banner h2 {
    font-size: 1.8rem;
    color: #333;
    font-weight: normal;
}

.separator {
    height: 3px;
    background: linear-gradient(to right, #8B0000 0%, #8B0000 30%, transparent 30%, transparent 35%, #8B0000 35%, #8B0000 65%, transparent 65%, transparent 70%, #8B0000 70%, #8B0000 100%);
    margin: 30px 0;
}

h3 {
    font-size: 1.5rem;
    color: #8B0000;
    margin-bottom: 15px;
}

.results-section {
    margin-top: 20px;
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.btn-print {
    background: #0066cc;
    color: #fff;
    padding: 10px 20px;
    font-size: 0.95rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.btn-print:hover {
    background: #0052a3;
}

.results-content {
    background: #f9f9f9;
    padding: 25px;
    border-radius: 8px;
    border: 1px solid #ddd;
}

.result-group {
    margin-bottom: 30px;
}

.result-group h4 {
    color: #8B0000;
    font-size: 1.3rem;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 2px solid #8B0000;
}

.result-item {
    display: grid;
    grid-template-columns: 250px 1fr;
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
}

.result-item:last-child {
    border-bottom: none;
}

.result-label {
    font-weight: bold;
    color: #333;
}

.result-value {
    color: #555;
}

.result-value.highlight {
    color: #8B0000;
    font-weight: bold;
    font-size: 1.1rem;
}

.result-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 5px;
}

.result-list-item {
    background: #fff;
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid #ddd;
    font-family: 'Courier New', monospace;
}

.result-table {
    width: 100%;
    margin-top: 10px;
    border-collapse: collapse;
}

.result-table th,
.result-table td {
    padding: 8px 12px;
    text-align: left;
    border: 1px solid #ddd;
}

.result-table th {
    background: #8B0000;
    color: #fff;
    font-weight: bold;
}

.result-table tr:nth-child(even) {
    background: #f5f5f5;
}

.result-table td:last-child {
    text-align: right;
    font-family: 'Courier New', monospace;
}

.multipliers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 10px;
}

.multiplier-card {
    background: #fff;
    padding: 12px;
    border-radius: 4px;
    border: 1px solid #ddd;
}

.multiplier-card h5 {
    color: #8B0000;
    margin-bottom: 8px;
    font-size: 1rem;
}

.multiplier-list {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #555;
}

footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 2px solid #ddd;
    text-align: center;
    color: #666;
    font-size: 0.9rem;
}

@media print {
    body {
        background: #fff;
        padding: 0;
    }

    .container {
        box-shadow: none;
        padding: 20px;
    }

    .btn-print {
        display: none !important;
    }

    .result-table {
        page-break-inside: avoid;
    }
}

@media (max-width: 768px) {
    .container {
        padding: 20px;
    }

    .banner h1 {
        font-size: 2rem;
    }

    .banner h2 {
        font-size: 1.5rem;
    }

    .result-item {
        grid-template-columns: 1fr;
        gap: 5px;
    }

    .results-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .btn-print {
        width: 100%;
    }

    .multipliers-grid {
        grid-template-columns: 1fr;
    }
}"""


def _format_if_present(label: str, value, format_number: bool = False) -> str:
    """Format a result item only if the value is present"""
    if not value or value == 'N/A':
        return ''
    
    if format_number and isinstance(value, (int, float)):
        value = f"{value:,}"
    
    return f"""<div class="result-item">
            <div class="result-label">{label}:</div>
            <div class="result-value">{value}</div>
        </div>"""


def _format_multiplier_section(title: str, items: list, count: int) -> str:
    """Format a multiplier section with list of items"""
    if not items:
        return ''
    
    items_html = ''.join(f'<span class="result-list-item">{item}</span>' for item in items)
    
    return f"""<div class="result-item">
            <div class="result-label">{title}:</div>
            <div class="result-value">{count}</div>
        </div>
        <div class="result-list">
            {items_html}
        </div>"""


def _format_qsos_by_band(qsos_by_band: Dict) -> str:
    """Format QSOs by band as a table"""
    # Filter out bands with 0 QSOs
    non_zero = [(band, count) for band, count in qsos_by_band.items() if count > 0]
    if not non_zero:
        return ''
    
    # Sort by band number
    band_order = ['160', '80', '40', '20', '15', '10', '6', '2']
    non_zero_sorted = sorted(non_zero, key=lambda x: band_order.index(x[0]) if x[0] in band_order else 999)
    
    rows = ''.join(f'<tr><td>{band}m</td><td>{count}</td></tr>' for band, count in non_zero_sorted)
    
    return f"""<div class="result-group">
        <h4>QSOs by Band</h4>
        <table class="result-table">
            <thead>
                <tr><th>Band</th><th>Count</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""


def _format_qsos_by_mode(qsos_by_mode: Dict) -> str:
    """Format QSOs by mode as a table"""
    non_zero = [(mode, count) for mode, count in qsos_by_mode.items() if count > 0]
    if not non_zero:
        return ''
    
    rows = ''.join(f'<tr><td>{mode}</td><td>{count}</td></tr>' for mode, count in non_zero)
    
    return f"""<div class="result-group">
        <h4>QSOs by Mode</h4>
        <table class="result-table">
            <thead>
                <tr><th>Mode</th><th>Count</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""


def _format_qsos_by_hour(qsos_by_hour: Dict) -> str:
    """Format QSOs by hour as a table"""
    non_zero = [(hour, count) for hour, count in qsos_by_hour.items() if count > 0]
    if not non_zero:
        return ''
    
    non_zero_sorted = sorted(non_zero)
    rows = ''.join(f'<tr><td>Hour {hour + 1}</td><td>{count}</td></tr>' for hour, count in non_zero_sorted)
    
    return f"""<div class="result-group">
        <h4>QSOs by Hour</h4>
        <table class="result-table">
            <thead>
                <tr><th>Hour</th><th>Count</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>"""


def _format_multipliers_by_band_mode(mult_dict: Dict) -> str:
    """Format multipliers by band/mode as a grid of cards"""
    if not mult_dict:
        return ''
    
    cards = []
    for band_mode, mults in sorted(mult_dict.items()):
        # Convert set to sorted list
        if isinstance(mults, set):
            mult_list = sorted(list(mults))
        else:
            mult_list = mults
        
        mult_text = ', '.join(str(m) for m in mult_list)
        
        cards.append(f"""<div class="multiplier-card">
                <h5>{band_mode}</h5>
                <div class="multiplier-list">{mult_text}</div>
            </div>""")
    
    cards_html = ''.join(cards)
    
    return f"""<div class="result-group">
        <h4>Multipliers by Band/Mode</h4>
        <div class="multipliers-grid">
            {cards_html}
        </div>
    </div>"""


def _format_bonuses_section(result: Dict, parishes_activated: list) -> str:
    """Format bonuses section"""
    has_bonuses = False
    bonus_items = []
    
    # N5LCC bonus
    if result.get('worked_n5lcc'):
        has_bonuses = True
        bonus_items.append(f"""<div class="result-item">
            <div class="result-label">Worked N5LCC:</div>
            <div class="result-value">Yes</div>
        </div>""")
        
        if result.get('num_n5lcc_contacts', 0) > 0:
            bonus_items.append(f"""<div class="result-item">
                <div class="result-label">N5LCC Contacts:</div>
                <div class="result-value">{result.get('num_n5lcc_contacts')}</div>
            </div>""")
    
    # Rover bonus
    if parishes_activated:
        has_bonuses = True
        items_html = ''.join(f'<span class="result-list-item">{p}</span>' for p in parishes_activated)
        bonus_items.append(f"""<div class="result-item">
            <div class="result-label">Parishes Activated (Rover):</div>
            <div class="result-value">{len(parishes_activated)}</div>
        </div>
        <div class="result-list">
            {items_html}
        </div>""")
    
    if result.get('rover_bonus_points', 0) > 0:
        has_bonuses = True
        bonus_items.append(f"""<div class="result-item">
            <div class="result-label">Rover Bonus Points:</div>
            <div class="result-value">{result.get('rover_bonus_points'):,}</div>
        </div>""")
    
    if not has_bonuses:
        return ''
    
    return f"""<div class="result-group">
        <h4>Bonuses</h4>
        {''.join(bonus_items)}
    </div>"""


def _format_bands_worked_section(bands_worked: list) -> str:
    """Format bands worked section"""
    if not bands_worked:
        return ''
    
    items_html = ''.join(f'<span class="result-list-item">{band}m</span>' for band in bands_worked)
    
    return f"""<div class="result-group">
        <h4>Bands Worked</h4>
        <div class="result-list">
            {items_html}
        </div>
    </div>"""


# Batch processing function
def generate_all_html_results(results: list, output_dir: Path = Path('HTML_RESULTS'), year: str = '2026') -> list:
    """
    Generate HTML result files for all contestants.
    
    Args:
        results: List of result dictionaries from batch processing
        output_dir: Base directory to write HTML files (default: 'HTML_RESULTS')
        year: Contest year (creates subdirectory, default: '2026')
    
    Returns:
        List of paths to generated HTML files
    """
    output_dir = Path(output_dir)
    
    html_files = []
    
    for result in results:
        try:
            html_file = generate_html_result(result, output_dir, year)
            html_files.append(html_file)
            print(f"✓ Generated: {html_file.name}")
        except Exception as e:
            callsign = result.get('callsign', 'UNKNOWN')
            print(f"✗ Failed to generate HTML for {callsign}: {e}")
    
    return html_files


if __name__ == "__main__":
    print("LAQP HTML Results Generator")
    print("This module should be imported, not run directly.")
    print()
    print("Usage:")
    print("  from html_results import generate_html_result, generate_all_html_results")
    print()
    print("  # Single result")
    print("  html_file = generate_html_result(result, Path('HTML_RESULTS'), year='2026')")
    print()
    print("  # Batch")
    print("  html_files = generate_all_html_results(results, Path('HTML_RESULTS'), year='2026')")
    print()
    print("Results will be organized as: HTML_RESULTS/2026/CALLSIGN_results.html")
