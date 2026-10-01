"""
sanitizer.py
Legal text and citation formatting utilities with strict Zero-Dashes enforcement.
"""

import re
from typing import Optional

def sanitize_zero_dashes(text: str) -> str:
    """
    Sanitizes em-dashes and spaced en-dashes into professional German legal phrasing (commas, colons, or parentheses).
    Strictly conforms to German court pleading standards.
    """
    if not text:
        return ""
    
    # Replace em-dashes and spaced en-dashes with comma/space
    t = text.replace(" — ", ", ").replace("—", ", ")
    t = t.replace(" – ", ", ").replace("–", ", ")
    t = t.replace(" - ", ", ")
    
    # Clean up lingering unicode dash characters
    for ch in ['\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2015']:
        t = t.replace(ch, ", ")
        
    # Clean up double punctuation
    t = re.sub(r",\s*,+", ", ", t)
    t = re.sub(r":\s*,+", ": ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def format_court_citation(court: str, date_str: str, az: str, ecli: Optional[str] = None) -> str:
    """
    Formats an authentic German court citation according to standard legal style:
    e.g. 'BGH, Urteil vom 15.03.2023, Az. VIII ZR 125/22'
    """
    c = court.strip()
    # Normalize common court prefixes
    if not c.startswith("BGH") and "bundesgerichtshof" in c.lower():
        c = "BGH"
    elif not c.startswith("BAG") and "bundesarbeitsgericht" in c.lower():
        c = "BAG"
    elif not c.startswith("BVerfG") and "bundesverfassungsgericht" in c.lower():
        c = "BVerfG"
        
    citation = f"{c}, Entscheidung vom {date_str.strip()}, Az. {az.strip()}"
    if ecli:
        citation += f" (ECLI: {ecli.strip()})"
    return citation
