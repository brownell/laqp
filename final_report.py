# In your report generation script
from leaderboards import generate_leaderboards, generate_html_table, print_final_report
from config.config import LEADERBOARDS, FINAL_REPORT_TXT, CONTEST_YEAR

# Generate leaderboards
sections = generate_leaderboards(CONTEST_YEAR, LEADERBOARDS)


# print Final Report on ternminal
print_final_report(sections)

# Create HTML report
report = f"""
<h1>Louisiana QSO Party {CONTEST_YEAR} - Final Results</h1>
<div class="intro">
{FINAL_REPORT_TXT}
</div>
"""
# Add all sections
for section in sections:
    report += f"<h2>{section['section_title']}</h2>"
    for table in section['tables']:
        report += generate_html_table(table)

# Save report as HTML file
with open(f'final_report_{CONTEST_YEAR}.html', 'w') as f:
    f.write(report)