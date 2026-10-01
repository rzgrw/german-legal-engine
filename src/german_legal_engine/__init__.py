"""
german-legal-engine
Sovereign German Legal Research & Procedural Subsumption Engine for AI Agents.
"""

from .client import LegalEngine
from .norms import fetch_statute_norm
from .case_law import search_case_law, get_decision_text
from .deadlines import calculate_deadline
from .subsumption import analyze_subsumption
from .sanitizer import sanitize_zero_dashes, format_court_citation

__version__ = "1.0.0"
__all__ = [
    "LegalEngine",
    "fetch_statute_norm",
    "search_case_law",
    "get_decision_text",
    "calculate_deadline",
    "analyze_subsumption",
    "sanitize_zero_dashes",
    "format_court_citation"
]
