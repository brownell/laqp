# Louisiana QSO Party - Leaderboard Generator

## Overview

The leaderboard generator interprets a declarative configuration (LEADERBOARDS) to generate ranked tables from the database. No hard-coded queries needed!

## Configuration Format

### Structure
```python
LEADERBOARDS = [
    [section_1_config],
    [section_2_config],
    ...
]
```

### Section Format
Each section is a list where:
- **First element** = Section metadata
- **Remaining elements** = Table definitions

```python
[
    # Section metadata (first element)
    {
        'section_title': 'Section Title Here',
        'show': [
            ['db_field_name', 'Column Header'],
            ['callsign', 'CallSign'],
            ['final_score', 'Total Score'],
            ...
        ]
    },
    
    # Table definition 1
    {
        'title': 'Table Title',
        'ands': [
            ['field', 'value'],           # Simple equality
            ['field', 'operator', 'value']  # Custom operator
        ]
    },
    
    # Table definition 2
    {...},
    ...
]
```

## AND Clause Formats

### 2-Element: Simple Equality
```python
['location_type', 'LA-FIXED']
# Generates: WHERE location_type = 'LA-FIXED'
```

### 3-Element: Custom Operator
```python
['final_score', '>', 1000]
# Generates: WHERE final_score > 1000

['total_qsos', '>=', 100]
# Generates: WHERE total_qsos >= 100

['callsign', 'LIKE', 'K5%']
# Generates: WHERE callsign LIKE 'K5%'
```

### Multiple AND Clauses
```python
'ands': [
    ['location_type', 'LA-FIXED'],
    ['power_level', 'QRP'],
    ['final_score', '>', 500]
]
# Generates: WHERE location_type = 'LA-FIXED' 
#            AND power_level = 'QRP'
#            AND final_score > 500
```

## Complete Example

```python
LEADERBOARDS = [
    # Section 1: Louisiana Stations
    [
        {
            'section_title': 'Top Level Categories - Louisiana Stations',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Total Score'],
                ['overlay', 'Overlay'],
                ['mode_category', 'Mode'],
                ['worked_n5lcc', 'N5LCC']
            ]
        },
        {'title': 'LA Fixed QRP', 
         'ands': [['location_type', 'LA-FIXED'], ['power_level', 'QRP']]},
        {'title': 'LA Fixed LOW', 
         'ands': [['location_type', 'LA-FIXED'], ['power_level', 'LOW']]},
        {'title': 'LA Fixed HIGH', 
         'ands': [['location_type', 'LA-FIXED'], ['power_level', 'HIGH']]},
        {'title': 'LA Rover QRP', 
         'ands': [['location_type', 'LA-ROVER'], ['power_level', 'QRP']]},
    ],
    
    # Section 2: Non-Louisiana Stations
    [
        {
            'section_title': 'Top Level Categories - Non-Louisiana Stations',
            'show': [
                ['callsign', 'CallSign'],
                ['final_score', 'Total Score'],
                ['overlay', 'Overlay']
            ]
        },
        {'title': 'NON-LA QRP', 
         'ands': [['location_type', 'NON-LA'], ['power_level', 'QRP']]},
        {'title': 'NON-LA LOW', 
         'ands': [['location_type', 'NON-LA'], ['power_level', 'LOW']]},
    ],
    
    # Section 3: High Scorers (using 3-element AND)
    [
        {
            'section_title': 'Top Scorers',
            'show': [
                ['callsign', 'CallSign'],
                ['location_type', 'Location'],
                ['final_score', 'Score']
            ]
        },
        {'title': 'Scores Over 5000', 
         'ands': [['final_score', '>=', 5000]]},
        {'title': 'Louisiana Scores Over 3000',
         'ands': [
             ['location_type', 'LIKE', 'LA-%'],
             ['final_score', '>=', 3000]
         ]},
    ]
]
```

## Usage

### Generate Leaderboards

```python
from leaderboards import generate_leaderboards
from config.config import LEADERBOARDS

# Generate all sections and tables
sections = generate_leaderboards('2026', LEADERBOARDS)

# sections is a list of dicts:
# [
#     {
#         'section_title': 'Section Title',
#         'show_fields': [...],
#         'tables': [
#             {
#                 'title': 'Table Title',
#                 'headers': ['Rank', 'CallSign', 'Total Score', ...],
#                 'rows': [
#                     [1, 'K5ABC', 1250, ...],
#                     [2, 'W5XYZ', 980, ...],
#                     ...
#                 ]
#             },
#             ...
#         ]
#     },
#     ...
# ]
```

