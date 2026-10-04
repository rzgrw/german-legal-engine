"""
triage.py
System 1 Legal Intake & Triage Layer for German Legal Engine.
Integrates Laya (https://brainfunctioncollapse.com/laya) as a non-generative,
typed decision model for rapid local legal matter classification, urgency scoring,
and deadline risk detection in ~20-30 ms without external API calls or PII leakage.
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from .sanitizer import anonymize_legal_text
from .subsumption import analyze_subsumption

# Standard typed legal questions for Laya
GERMAN_LEGAL_TRIAGE_QUESTIONS = {
    "rechtsgebiet": {
        "type": "choice",
        "instructions": "Welchem Rechtsgebiet ist dieser Sachverhalt zuzuordnen?",
        "criteria": {
            "arbeitsrecht": "Kündigung des Arbeitsvertrags, Abmahnung, Lohn, Kündigungsschutzklage, Arbeitnehmer",
            "mietrecht": "Wohnraummiete, Kündigung Mietvertrag, Mietminderung wegen Mängeln, Kaution, Nebenkosten",
            "verkehrsrecht_owig": "Bußgeldbescheid, Geschwindigkeitsüberschreitung, Fahrverbot, Ordnungswidrigkeit, Blitzer",
            "vertragsrecht_schadensersatz": "Pflichtverletzung aus Vertrag, Schadensersatz, Rücktritt, Gewährleistung, Kaufvertrag",
            "deliktsrecht": "Unerlaubte Handlung, Schadensersatz wegen Körper- oder Sachschaden, Verletzung von Rechten",
            "allgemein": "Sonstige allgemeine Rechtsfrage oder nicht spezifischer Sachverhalt"
        }
    },
    "dringlichkeit": {
        "type": "score",
        "instructions": "Wie akut ist der anwaltliche Handlungsbedarf bei diesem Vorgang?",
        "criteria": [
            "routine: normale juristische Prüfung ohne Fristdruck",
            "mittelfristig: Klärungsbedarf binnen weniger Wochen",
            "akute_notfrist: sofortiger Handlungsbedarf wegen drohendem Fristablauf oder Kündigungsschutz"
        ]
    },
    "droht_fristablauf": {
        "type": "noul",
        "instructions": "Droht in diesem Fall der Ablauf einer gesetzlichen oder behördlichen Ausschlussfrist?",
        "criteria": {
            "true": "Es liegt eine Kündigung, ein Bescheid oder eine zeitkritische Klagefrist vor.",
            "false": "Keine konkrete Frist oder zeitliche Dringlichkeit ersichtlich."
        }
    },
    "erfordert_sofortige_eskalation": {
        "type": "noul",
        "instructions": "Muss dieser Vorgang prioritär einem Rechtsanwalt zur Fristenprüfung vorgelegt werden?",
        "criteria": {
            "true": "Sofortige anwaltliche Fristenkontrolle dringend geboten.",
            "false": "Kann in den regulären Kanzlei-Posteingang eingesteuert werden."
        }
    }
}

RECOMMENDED_NORMS_BY_DOMAIN: Dict[str, List[Tuple[str, str]]] = {
    "arbeitsrecht": [("KSchG", "4"), ("KSchG", "1"), ("BGB", "626")],
    "mietrecht": [("BGB", "535"), ("BGB", "551"), ("BGB", "314")],
    "verkehrsrecht_owig": [("OWiG", "67")],
    "vertragsrecht_schadensersatz": [("BGB", "280"), ("BGB", "314")],
    "deliktsrecht": [("BGB", "823")]
}

_LAYA_AGENT = None
_LAYA_CHECKED = False

def get_laya_agent():
    """Lazily loads the Laya multilingual decision model if installed."""
    global _LAYA_AGENT, _LAYA_CHECKED
    if _LAYA_CHECKED:
        return _LAYA_AGENT
    _LAYA_CHECKED = True
    try:
        import importlib
        laya = importlib.import_module("laya")
        # For German legal text, multilingual checkpoint provides fast local inference (~21ms)
        _LAYA_AGENT = laya.load("convaiinnovations/laya", subfolder="multilingual")
    except Exception:
        _LAYA_AGENT = None
    return _LAYA_AGENT


def heuristic_fallback_triage(clean_text: str) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback when the neural Laya model is not installed.
    Ensures zero runtime errors and provides baseline classification.
    """
    text_lower = clean_text.lower()
    
    scores = {
        "arbeitsrecht": 0,
        "mietrecht": 0,
        "verkehrsrecht_owig": 0,
        "vertragsrecht_schadensersatz": 0,
        "deliktsrecht": 0,
        "allgemein": 1
    }
    
    # Keyword detection for German legal categories
    if any(k in text_lower for k in ["kündigung", "arbeitgeber", "arbeitnehmer", "arbeitsvertrag", "kündigungsschutz", "abmahnung", "fristlos"]):
        scores["arbeitsrecht"] += 5
    if any(k in text_lower for k in ["mieter", "vermieter", "miete", "kaution", "mietvertrag", "mietminderung", "nebenkosten"]):
        scores["mietrecht"] += 5
    if any(k in text_lower for k in ["bußgeld", "blitzer", "fahrverbot", "ordnungswidrigkeit", "geschwindigkeitsüberschreitung", "polizei"]):
        scores["verkehrsrecht_owig"] += 5
    if any(k in text_lower for k in ["schadensersatz", "pflichtverletzung", "vertrag", "mangel", "gewährleistung"]):
        scores["vertragsrecht_schadensersatz"] += 4
    if any(k in text_lower for k in ["körperverletzung", "unerlaubte handlung", "schmerzensgeld", "delikt"]):
        scores["deliktsrecht"] += 4

    best_domain = max(list(scores.keys()), key=lambda k: scores[k])
    if scores[best_domain] == 1:
        best_domain = "allgemein"
        
    # Deadline & Urgency detection
    has_deadline = any(k in text_lower for k in ["frist", "kündigung", "bescheid", "wochen", "tage", "sofort", "eilig"])
    urgency_score = 2.0 if has_deadline else 0.5
    
    return {
        "engine": "heuristic_fallback",
        "laya_model_active": False,
        "notice": "Laya neural model not installed. Install via `pip install laya` or `pip install german-legal-engine[laya]` for calibrated neural probabilities (https://brainfunctioncollapse.com/laya).",
        "rechtsgebiet": {
            "choice": best_domain,
            "confidence": 0.85 if scores[best_domain] > 1 else 0.40,
            "probabilities": {k: round(v / sum(scores.values()), 3) for k, v in scores.items()}
        },
        "dringlichkeit": {
            "score": urgency_score,
            "confidence": 0.80
        },
        "droht_fristablauf": {
            "noul": 0.90 if has_deadline else 0.15,
            "confidence": 0.80
        },
        "erfordert_sofortige_eskalation": {
            "noul": 0.85 if has_deadline else 0.10,
            "confidence": 0.75
        }
    }


