#!/usr/bin/env python3
"""
Louisiana QSO Party - Leaderboard Generator

Generates leaderboard tables based on declarative configuration.
Interprets LEADERBOARDS configuration to create ranked tables.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Tuple


class LeaderboardGenerator:
    """Generates leaderboards from database based on configuration"""
    
    def __init__(self, db_path: str = 'laqp/database/laqp.db'):
        """
        Initialize leaderboard generator.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
    
    def generate_leaderboards(self, year: str, leaderboards_config: List) -> List[Dict]:
        """
        Generate all leaderboards for a year based on configuration.
        
        Args:
            year: Contest year
            leaderboards_config: LEADERBOARDS configuration from config.py
            
        Returns:
            List of sections, each containing tables with data
        """
        sections = []
        
        for section_config in leaderboards_config:
            section = self._generate_section(year, section_config)
            if section['tables']:  # Only include sections with tables
                sections.append(section)
        
        return sections
    
    def _generate_section(self, year: str, section_config: List[Dict]) -> Dict:
        """
        Generate a single section with multiple tables.
        
        Args:
            year: Contest year
            section_config: Section configuration (first element is metadata, rest are tables)
            
        Returns:
            Dict with section metadata and tables
        """
        # First element is section metadata
        metadata = section_config[0]
        section_title = metadata['section_title']
        show_fields = metadata['show']
        
        # Rest are table definitions
        tables = []
        for table_config in section_config[1:]:
            table = self._generate_table(year, table_config, show_fields)
            if table['rows']:  # Only include tables with data (skip empty tables)
                tables.append(table)
        
        return {
            'section_title': section_title,
            'show_fields': show_fields,
            'tables': tables
        }
    
    def _generate_table(self, year: str, table_config: Dict, show_fields: List) -> Dict:
        """
        Generate a single ranked table.
        
        Args:
            year: Contest year
            table_config: Table configuration with 'title' and 'ands'
            show_fields: Fields to display from section metadata
            
        Returns:
            Dict with table title, headers, and ranked rows
        """
        title = table_config['title']
        ands = table_config['ands']
        
        # Build SQL query
        sql, params = self._build_query(year, ands, show_fields)
        
        # Execute query
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        
        # Add rank column (starting at 1)
        ranked_rows = []
        for rank, row in enumerate(rows, 1):
            ranked_row = [rank] + list(row)
            ranked_rows.append(ranked_row)
        
        # Build headers (Rank + show fields)
        headers = ['Rank'] + [field[1] for field in show_fields]
        
        return {
            'title': title,
            'headers': headers,
            'rows': ranked_rows
        }
    
    def _build_query(self, year: str, ands: List, show_fields: List) -> Tuple[str, List]:
        """
        Build SQL query from AND conditions.
        
        Args:
            year: Contest year
            ands: List of AND conditions:
                  - 2-element: [field, value] → field = value
                  - 3-element: [field, operator, value] → field operator value
            show_fields: Fields to select
            
        Returns:
            Tuple of (sql_string, parameters)
        """
        # Extract field names to select
        select_fields = [field[0] for field in show_fields]
        select_clause = ', '.join(select_fields)
        
        # Build WHERE clause
        where_conditions = ['year = ?', 'is_valid = 1', "callsign != 'N5LCC'"]
        params = [year]
        
        for and_clause in ands:
            if len(and_clause) == 2:
                # Simple equality: [field, value]
                field, value = and_clause
                where_conditions.append(f"{field} = ?")
                params.append(value)
            elif len(and_clause) == 3:
                # Custom operator: [field, operator, value]
                field, operator, value = and_clause
                where_conditions.append(f"{field} {operator} ?")
                params.append(value)
            else:
                raise ValueError(f"Invalid AND clause: {and_clause} (must be 2 or 3 elements)")
        
        where_clause = ' AND '.join(where_conditions)
        
        # Build complete query (always ordered by final_score DESC)
        sql = f"""
            SELECT {select_clause}
            FROM contest_results
            WHERE {where_clause}
            ORDER BY final_score DESC
        """
        
        return sql, params


# Convenience function
def generate_leaderboards(year: str, leaderboards_config: List, 
                         db_path: str = 'laqp/database/laqp.db') -> List[Dict]:
    """
    Generate leaderboards for a year.
    
    Args:
        year: Contest year
        leaderboards_config: LEADERBOARDS configuration from config.py
        db_path: Path to database file
        
    Returns:
        List of sections with tables
    """
    generator = LeaderboardGenerator(db_path)
    return generator.generate_leaderboards(year, leaderboards_config)

# To generate the HTML for the Final Report
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

# To print the Final Report on paper
def print_final_report(sections):
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

if __name__ == "__main__":
    print("LAQP Leaderboard Generator")
    print("This module should be imported, not run directly.")
    print()
    print("Usage:")
    print("  from leaderboards import generate_leaderboards")
    print("  from config.config import LEADERBOARDS")
    print()
    print("  sections = generate_leaderboards('2026', LEADERBOARDS)")
    print()
    print("  for section in sections:")
    print("      print(section['section_title'])")
    print("      for table in section['tables']:")
    print("          print(f\"  {table['title']}: {len(table['rows'])} entries\")")
