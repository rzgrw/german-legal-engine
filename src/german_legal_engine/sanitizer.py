"""
sanitizer.py
Legal text and citation formatting utilities with strict Zero-Dashes enforcement.
"""

import re
from typing import Optional

def sanitize_zero_dashes(text: str) -> str:
    """
    Sanitizes em-dashes and spaced en-dashes into professional German legal phrasing (commas, colons, or parentheses).
    Strictly conforms to German court pleading standards while preserving paragraph structure and hyphenated compound words.
    """
    if not text:
        return ""
    
    # 1. Normalize number ranges with en-dash/em-dash to ASCII hyphen (e.g. §§ 187–193 -> §§ 187-193)
    t = re.sub(r'(\d+)\s*[\u2013\u2014]\s*(\d+)', r'\1-\2', text)
    
    # 2. Replace em-dashes and spaced en-dashes with comma/space
    t = t.replace(" — ", ", ").replace("—", ", ")
    t = t.replace(" – ", ", ").replace("–", ", ")
    t = re.sub(r'\s+-\s+', ', ', t)
    
    # 3. Clean up lingering quotation dashes and unicode em/en-dashes
    for ch in ['\u2012', '\u2013', '\u2014', '\u2015']:
        t = t.replace(ch, ", ")
        
    # 4. Clean up double punctuation
    t = re.sub(r",\s*,+", ", ", t)
    t = re.sub(r":\s*,+", ": ", t)
    t = re.sub(r"\.\s*,+", ". ", t)
    
    # 5. Normalize whitespace within lines while preserving paragraph breaks
    lines = []
    for line in t.splitlines():
        cleaned_line = re.sub(r"[^\S\r\n]+", " ", line).strip()
        lines.append(cleaned_line)
        
    res = "\n".join(lines)
    # Collapse 3 or more consecutive newlines down to 2
    res = re.sub(r"\n{3,}", "\n\n", res)
    return res.strip()


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
