"""
case_law.py
Native retrieval of German Federal Court decisions (BGH, BAG, BVerfG, BVerwG, BFH)
and Bavarian State Court decisions (AG München, LG München, OLG München, etc.)
via official open repositories.
Zero external Node/NPM dependencies.
"""

import re
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

from .sanitizer import sanitize_zero_dashes, format_court_citation
from .bayern import search_bayern_court_decisions, get_bayern_court_decision

RII_BASE_URL = "https://www.rechtsprechung-im-internet.de/jportal/portal/page/bsjrsprod.psml"
USER_AGENT = "GermanLegalEngine/1.0 (Open Source Legal AI Framework; https://github.com/rzgrw/german-legal-engine)"


def search_federal_decisions(
    query: str,
    limit: int = 5,
    court: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Searches official German federal court decisions (BGH, BAG, BVerfG, etc.) via Rechtsprechung im Internet.
    """
    search_url = f"{RII_BASE_URL}/js_peid/Suchportlet2/media-type/html"
    params = {
        "formhaschangedvalue": "yes",
        "eventSubmit_doSearch": "suchen",
        "action": "portlets.jw.MainAction",
        "form": "jurisExpertSearch",
        "desc": "text",
        "query": query
    }
    
    full_url = f"{search_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            soup = BeautifulSoup(resp.read(), "html.parser")
    except Exception as e:
        return [{"error": f"Failed to search Rechtsprechung im Internet: {e}"}]
        
    results = []
    # Filter rows: target a.TrefferlisteHervorheben
    all_links = soup.find_all("a", class_="TrefferlisteHervorheben")
    links = [
        a for a in all_links
        if isinstance(a, Tag) and a.get("id") and str(a.get("id", "")).startswith("tlid") and "." not in str(a.get("id", ""))
    ]
    
    for a in links:
        href = str(a.get("href", ""))
        m_id = re.search(r"doc\.id=([^&]+)", href)
        if not m_id:
            continue
        doc_id = m_id.group(1).strip()
        
        row = a.find_parent("tr")
        date_val = ""
        if isinstance(row, Tag):
            tds = row.find_all("td", recursive=False)
            if tds:
                date_val = tds[0].get_text(strip=True)
                
        strongs = a.find_all("strong")
        court_val = strongs[0].get_text(strip=True) if strongs else ""
        summary_val = strongs[-1].get_text(" ", strip=True) if len(strongs) > 1 else ""
        
        span = a.find("span")
        span_html = str(span) if span else ""
        first_line = re.split(r"<br\s*/?>", span_html, flags=re.IGNORECASE)[0]
        first_text = BeautifulSoup(first_line, "html.parser").get_text(" ", strip=True)
        az_val = ""
        if "|" in first_text:
            az_val = first_text.split("|", 1)[1].strip()
            
        if court and court_val:
            if court.lower() not in court_val.lower():
                continue
                
        citation = format_court_citation(court_val or "Bundesgericht", date_val or "ohne Datum", az_val or "ohne Az.")
        
        results.append({
            "doc_id": doc_id,
            "court": court_val,
            "date": date_val,
            "az": az_val,
            "title": sanitize_zero_dashes(summary_val or first_text),
            "citation": citation,
            "jurisdiction": "BUND",
            "source_url": f"{RII_BASE_URL}?doc.id={doc_id}"
        })
        
        if len(results) >= limit:
            break
            
    return results


def get_federal_decision(doc_id: str) -> Dict[str, Any]:
    """
    Retrieves and parses the decision text from Rechtsprechung im Internet.
    """
    url = f"{RII_BASE_URL}?doc.id={doc_id}&doc.part=L&showdoccase=1&paramfromHL=true"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            soup = BeautifulSoup(resp.read(), "html.parser")
    except Exception as e:
        return {"error": f"Failed to retrieve federal decision {doc_id}: {e}"}
        
    doc_layout = soup.find("div", class_="docLayoutText")
    if doc_layout:
        raw_text = doc_layout.get_text("\n\n", strip=True)
    else:
        jur_html = soup.find("div", class_="jurHtml")
        raw_text = jur_html.get_text("\n\n", strip=True) if jur_html else soup.get_text("\n\n", strip=True)
        
    return {
        "doc_id": doc_id,
        "url": url,
        "jurisdiction": "BUND",
        "text": sanitize_zero_dashes(raw_text)
    }


def search_case_law(
    query: str,
    limit: int = 5,
    court: Optional[str] = None,
    source: str = "ALL"
) -> List[Dict[str, Any]]:
    """
    Unified entrypoint for case law search across federal and state courts.
    source: 'ALL', 'BUND' (federal), or 'BY' (Bavarian state courts).
    """
    source_clean = source.upper().strip()
    
    is_bayern_court = False
    if court:
        c_lower = court.lower()
        if any(term in c_lower for term in ["münchen", "bayern", "nürnberg", "augsburg", "bayverfgh", "bamberg", "würzburg"]):
            is_bayern_court = True
            
    if source_clean == "BY" or is_bayern_court:
        return search_bayern_court_decisions(query, limit=limit, court=court)
        
    if source_clean == "BUND":
        return search_federal_decisions(query, limit=limit, court=court)
        
    # source == "ALL": query both and combine
    federal_hits = search_federal_decisions(query, limit=limit, court=court)
    bayern_hits = search_bayern_court_decisions(query, limit=limit, court=court)
    
    # Filter errors
    clean_fed = [h for h in federal_hits if "error" not in h]
    clean_by = [h for h in bayern_hits if "error" not in h]
    
    combined = []
    # Interleave or merge results
    max_len = max(len(clean_fed), len(clean_by))
    for i in range(max_len):
        if i < len(clean_fed):
            combined.append(clean_fed[i])
        if i < len(clean_by):
            combined.append(clean_by[i])
        if len(combined) >= limit:
            break
            
    return combined if combined else (federal_hits or bayern_hits)


def get_decision_text(doc_id: str) -> Dict[str, Any]:
    """
    Retrieves decision text by ID (automatically routes Y-* IDs to gesetze-bayern.de, others to federal RII).
    """
    if doc_id.startswith("Y-"):
        return get_bayern_court_decision(doc_id)
    return get_federal_decision(doc_id)
