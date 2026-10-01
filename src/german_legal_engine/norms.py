"""
norms.py
Deterministic retrieval of authentic German statutory laws (BGB, ZPO, KSchG, StGB, RVG, etc.)
Directly accesses official repositories (gesetze-im-internet.de) without hallucination.
"""

import re
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from .sanitizer import sanitize_zero_dashes

# Common law slugs on gesetze-im-internet.de
COMMON_LAW_SLUGS = {
    "bgb": "bgb",
    "zpo": "zpo",
    "kschg": "kschg",
    "stgb": "stgb",
    "stpo": "stpo",
    "arbgg": "arbgg",
    "rvg": "rvg",
    "hgb": "hgb",
    "vvg": "vvg",
    "gg": "gg",
    "owig": "owig",
    "stvg": "stvg",
    "sgb2": "sgb_2",
    "sgb_ii": "sgb_2",
    "aufenthg": "aufenthg",
    "famfg": "famfg",
    "brao": "brao"
}

def fetch_statute_norm(law: str, section: str) -> Dict[str, Any]:
    """
    Fetches the verbatim text of a German federal statute paragraph.
    law: e.g. 'bgb', 'zpo', 'kschg'
    section: e.g. '823', '253', '1'
    """
    law_clean = law.lower().strip()
    slug = COMMON_LAW_SLUGS.get(law_clean, law_clean)
    
    # Clean section number
    sec_clean = section.replace("§", "").replace("Art.", "").replace("Artikel", "").strip()
    
    # URL pattern on gesetze-im-internet: __<sec>.html or <sec>.html
    # In gesetze-im-internet, most numbered sections use double underscores __823.html
    url_candidates = [
        f"https://www.gesetze-im-internet.de/{slug}/__{sec_clean}.html",
        f"https://www.gesetze-im-internet.de/{slug}/_{sec_clean}.html",
        f"https://www.gesetze-im-internet.de/{slug}/art_{sec_clean}.html"
    ]
    
    headers = {
        "User-Agent": "GermanLegalEngine/1.0 (Open Source Legal AI Framework; contact@leolegal.de)"
    }
    
    html_content = None
    final_url = None
    
    for u in url_candidates:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    html_content = resp.read().decode("utf-8", errors="replace")
                    final_url = u
                    break
        except Exception:
            continue
            
    if not html_content:
        return {
            "success": False,
            "law": law.upper(),
            "section": sec_clean,
            "error": f"Norm {law.upper()} § {sec_clean} could not be retrieved from official registry."
        }
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract title and paragraph bodies
    # On gesetze-im-internet, heading is in jnnorm / jnsp
    title_elem = soup.find("span", class_="jnentitel") or soup.find("h1")
    title_text = title_elem.get_text(strip=True) if title_elem else f"§ {sec_clean}"
    
    # Extract paragraph texts
    body_elem = soup.find("div", class_="jnhtml") or soup.find("div", class_="jnentblock")
    paragraphs = []
    
    if body_elem:
        for p in body_elem.find_all("p"):
            p_text = p.get_text(strip=True)
            if p_text:
                paragraphs.append(p_text)
    else:
        for p in soup.find_all("p"):
            p_text = p.get_text(strip=True)
            if p_text:
                paragraphs.append(p_text)
                
    full_text = "\n\n".join(paragraphs) if paragraphs else soup.get_text(separator="\n", strip=True)
    
    return {
        "success": True,
        "law": law.upper(),
        "section": sec_clean,
        "title": title_text,
        "source_url": final_url,
        "content_raw": full_text,
        "content_clean": sanitize_zero_dashes(full_text)
    }