class LegalTriage:
    """
    Non-generative System 1 Decision & Intake Classifier for law firms.
    Underpins the German Legal Engine with 20-30ms local typed decisions.
    """

    @classmethod
    def get_triage_questions(cls) -> Dict[str, Any]:
        """Returns the canonical typed question definitions for German legal triage."""
        return GERMAN_LEGAL_TRIAGE_QUESTIONS

    @classmethod
    def triage_mandate(
        cls,
        text: str,
        state: str = "BY",
        agent: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Triages an incoming legal mandate, letter or email.
        
        1. Anonymizes PII locally (DSGVO Art. 5).
        2. Queries Laya System 1 decision model (or heuristic fallback).
        3. Maps results to relevant statutory norms and subsumption blueprints.
        """
        # Step 1: Local PII protection gate
        clean_text = anonymize_legal_text(text)
        
        # Step 2: Laya inference or fallback
        laya_instance = agent or get_laya_agent()
        
        if laya_instance is not None:
            try:
                # Laya predicts typed probabilities in a single forward pass
                res = laya_instance.predict(clean_text, GERMAN_LEGAL_TRIAGE_QUESTIONS, lang="de")
                answers = res.get("answers", {})
                triage_data = {
                    "engine": "laya_multilingual",
                    "laya_model_active": True,
                    "model_source": "https://brainfunctioncollapse.com/laya",
                    "rechtsgebiet": answers.get("rechtsgebiet", {}),
                    "dringlichkeit": answers.get("dringlichkeit", {}),
                    "droht_fristablauf": answers.get("droht_fristablauf", {}),
                    "erfordert_sofortige_eskalation": answers.get("erfordert_sofortige_eskalation", {})
                }
            except Exception as e:
                triage_data = heuristic_fallback_triage(clean_text)
                triage_data["laya_error"] = str(e)
        else:
            triage_data = heuristic_fallback_triage(clean_text)

        # Step 3: Norm mapping & statutory guidance
        chosen_domain = triage_data["rechtsgebiet"].get("choice", "allgemein")
        recommended_norm_tuples = RECOMMENDED_NORMS_BY_DOMAIN.get(chosen_domain, [])
        
        suggested_blueprints = []
        for law, sec in recommended_norm_tuples:
            bp_res = analyze_subsumption(law, sec)
            if bp_res.get("success"):
                bp = bp_res["blueprint"]
                suggested_blueprints.append({
                    "norm": bp["norm"],
                    "title": bp["title"],
                    "tatbestandsmerkmale_count": len(bp["tatbestandsmerkmale"]),
                    "rechtsfolge": bp["rechtsfolge"]
                })

        # Date pattern check in text for deadline hints
        date_pattern = r"\b(\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{2}-\d{2})\b"
        found_dates = re.findall(date_pattern, clean_text)
        
        return {
            "success": True,
            "jurisdiction_state": state.upper(),
            "domain": chosen_domain,
            "domain_confidence": triage_data["rechtsgebiet"].get("confidence", 0.0),
            "urgency_score": triage_data["dringlichkeit"].get("score", 0.0),
            "deadline_risk_prob": triage_data["droht_fristablauf"].get("noul", 0.0),
            "requires_escalation": triage_data["erfordert_sofortige_eskalation"].get("noul", 0.0) >= 0.5,
            "detected_event_dates": found_dates,
            "suggested_statutory_norms": suggested_blueprints,
            "raw_triage": triage_data
        }
