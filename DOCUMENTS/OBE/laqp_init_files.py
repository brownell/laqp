# ============================================================
# config/__init__.py
# ============================================================
"""
Louisiana QSO Party Configuration Package
"""
from .config import *

__version__ = "0.1.0"


# ============================================================
# laqp/__init__.py
# ============================================================
"""
Louisiana QSO Party Processor

Main package for contest log processing.
"""
__version__ = "0.1.0"
__author__ = "Jefferson Amateur Radio Club"


# ============================================================
# laqp/models/__init__.py
# ============================================================
"""
Database models for LAQP
"""
from .database import (
    Base, Database,
    Contestant, QSO, ScoreDetail,
    Parish, Multiplier, ContestStatistics,
    LocationType, ModeCategory, PowerLevel, OverlayCategory
)

__all__ = [
    'Base', 'Database',
    'Contestant', 'QSO', 'ScoreDetail',
    'Parish', 'Multiplier', 'ContestStatistics',
    'LocationType', 'ModeCategory', 'PowerLevel', 'OverlayCategory'
]


# ============================================================
# laqp/core/__init__.py
# ============================================================
"""
Core processing modules for LAQP
"""
from .validator import LogValidator, ValidationResult, validate_single_log
from .preparation import LogPreparation, prepare_single_log
from .scoring import ScoreCalculator, score_single_log, generate_score_report
from .statistics import StatisticsGenerator, generate_statistics_from_logs

__all__ = [
    'LogValidator',
    'ValidationResult',
    'validate_single_log',
    'LogPreparation',
    'prepare_single_log',
    'ScoreCalculator',
    'score_single_log',
    'generate_score_report',
    'StatisticsGenerator',
    'generate_statistics_from_logs',
]


# ============================================================
# laqp/utils/__init__.py
# ============================================================
"""
Utility functions for LAQP processing
"""
# TODO: Add utility functions as they're created
# from .cabrillo import parse_cabrillo_line, format_cabrillo_line
# from .callsign import get_prefix, is_dx_call, get_country
# from .file_ops import safe_copy, safe_move, ensure_dir

__all__ = []


# ============================================================
# laqp/cli/__init__.py
# ============================================================
"""
Command-line interface for LAQP processor
"""
# TODO: Add CLI commands when created

__all__ = []


# ============================================================
# web/__init__.py
# ============================================================
"""
Flask web application for LAQP
"""
# TODO: Add when Flask app is created
# from .app import create_app

__all__ = []


# ============================================================
# tests/__init__.py
# ============================================================
"""
Test suite for LAQP processor
"""
__all__ = []
