"""
subsumption.py
Directed Legal Subsumption Engine (Tatbestandsmerkmale, Beweislast, Rechtsfolgen).
Transforms raw statutory text into structured procedural reasoning graphs.
"""

from typing import Dict, Any, List, Optional
from .sanitizer import sanitize_zero_dashes

# Known statutory subsumption blueprints
STATUTORY_BLUEPRINTS = {
    "BGB_823_1": {
        "norm": "§ 823 Abs. 1 BGB",
        "title": "Deliktischer Schadensersatzanspruch (Rechtsgutsverletzung)",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Verletzung eines geschützten Rechtsguts",
                "details": "Leben, Körper, Gesundheit, Freiheit, Eigentum oder berechtigtes sonstiges Recht (z.B. berechtigter Besitz, APR).",
                "beweislast": "Anspruchsteller (Kläger)"
            },
            {
                "merkmal": "Verletzungshandlung",
                "details": "Positives Tun oder pflichtwidriges Unterlassen (bei Bestehen einer Verkehrssicherungspflicht).",
                "beweislast": "Anspruchsteller (Kläger)"
            },
            {
                "merkmal": "Haftungsbegründende Kausalität",
                "details": "Äquivalente und adäquate Kausalität zwischen Handlung und Rechtsgutsverletzung (Schutzzweck der Norm).",
                "beweislast": "Anspruchsteller (Kläger)"
            },
            {
                "merkmal": "Rechtswidrigkeit",
                "details": "Wird durch die Rechtsgutsverletzung indiziert, es sei denn, ein Rechtfertigungsgrund (Notwehr, Einwilligung) greift ein.",
                "beweislast": "Vom Beklagten darzulegen und zu beweisen"
            },
            {
                "merkmal": "Verschulden",
                "details": "Vorsatz oder Fahrlässigkeit (§ 276 BGB). Verschuldensfähigkeit nach §§ 827, 828 BGB.",
                "beweislast": "Anspruchsteller (Kläger)"
            },
            {
                "merkmal": "Eintritt eines Schadens",
                "details": "Ermittlung nach der Differenzhypothese (§§ 249 ff. BGB).",
                "beweislast": "Anspruchsteller (Kläger)"
            },
            {
                "merkmal": "Haftungsausfüllende Kausalität",
                "details": "Kausalität zwischen primärer Rechtsgutsverletzung und dem konkret geltend gemachten Folgeschaden.",
                "beweislast": "Anspruchsteller (Kläger, Erleichterung gem. § 287 ZPO)"
            }
        ],
        "rechtsfolge": "Ersatz des daraus entstehenden Schadens (Naturalrestitution oder Schadensersatz in Geld, §§ 249 ff. BGB)."
    },
    "BGB_551": {
        "norm": "§ 551 BGB",
        "title": "Begrenzung und Anlage von Mietsicherheiten (Kaution)",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Bestehen eines Wohnraummietverhältnisses",
                "details": "Gültiger Mietvertrag über Wohnraum.",
                "beweislast": "Mieter"
            },
            {
                "merkmal": "Kautionsvereinbarung und Leistung",
                "details": "Zulässige Obergrenze maximal drei Nettokaltmieten (§ 551 Abs. 1 BGB). Dreimonatige Ratenzahlung (§ 551 Abs. 2 BGB).",
                "beweislast": "Mieter (Zahlungsnachweis)"
            },
            {
                "merkmal": "Beendigung des Mietverhältnisses und Rückgabe",
                "details": "Mietverhältnis beendet, Mietsache an den Vermieter übergeben.",
                "beweislast": "Mieter"
            },
            {
                "merkmal": "Ablauf der Prüf- und Überlegungsfrist",
                "details": "Übliche Frist von 3 bis 6 Monaten nach Wohnungsrückgabe abgelaufen.",
                "beweislast": "Mieter"
            },
            {
                "merkmal": "Fehlen bestehender Gegenansprüche",
                "details": "Keine fälligen Mietrückstände, Schäden oder offene Betriebskostennachforderungen des Vermieters.",
                "beweislast": "Vom Vermieter substantiiert darzulegen und aufzurechnen"
            }
        ],
        "rechtsfolge": "Auszahlung des Kautionsguthabens nebst den gem. § 551 Abs. 3 BGB angefallenen Zinserträgen."
    },
    "KSCHG_1": {
        "norm": "§ 1 KSchG",
        "title": "Kündigungsschutzklage (Soziale Ungerechtfertigtheit)",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Anwendbarkeit des KSchG",
                "details": "Betriebsgröße mehr als 10 Arbeitnehmer (§ 23 Abs. 1 KSchG) und Wartezeit von 6 Monaten erfüllt (§ 1 Abs. 1 KSchG).",
                "beweislast": "Arbeitnehmer darlegungspflichtig, Arbeitgeber beweisbelastet für Kleinbetrieb"
            },
            {
                "merkmal": "Fristgerechte Klageerhebung (§ 4 KSchG)",
                "details": "Klage innerhalb von 3 Wochen nach Zugang der schriftlichen Kündigung beim Arbeitsgericht eingereicht.",
                "beweislast": "Arbeitnehmer (Zugangsnachweis & Eingangsstempel ArbG)"
            },
            {
                "merkmal": "Soziale Rechtfertigung",
                "details": "Personenbedingte, verhaltensbedingte oder dringende betriebliche Erfordernisse (§ 1 Abs. 2 KSchG).",
                "beweislast": "Arbeitgeber (§ 1 Abs. 2 Satz 4 KSchG)"
            }
        ],
        "rechtsfolge": "Feststellung, dass das Arbeitsverhältnis durch die Kündigung nicht aufgelöst worden ist."
    }
}

def analyze_subsumption(law: str, section: str) -> Dict[str, Any]:
    """
    Returns the structured subsumption model for a given norm,
    including individual elements of proof, factual requirements, and burden of proof.
    """
    sec_clean = section.replace('§', '').strip()
    key = f"{law.upper()}_{sec_clean}"
    if key in STATUTORY_BLUEPRINTS:
        return {
            "success": True,
            "blueprint": STATUTORY_BLUEPRINTS[key]
        }
        
    for k, v in STATUTORY_BLUEPRINTS.items():
        if k.startswith(f"{key}_"):
            return {
                "success": True,
                "blueprint": v
            }
        
    return {
        "success": False,
        "message": f"Kein vordefinierter Subsumptions-Graph für {law} § {section} vorhanden. Bitte Gesetzestext via get_norm analysieren."
    }
