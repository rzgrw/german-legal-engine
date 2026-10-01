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
    "vvg": "vvg_2008",
    "gg": "gg",
    "owig": "owig_1968",
    "stvg": "stvg",
    "sgb2": "sgb_2",
    "sgb_ii": "sgb_2",
    "aufenthg": "aufenthg_2004",
    "famfg": "famfg",
    "brao": "brao",
    "aktg": "aktg",
    "gmbhg": "gmbhg",
    "inso": "inso",
    "vwgo": "vwgo",
    "stvo": "stvo_2013",
    "uwg": "uwg_2004",
    "asylg": "asylvfg_1992",
    "asylblg": "asylblg"
}

def fetch_statute_norm(law: str, section: str) -> Dict[str, Any]:
    """
    Fetches the verbatim text of a German federal statute paragraph.
    law: e.g. 'bgb', 'zpo', 'kschg', 'aufenthg'
    section: e.g. '823', '253', '1', '81'
    """
    law_clean = law.lower().strip()
    slug = COMMON_LAW_SLUGS.get(law_clean, law_clean)
    
    # Clean section number
    sec_clean = section.replace("§", "").replace("Art.", "").replace("Artikel", "").strip()
    
    # URL pattern on gesetze-im-internet: __<sec>.html, _<sec>.html, art_<sec>.html
    url_candidates = [
        f"https://www.gesetze-im-internet.de/{slug}/__{sec_clean}.html",
        f"https://www.gesetze-im-internet.de/{slug}/_{sec_clean}.html",
        f"https://www.gesetze-im-internet.de/{slug}/art_{sec_clean}.html",
        f"https://www.gesetze-im-internet.de/{slug}/___{sec_clean}.html"
    ]
    
    headers = {
        "User-Agent": "GermanLegalEngine/1.0 (Open Source Legal AI Framework; https://github.com/rzgrw/german-legal-engine)"
    }
    
    raw_bytes = None
    charset = None
    final_url = None
    
    for u in url_candidates:
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    raw_bytes = resp.read()
                    charset = resp.headers.get_content_charset()
                    final_url = u
                    break
        except Exception:
            continue
            
    if not raw_bytes:
        return {
            "success": False,
            "law": law.upper(),
            "section": sec_clean,
            "error": f"Norm {law.upper()} § {sec_clean} could not be retrieved from official registry."
        }
    
    # Handle charset (gesetze-im-internet.de frequently uses iso-8859-1)
    if not charset:
        m = re.search(rb"charset=([a-zA-Z0-9_-]+)", raw_bytes[:1024], re.IGNORECASE)
        charset = m.group(1).decode("ascii") if m else "iso-8859-1"
        
    try:
        html_content = raw_bytes.decode(charset, errors="replace")
    except Exception:
        html_content = raw_bytes.decode("utf-8", errors="replace")
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract official section title
    title_elem = soup.find("span", class_="jnentitel")
    if not title_elem:
        h1_elem = soup.find("h1")
        if h1_elem:
            # Often contains: <span class="jnenbez">§ 823</span> <span class="jnentitel">...</span>
            entitel = h1_elem.find("span", class_="jnentitel")
            title_text = entitel.get_text(strip=True) if entitel else h1_elem.get_text(strip=True)
        else:
            title_text = f"§ {sec_clean}"
    else:
        title_text = title_elem.get_text(strip=True)
        
    # Extract authentic paragraph texts
    # On gesetze-im-internet.de, individual paragraphs are <div class="jurAbsatz">
    body_elem = soup.find("div", class_="jnhtml") or soup.find("div", class_="jnentblock")
    paragraphs = []
    
    if body_elem:
        absatz_divs = body_elem.find_all("div", class_="jurAbsatz")
        if absatz_divs:
            for div in absatz_divs:
                txt = div.get_text(" ", strip=True)
                if txt:
                    paragraphs.append(txt)
        else:
            p_tags = body_elem.find_all("p")
            if p_tags:
                for p in p_tags:
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        paragraphs.append(txt)
            else:
                raw_text = body_elem.get_text("\n\n", strip=True)
                if raw_text:
                    paragraphs.append(raw_text)
                    
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