### Print Leaderboards (Text)

```python
for section in sections:
    print(f"\n{'='*60}")
    print(f"{section['section_title']}")
    print(f"{'='*60}\n")
    
    for table in section['tables']:
        print(f"\n{table['title']}")
        print('-' * 60)
        
        # Print headers
        print(' | '.join(f"{h:12}" for h in table['headers']))
        print('-' * 60)
        
        # Print rows
        for row in table['rows']:
            print(' | '.join(f"{str(v):12}" for v in row))
```

### Generate HTML

```python
def generate_html_table(table):
    """Convert table dict to HTML table"""
    html = f"<h3>{table['title']}</h3>\n"
    html += "<table class='leaderboard-table'>\n"
    
    # Headers
    html += "  <thead><tr>\n"
    for header in table['headers']:
        html += f"    <th>{header}</th>\n"
    html += "  </tr></thead>\n"
    
    # Rows
    html += "  <tbody>\n"
    for row in table['rows']:
        html += "  <tr>\n"
        for value in row:
            html += f"    <td>{value}</td>\n"
        html += "  </tr>\n"
    html += "  </tbody>\n"
    
    html += "</table>\n"
    return html

# Generate complete HTML report
html_parts = []
for section in sections:
    html_parts.append(f"<h2>{section['section_title']}</h2>")
    for table in section['tables']:
        html_parts.append(generate_html_table(table))

html_report = '\n'.join(html_parts)
```

## Key Features

✅ **Declarative** - Define queries in config, not code
✅ **Automatic ranking** - Rank column added to every table
✅ **Sorted by score** - Always `ORDER BY final_score DESC`
✅ **Skip empty tables** - Tables with 0 rows are excluded
✅ **Flexible conditions** - 2-element (=) or 3-element (any operator)
✅ **Clean data structure** - Easy to convert to HTML, PDF, etc.

## Example Output Structure

```python
{
    'section_title': 'Louisiana Stations',
    'show_fields': [['callsign', 'CallSign'], ...],
    'tables': [
        {
            'title': 'LA Fixed QRP',
            'headers': ['Rank', 'CallSign', 'Total Score', 'Overlay', 'Mode'],
            'rows': [
                [1, 'K5ABC', 1250, None, 'MIXED'],
                [2, 'W5XYZ', 980, 'WIRES', 'PHONE'],
                [3, 'N5TEST', 750, None, 'CW-DIGITAL']
            ]
        },
        {
            'title': 'LA Fixed LOW',
            'headers': ['Rank', 'CallSign', 'Total Score', ...],
            'rows': [...]
        }
    ]
}
```

## Advanced Examples

### Using Custom Operators

```python
# Top 10 scores
{'title': 'Top 10 Overall', 
 'ands': [['final_score', '>', 0]]},  # Get all, then limit in processing

# Callsigns starting with K5
{'title': 'K5 Callsigns',
 'ands': [['callsign', 'LIKE', 'K5%']]},

# QRP with > 100 QSOs
{'title': 'QRP > 100 QSOs',
 'ands': [
     ['power_level', 'QRP'],
     ['valid_qsos', '>', 100]
 ]},

# Not null overlay
{'title': 'Overlay Participants',
 'ands': [['overlay', 'IS NOT', 'NULL']]},
```

## Integration with Final Report

```python
# In your report generation script
from leaderboards import generate_leaderboards
from config.config import LEADERBOARDS, FINAL_REPORT_TXT

year = '2026'

# Generate leaderboards
sections = generate_leaderboards(year, LEADERBOARDS)

# Create report
report = f"""
<h1>Louisiana QSO Party {year} - Final Results</h1>
<div class="intro">
{FINAL_REPORT_TXT}
</div>
"""

# Add all sections
for section in sections:
    report += f"<h2>{section['section_title']}</h2>"
    for table in section['tables']:
        report += generate_html_table(table)

# Save report
with open(f'final_report_{year}.html', 'w') as f:
    f.write(report)
```

## Testing

```python
# Test with simple config
test_config = [
    [
        {'section_title': 'Test Section', 
         'show': [['callsign', 'Call'], ['final_score', 'Score']]},
        {'title': 'All LA Stations', 
         'ands': [['location_type', 'LIKE', 'LA-%']]},
    ]
]

sections = generate_leaderboards('2026', test_config)
print(f"Generated {len(sections)} section(s)")
for section in sections:
    print(f"  {len(section['tables'])} table(s)")
```

The leaderboard generator is completely data-driven - just update the LEADERBOARDS configuration to add new categories!
