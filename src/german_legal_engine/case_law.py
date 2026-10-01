"""
case_law.py
Retrieval of German Federal Court Decisions (BGH, BAG, BVerfG, BVerwG, BFH)
via official open repositories (Rechtsprechung im Internet).
"""

import subprocess
from typing import List, Dict, Any, Optional
from .sanitizer import sanitize_zero_dashes, format_court_citation

def search_case_law(query: str, limit: int = 5, court: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Searches official federal court decisions via Rechtsprechung im Internet.
    """
    cmd = ["npx", "-y", "@metaneutrons/german-legal-mcp", "rii_search", "--query", query, "--limit", str(limit)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        lines = [l for l in res.stdout.splitlines() if not l.startswith("[2026-") and not l.strip().startswith("module:")]
        
        results = []
        for l in lines:
            if not l.strip() or l.startswith("src\t") or "results (" in l:
                continue
            parts = l.split("\t")
            if len(parts) >= 7:
                src, dt, c_name, az, ecli, title, doc_id = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6]
                if court and court.lower() not in c_name.lower():
                    continue
                results.append({
                    "doc_id": doc_id.strip(),
                    "court": c_name.strip(),
                    "az": az.strip(),
                    "date": dt.strip(),
                    "ecli": ecli.strip() if ecli != "—" else None,
                    "title": sanitize_zero_dashes(title.strip()),
                    "citation": format_court_citation(c_name.strip(), dt.strip(), az.strip(), ecli.strip() if ecli != "—" else None)
                })
        return results
    except Exception as e:
        return [{"error": str(e)}]


def get_decision_text(doc_id: str) -> Dict[str, Any]:
    """
    Retrieves the decision text or Randnummern for a given document ID.
    """
    cmd = ["npx", "-y", "@metaneutrons/german-legal-mcp", "rii_get_decision", "--id", doc_id]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        clean_lines = [l for l in res.stdout.splitlines() if not l.startswith("[2026-") and not l.strip().startswith("module:")]
        text = "\n".join(clean_lines).strip()
        return {
            "doc_id": doc_id,
            "text": sanitize_zero_dashes(text)
        }
    except Exception as e:
        return {"error": str(e)}
