"""
Louisiana QSO Party - Summary Report Generator

Generates Summary_Report.docx with:
- Contest header and sponsor information
- Overall standings (all logs sorted by score)
- Contest statistics
- Category sections (one per active category)

Adapted from TQP statistics.py for LA rules created by Charles Sanders, NO5W

Each category section includes:
- Category standings
- Category-specific statistics
"""
import sys
from pathlib import Path
from typing import Dict, List
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.config import (
    CONTEST_NAME, CONTEST_YEAR, SPONSOR_NAME, SPONSOR_WEBSITE,
    REPORT_TXT, DATA_OUTPUT_DIR
)
from laqp.categories import CATEGORIES


class SummaryReportGenerator:
    """Generates Summary Report DOCX for contest"""
    
    def __init__(self, contest_year: int = None):
        """
        Initialize generator.
        
        Args:
            contest_year: Contest year (defaults to config.CONTEST_YEAR)
        """
        self.contest_year = contest_year or CONTEST_YEAR
        self.contest_name = f"{CONTEST_NAME} {self.contest_year}"
    
    def generate_report(self,
                       all_scores: List[Dict],
                       category_scores: Dict[str, List[Dict]],
                       contest_stats: Dict,
                       output_path: Path = None) -> Path:
        """
        Generate the complete Summary Report.
        
        Args:
            all_scores: List of all score dicts (sorted by score)
            category_scores: Dict of {category: [score dicts]}
            contest_stats: Dict with overall contest statistics
            output_path: Output file path (defaults to DATA_OUTPUT_DIR/Summary_Report.docx)
        
        Returns:
            Path to generated file
        """
        if output_path is None:
            output_path = DATA_OUTPUT_DIR / 'Summary_Report.docx'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create document
        doc = Document()
        
        # Set default font and spacing
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        paragraph_format = style.paragraph_format
        paragraph_format.space_before = Pt(0)
        paragraph_format.space_after = Pt(6)
        paragraph_format.line_spacing = 1.0
        
        # Title page
        self._add_title_page(doc)
        
        # Introduction text
        self._add_introduction(doc)
        
        # Overall standings
        self._add_overall_standings(doc, all_scores)
        
        # Contest statistics
        self._add_contest_statistics(doc, contest_stats, all_scores)
        
        # Category sections
        self._add_category_sections(doc, category_scores, contest_stats)
        
        # Save
        doc.save(str(output_path))
        
        return output_path
    
    def _reduce_spacing(self, paragraph):
        """Reduce spacing for a paragraph"""
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(3)
        paragraph.paragraph_format.line_spacing = 1.0
    
    def _add_page_break(self, doc):
        """Add a page break"""
        doc.add_page_break()
    
    def _add_title_page(self, doc: Document):
        """Add title page"""
        # Main title
        title = doc.add_heading(self.contest_name.upper(), level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._reduce_spacing(title)
        
        # Sponsor
        sponsor = doc.add_paragraph(f'Hosted by {SPONSOR_NAME}')
        sponsor.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sponsor.runs[0].font.size = Pt(14)
        self._reduce_spacing(sponsor)
        
        # Website
        website = doc.add_paragraph(SPONSOR_WEBSITE)
        website.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._reduce_spacing(website)
        
        # Separator
        sep = doc.add_paragraph('=' * 80)
        self._reduce_spacing(sep)
    
    def _add_introduction(self, doc: Document):
        """Add introduction text from config"""
        # Add REPORT_TXT paragraphs
        for line in REPORT_TXT.strip().split('\n'):
            if line.strip():
                para = doc.add_paragraph(line.strip())
                self._reduce_spacing(para)
        
        # Separator
        sep = doc.add_paragraph('=' * 80)
        self._reduce_spacing(sep)
    
    def _add_overall_standings(self, doc: Document, all_scores: List[Dict]):
        """Add overall standings section"""
        # MAJOR HEADER
        heading = doc.add_heading('OVERALL STANDINGS - ALL CATEGORIES', level=1)
        heading.runs[0].font.size = Pt(16)
        heading.runs[0].font.bold = True
        self._reduce_spacing(heading)
        
        para = doc.add_paragraph(f'Total Logs Received: {len(all_scores)}')
        self._reduce_spacing(para)
        
        # Standings table header
        para = doc.add_paragraph()
        para.add_run('Rank  Callsign    Category                          Score        QSOs').font.bold = True
        self._reduce_spacing(para)
        
        sep = doc.add_paragraph('─' * 80)
        self._reduce_spacing(sep)
        
        # Standings
        for i, score in enumerate(all_scores, 1):
            category_full = CATEGORIES.get(score['category'], score['category'])
            para = doc.add_paragraph(
                f"{i:4d}  {score['callsign']:10s}  "
                f"{category_full:32s}  "
                f"{score['final_score']:8,d}  "
                f"{score['total_qsos']:5d}"
            )
            self._reduce_spacing(para)
        
        # Separator
        sep = doc.add_paragraph('=' * 80)
        self._reduce_spacing(sep)
    
    def _add_contest_statistics(self, doc: Document, stats: Dict, all_scores: List[Dict]):
        """Add overall contest statistics"""
        # MAJOR HEADER
        heading = doc.add_heading('LOUISIANA QSO PARTY - CONTEST STATISTICS', level=1)
        heading.runs[0].font.size = Pt(16)
        heading.runs[0].font.bold = True
        self._reduce_spacing(heading)
        
        # Overall stats
        total_qsos = sum(s['total_qsos'] for s in all_scores)
        
        para = doc.add_paragraph()
        para.add_run('Total Logs Received: ').font.bold = True
        para.add_run(str(len(all_scores)))
        self._reduce_spacing(para)
        
        para = doc.add_paragraph()
        para.add_run('Total QSOs: ').font.bold = True
        para.add_run(f"{total_qsos:,}")
        self._reduce_spacing(para)
        
        # More statistics from stats dict if available
        if 'parishes_activated' in stats:
            para = doc.add_paragraph()
            para.add_run('Parishes Activated: ').font.bold = True
            para.add_run(str(stats['parishes_activated']))
            self._reduce_spacing(para)
        
        if 'unique_callsigns' in stats:
            para = doc.add_paragraph()
            para.add_run('Unique Callsigns: ').font.bold = True
            para.add_run(str(stats['unique_callsigns']))
            self._reduce_spacing(para)
        
        # Top bands
        if 'band_activity' in stats:
            heading = doc.add_heading('QSOs by Band', level=2)
            heading.runs[0].font.size = Pt(14)
            self._reduce_spacing(heading)
            
            for band, count in sorted(stats['band_activity'].items()):
                para = doc.add_paragraph()
                para.add_run(f'  {band}m: ').font.bold = True
                para.add_run(f"{count:,}")
                self._reduce_spacing(para)
        
        # Separator
        sep = doc.add_paragraph('=' * 80)
        self._reduce_spacing(sep)
    
    def _add_category_sections(self, doc: Document, category_scores: Dict[str, List[Dict]],
                               contest_stats: Dict):
        """Add sections for each active category"""
        # Sort categories alphabetically
        for category in sorted(category_scores.keys()):
            logs = category_scores[category]
            
            if not logs:
                continue  # Skip empty categories
            
            # Page break before each category
            self._add_page_break(doc)
            
            # MAJOR HEADER - Category name
            category_full = CATEGORIES.get(category, category)
            heading = doc.add_heading(f'CATEGORY: {category_full}', level=1)
            heading.runs[0].font.size = Pt(16)
            heading.runs[0].font.bold = True
            self._reduce_spacing(heading)
            
            para = doc.add_paragraph(f'Logs in category: {len(logs)}')
            self._reduce_spacing(para)
            
            # MINOR HEADER - Standings
            subheading = doc.add_heading('Category Standings', level=2)
            subheading.runs[0].font.size = Pt(14)
            self._reduce_spacing(subheading)
            
            # Standings table header
            para = doc.add_paragraph()
            para.add_run('Rank  Callsign      Score        QSOs    Multipliers').font.bold = True
            self._reduce_spacing(para)
            
            sep = doc.add_paragraph('─' * 70)
            self._reduce_spacing(sep)
            
            # Category standings
            for i, score in enumerate(logs, 1):
                para = doc.add_paragraph(
                    f"{i:4d}  {score['callsign']:12s}  "
                    f"{score['final_score']:8,d}  "
                    f"{score['total_qsos']:6d}  "
                    f"{score['multipliers']:6d}"
                )
                self._reduce_spacing(para)
            
            # Category statistics
            self._add_category_statistics(doc, logs, category)
        
        # Final separator
        sep = doc.add_paragraph('=' * 80)
        self._reduce_spacing(sep)
    
    def _add_category_statistics(self, doc: Document, logs: List[Dict], category: str):
        """Add statistics for a specific category"""
        # MINOR HEADER
        subheading = doc.add_heading('Category Statistics', level=2)
        subheading.runs[0].font.size = Pt(14)
        self._reduce_spacing(subheading)
        
        # Calculate category stats
        total_qsos = sum(log['total_qsos'] for log in logs)
        total_points = sum(log['qso_points'] for log in logs)
        
        para = doc.add_paragraph()
        para.add_run('Total QSOs in category: ').font.bold = True
        para.add_run(f"{total_qsos:,}")
        self._reduce_spacing(para)
        
        para = doc.add_paragraph()
        para.add_run('Total Points: ').font.bold = True
        para.add_run(f"{total_points:,}")
        self._reduce_spacing(para)
        
        # Average stats
        if logs:
            avg_qsos = total_qsos / len(logs)
            avg_score = sum(log['final_score'] for log in logs) / len(logs)
            
            para = doc.add_paragraph()
            para.add_run('Average QSOs per log: ').font.bold = True
            para.add_run(f"{avg_qsos:.1f}")
            self._reduce_spacing(para)
            
            para = doc.add_paragraph()
            para.add_run('Average Score: ').font.bold = True
            para.add_run(f"{avg_score:,.0f}")
            self._reduce_spacing(para)
        
        # Band breakdown for category
        band_qsos = {}
        for log in logs:
            for band, count in log.get('qsos_by_band', {}).items():
                band_qsos[band] = band_qsos.get(band, 0) + count
        
        if band_qsos:
            subheading2 = doc.add_heading('QSOs by Band', level=3)
            subheading2.runs[0].font.size = Pt(12)
            self._reduce_spacing(subheading2)
            
            for band in sorted(band_qsos.keys(), reverse=True):
                count = band_qsos[band]
                para = doc.add_paragraph()
                para.add_run(f'  {band}m: ').font.bold = True
                para.add_run(f"{count:,}")
                self._reduce_spacing(para)


def generate_summary_report(all_scores: List[Dict],
                            category_scores: Dict[str, List[Dict]],
                            contest_stats: Dict = None,
                            output_path: Path = None) -> Path:
    """
    Generate the Summary Report DOCX file.
    
    Args:
        all_scores: List of all score dicts (sorted by score)
        category_scores: Dict of {category: [score dicts]}
        contest_stats: Optional dict with contest statistics
        output_path: Optional output path
    
    Returns:
        Path to generated file
    """
    if contest_stats is None:
        contest_stats = {}
    
    generator = SummaryReportGenerator()
    return generator.generate_report(all_scores, category_scores, contest_stats, output_path)


if __name__ == "__main__":
    print("Summary Report Generator")
    print("This module should be imported, not run directly.")
