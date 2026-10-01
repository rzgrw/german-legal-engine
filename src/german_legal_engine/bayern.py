"""
bayern.py
Resilient native scraper and client for Bavarian State Courts (gesetze-bayern.de).
Supports AG München, LG München I & II, OLG München, ArbG München, LAG München, BayVerfGH, etc.
Zero external Node/NPM dependencies.
"""

import re
import urllib.request
import urllib.parse
import http.cookiejar
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

from .sanitizer import sanitize_zero_dashes, format_court_citation

BASE_URL = "https://www.gesetze-bayern.de"

class BayernLegalClient:
    """
    Scraper and API client for the official Bavarian Court Decision Registry (gesetze-bayern.de).
    Maintains session state and handles AntiForgery tokens with automatic retry.
    """
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        self.token: Optional[str] = None
        self._user_agent = "GermanLegalEngine/1.0 (Open Source Legal AI Framework; https://github.com/rzgrw/german-legal-engine)"

    def _init_session(self, force_refresh: bool = False) -> None:
        """Fetches fresh session cookies and the __RequestVerificationToken."""
        if self.token and not force_refresh:
            return
            
        req = urllib.request.Request(
            BASE_URL,
            headers={"User-Agent": self._user_agent}
        )
        try:
            with self.opener.open(req, timeout=15) as resp:
                soup = BeautifulSoup(resp.read(), "html.parser")
                tok_el = soup.find("input", attrs={"name": "__RequestVerificationToken"})
                if tok_el and tok_el.get("value"):
                    self.token = str(tok_el.get("value", ""))
        except Exception as e:
            # Clear token on failure
            self.token = None
            raise ConnectionError(f"Failed to initialize Bavarian court session: {e}")

    def search(
        self,
        query: str,
        limit: int = 5,
        court: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches decisions on gesetze-bayern.de.
        query: e.g. 'Mietkaution Kündigung'
        limit: maximum number of results
        court: optional filter e.g. 'AG München', 'OLG München'
        """
        self._init_session()
        
        def _execute_search(tok: str) -> List[Dict[str, Any]]:
            payload = urllib.parse.urlencode({
                "__RequestVerificationToken": tok,
                "SearchFields.Content": query
            }).encode("utf-8")
            
            req = urllib.request.Request(
                f"{BASE_URL}/Search",
                data=payload,
                headers={
                    "User-Agent": self._user_agent,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            with self.opener.open(req, timeout=20) as resp:
                soup = BeautifulSoup(resp.read(), "html.parser")
                
            results = []
            links = soup.select("p.hltitel a, a.hltitel")
            for a in links:
                href = str(a.get("href", ""))
                m_id = re.search(r"/Content/Document/([^?]+)", href)
                if not m_id:
                    continue
                doc_id = m_id.group(1).strip()
                if not doc_id.startswith("Y-"):
                    continue
                    
                raw_title = a.get_text(" ", strip=True)
                
                # Split 'Court: Subject'
                c_name, subject = "", raw_title
                if ":" in raw_title:
                    parts = raw_title.split(":", 1)
                    c_name = parts[0].strip()
                    subject = parts[1].strip()
                    
                sub_el = a.find_parent("div")
                sub_text = ""
                snippet = ""
                if sub_el:
                    sub_p = sub_el.find("p", class_="hlSubTitel")
                    if sub_p:
                        sub_text = sub_p.get_text(" ", strip=True)
                    snip_p = sub_el.find("p", class_="hlSnippet")
                    if snip_p:
                        snippet = snip_p.get_text(" ", strip=True)
                        
                # Extract date and Aktenzeichen e.g. 'Endurteil vom 10.06.2021 – 472 C 2064/20'
                dt_m = re.search(r"(?:(\w+)\s+)?vom\s+(\d{2}\.\d{2}\.\d{4})\s*[\u2013\u2014-]\s*(\S.*)", sub_text)
                dec_type = dt_m.group(1) if dt_m and dt_m.group(1) else "Entscheidung"
                dec_date = dt_m.group(2) if dt_m else ""
                az = dt_m.group(3) if dt_m else ""
                
                # Court filtering
                if court and c_name:
                    if court.lower() not in c_name.lower():
                        continue
                        
                citation = format_court_citation(c_name or "Gericht", dec_date or "ohne Datum", az or "ohne Az.")
                
                results.append({
                    "doc_id": doc_id,
                    "court": c_name,
                    "date": dec_date,
                    "az": az,
                    "type": dec_type,
                    "title": sanitize_zero_dashes(subject),
                    "snippet": sanitize_zero_dashes(snippet),
                    "citation": citation,
                    "jurisdiction": "BY",
                    "source_name": "Bayerische Staatskanzlei (gesetze-bayern.de)",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "source_url": f"{BASE_URL}/Content/Document/{doc_id}",
                    "is_search_snippet": True
                })
                
                if len(results) >= limit:
                    break
            return results

        try:
            return _execute_search(self.token or "")
        except Exception:
            # Refresh session once and retry
            self._init_session(force_refresh=True)
            if self.token:
                return _execute_search(self.token)
            return []

    def get_decision(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieves and parses the full decision from gesetze-bayern.de.
        Extracts structured Leitsatz, Normenketten, Tenor, Tatbestand, and Entscheidungsgründe.
        """
        clean_id = doc_id.replace("?hl=true", "").strip()
        url = f"{BASE_URL}/Content/Document/{clean_id}"
        req = urllib.request.Request(url, headers={"User-Agent": self._user_agent})
        
        try:
            with self.opener.open(req, timeout=20) as resp:
                soup = BeautifulSoup(resp.read(), "html.parser")
        except Exception as e:
            return {"error": f"Failed to retrieve decision {clean_id}: {e}"}
            
        cont = soup.find("div", class_="cont")
        if not cont:
            return {
                "doc_id": clean_id,
                "text": sanitize_zero_dashes(soup.get_text("\n\n", strip=True))
            }
            
        # Parse metadata
        leitsaetze = [ls.get_text(" ", strip=True) for ls in cont.select(".leitsatz")]
        normenketten = [n.get_text(" ", strip=True) for n in cont.select(".normenketten")]
        
        # Build clean markdown
        markdown_blocks = []
        
        # Headings and content blocks
        sections: Dict[str, List[str]] = {}
        curr_heading = "Header"
        sections[curr_heading] = []
        
        for el in cont.children:
            if not isinstance(el, Tag):
                continue
            if el.name in ["h1", "h2", "h3"]:
                h_text = el.get_text(strip=True)
                curr_heading = h_text
                sections[curr_heading] = []
            else:
                # Check for rdblocks with explicit Randnummer
                rd_el = el.find("div", class_="rd")
                rd_num = rd_el.get_text(strip=True) if isinstance(rd_el, Tag) else ""
                
                absatz_el = el.find("div", class_="absatz")
                p_text = absatz_el.get_text(" ", strip=True) if isinstance(absatz_el, Tag) else el.get_text(" ", strip=True)
                
                if p_text:
                    if rd_num and rd_num.isdigit():
                        sections[curr_heading].append(f"[Rn. {rd_num}] {p_text}")
                    else:
                        sections[curr_heading].append(p_text)
                        
        for heading, paras in sections.items():
            if not paras:
                continue
            if heading != "Header":
                markdown_blocks.append(f"### {heading}")
            for p in paras:
                markdown_blocks.append(p)
            markdown_blocks.append("")
            
        full_text = "\n\n".join(markdown_blocks).strip()
        
        return {
            "doc_id": clean_id,
            "url": url,
            "jurisdiction": "BY",
            "source_name": "Bayerische Staatskanzlei (gesetze-bayern.de)",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "is_official_verbatim": True,
            "leitsaetze": [sanitize_zero_dashes(l) for l in leitsaetze],
            "normenketten": normenketten,
            "text": sanitize_zero_dashes(full_text),
            "legal_notice": "Amtliches Werk gem. § 5 Abs. 1 UrhG. Redaktionelle Leitsätze sind als solche ausgewiesen."
        }


# Singleton client instance
_bayern_client = BayernLegalClient()

def search_bayern_court_decisions(query: str, limit: int = 5, court: Optional[str] = None) -> List[Dict[str, Any]]:
    return _bayern_client.search(query, limit=limit, court=court)

def get_bayern_court_decision(doc_id: str) -> Dict[str, Any]:
    return _bayern_client.get_decision(doc_id)
