"""
client.py
High-level unified interface for the German Legal Engine.
"""

from datetime import date
from typing import Dict, Any, List, Optional, Tuple

from .norms import fetch_statute_norm
from .case_law import search_case_law, get_decision_text
from .deadlines import calculate_deadline
from .subsumption import analyze_subsumption
from .sanitizer import sanitize_zero_dashes, anonymize_legal_text
from .triage import LegalTriage

class LegalEngine:
    """
    Sovereign German Legal Research and Subsumption Engine.
    """
    
    @staticmethod
    def get_norm(law: str, section: str) -> Dict[str, Any]:
        """Fetch authentic statutory law from official registry."""
        return fetch_statute_norm(law, section)
        
    @staticmethod
    def search_precedents(
        query: str,
        limit: int = 5,
        court: Optional[str] = None,
        source: str = "ALL"
    ) -> List[Dict[str, Any]]:
        """Search federal and state court decisions (BGH, BAG, BVerfG, AG/LG/OLG München, etc.)."""
        return search_case_law(query, limit=limit, court=court, source=source)
        
    @staticmethod
    def get_decision(doc_id: str) -> Dict[str, Any]:
        """Fetch decision text by document ID."""
        return get_decision_text(doc_id)
        
    @staticmethod
    def compute_deadline(
        ereignis_datum: date,
        dauer_wert: int,
        dauer_einheit: str = "wochen",
        state: str = "BY"
    ) -> Dict[str, Any]:
        """Calculate procedural deadline under §§ 187-193 BGB."""
        return calculate_deadline(ereignis_datum, dauer_wert, dauer_einheit, state)
        
    @staticmethod
    def get_subsumption_blueprint(law: str, section: str) -> Dict[str, Any]:
        """Retrieve structured legal elements and burden of proof."""
        return analyze_subsumption(law, section)
        
    @staticmethod
    def anonymize_text(text: str) -> str:
        """Redact sensitive PII (IBAN, email, phone, addresses) under DSGVO Art. 5."""
        return anonymize_legal_text(text)
        
    @staticmethod
    def triage_mandate(text: str, state: str = "BY", agent: Optional[Any] = None) -> Dict[str, Any]:
        """
        Triage and classify an incoming mandate or legal text using the Laya System 1 decision model
        (https://brainfunctioncollapse.com/laya) or deterministic fallback.
        """
        return LegalTriage.triage_mandate(text, state=state, agent=agent)
        
    @classmethod
    def prepare_dossier_context(cls, norms: List[Tuple[str, str]], query: str) -> str:
        """
        Builds a comprehensive legal context block for LLM prompts,
        court pleadings, or legal briefs with strict zero-dashes compliance.
        """
        lines = ["### Maßgebliche Rechtsnormen & BGH/BAG-Rechtsprechung (German Legal Engine Ground Truth):\n"]
        for law, sec in norms:
            n_res = cls.get_norm(law, sec)
            if n_res.get("success"):
                lines.append(f"#### {n_res['law']} § {n_res['section']}: {n_res['title']}")
                lines.append(f"{n_res['content_clean']}\n")
                
                # Check for subsumption blueprint
                sub_res = cls.get_subsumption_blueprint(law, sec)
                if sub_res.get("success"):
                    bp = sub_res["blueprint"]
                    lines.append(f"**Tatbestandsmerkmale & Beweislast ({bp['title']}):**")
                    for m in bp["tatbestandsmerkmale"]:
                        lines.append(f"- **{m['merkmal']}**: {m['details']} *(Beweislast: {m['beweislast']})*")
                    lines.append(f"**Rechtsfolge:** {bp['rechtsfolge']}\n")
                    
        precedents = cls.search_precedents(query, limit=3)
        if precedents and "error" not in precedents[0]:
            lines.append("#### Relevante Leitsatzentscheidungen:")
            for p in precedents:
                lines.append(f"- **{p['citation']}**: {p['title']}")
                
        return "\n".join(lines)
