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
    "BGB_280_1": {
        "norm": "§ 280 Abs. 1 BGB",
        "title": "Schadensersatz wegen Pflichtverletzung (Vertragliche Haftung)",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Bestehen eines Schuldverhältnisses",
                "details": "Wirksamer Vertrag (z.B. Kauf-, Dienst-, Werk- oder Mietvertrag) oder vorvertragliches Schuldverhältnis (§ 311 Abs. 2 BGB).",
                "beweislast": "Gläubiger (Anspruchsteller / Kläger)"
            },
            {
                "merkmal": "Pflichtverletzung",
                "details": "Verletzung einer Hauptleistungspflicht oder einer vertraglichen Neben- bzw. Schutzpflicht (§ 241 Abs. 2 BGB).",
                "beweislast": "Gläubiger (Anspruchsteller / Kläger)"
            },
            {
                "merkmal": "Kausalität zwischen Pflichtverletzung und Schaden",
                "details": "Schaden adäquat kausal durch die Pflichtverletzung verursacht.",
                "beweislast": "Gläubiger (Anspruchsteller / Kläger)"
            },
            {
                "merkmal": "Vertretenmüssen / Verschulden (§ 280 Abs. 1 Satz 2 BGB)",
                "details": "Gesetzliche Vermutung des Vertretenmüssens. Schuldner haftet für Vorsatz und Fahrlässigkeit (§ 276 BGB) sowie Erfüllungsgehilfen (§ 278 BGB).",
                "beweislast": "Schuldner (Beklagter muss sich exkulpieren)"
            },
            {
                "merkmal": "Eintritt eines ersatzfähigen Schadens",
                "details": "Vermögensschaden nach Differenzhypothese gem. §§ 249 ff. BGB.",
                "beweislast": "Gläubiger (Anspruchsteller / Kläger)"
            }
        ],
        "rechtsfolge": "Anspruch auf Ersatz des aus der Pflichtverletzung entstandenen Schadens gem. §§ 249 ff. BGB."
    },
    "BGB_314": {
        "norm": "§ 314 BGB",
        "title": "Kündigung von Dauerschuldverhältnissen aus wichtigem Grund",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Vorliegen eines Dauerschuldverhältnisses",
                "details": "Fortlaufendes Vertragsverhältnis wie Miet-, Dienst-, Gesellschafts-, Lizenz- oder Rahmenvertrag.",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Wichtiger Grund (§ 314 Abs. 1 Satz 2 BGB)",
                "details": "Tatsachen, aufgrund derer dem Kündigenden unter Berücksichtigung aller Umstände des Einzelfalls und unter Abwägung der beiderseitigen Interessen die Fortsetzung bis zur vereinbarten Beendigung oder bis zum Ablauf einer Kündigungsfrist nicht zugemutet werden kann.",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Erfolglose Abmahnung oder Fristsetzung (§ 314 Abs. 2 BGB)",
                "details": "Besteht der wichtige Grund in der Verletzung einer Vertragspflicht, ist die Kündigung erst nach erfolglosem Ablauf einer Abhilfefrist oder nach erfolgloser Abmahnung zulässig (Ausnahmen gem. § 323 Abs. 2 BGB).",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Einhaltung der angemessenen Kündigungsfrist (§ 314 Abs. 3 BGB)",
                "details": "Die Kündigung kann nur innerhalb einer angemessenen Frist nach Kenntniserlangung vom Kündigungsgrund erfolgen.",
                "beweislast": "Kündigender"
            }
        ],
        "rechtsfolge": "Beendigung des Dauerschuldverhältnisses mit Zugang der Kündigung für die Zukunft (ex nunc)."
    },
    "BGB_535_1_2": {
        "norm": "§ 535 Abs. 1 Satz 2 BGB",
        "title": "Mängelbeseitigung und Instandhaltung im Mietrecht",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Wirksamer Mietvertrag über die Mietsache",
                "details": "Bestehendes Mietverhältnis über Wohn- oder Gewerberaum.",
                "beweislast": "Mieter"
            },
            {
                "merkmal": "Vorliegen eines Mangels der Mietsache",
                "details": "Abweichung der Ist-Beschaffenheit von der vertraglich geschuldeten Soll-Beschaffenheit, welche die Tauglichkeit zum vertragsgemäßen Gebrauch mindert oder aufhebt (§ 536 Abs. 1 BGB).",
                "beweislast": "Mieter"
            },
            {
                "merkmal": "Mängelanzeige an den Vermieter (§ 536c BGB)",
                "details": "Unverzügliche Anzeige des Mangels gegenüber dem Vermieter zwecks Möglichkeit zur Abhilfe.",
                "beweislast": "Mieter (Zugang der Mängelanzeige)"
            },
            {
                "merkmal": "Fehlen von Ausschlussgründen",
                "details": "Keine Kenntnis oder grob fahrlässige Unkenntnis bei Vertragsschluss (§ 536b BGB), keine vorbehaltlose Annahme trotz Kenntnis, kein Mieterverschulden.",
                "beweislast": "Vermieter"
            }
        ],
        "rechtsfolge": "Anspruch auf Mängelbeseitigung (§ 535 Abs. 1 Satz 2 BGB) sowie automatische Minderung der Miete gem. § 536 Abs. 1 BGB für die Dauer des Mangels."
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
    "BGB_626": {
        "norm": "§ 626 BGB",
        "title": "Außerordentliche fristlose Kündigung des Arbeitsverhältnisses",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Bestehen eines Arbeitsverhältnisses",
                "details": "Wirksamer Arbeitsvertrag zwischen Arbeitnehmer und Arbeitgeber.",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Wichtiger Grund an sich (§ 626 Abs. 1 BGB)",
                "details": "Schwerwiegender Verstoß gegen arbeitsvertragliche Pflichten (z.B. Vermögensdelikte, beharrliche Arbeitsverweigerung, schwerer Vertrauensbruch, Tätlichkeiten).",
                "beweislast": "Kündigender (in der Regel Arbeitgeber)"
            },
            {
                "merkmal": "Interessenabwägung und Ultima-Ratio-Prinzip",
                "details": "Fortsetzung des Arbeitsverhältnisses selbst bis zum Ablauf der ordentlichen Kündigungsfrist unzumutbar. Keine milderen Mittel wie Abmahnung oder Versetzung.",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Einhaltung der Zwei-Wochen-Ausschlussfrist (§ 626 Abs. 2 BGB)",
                "details": "Kündigungserklärung muss dem Kündigungsempfänger innerhalb von zwei Wochen ab Kenntnis der für die Kündigung maßgebenden Tatsachen zugehen.",
                "beweislast": "Kündigender"
            },
            {
                "merkmal": "Ordnungsgemäße Betriebsratsanhörung (§ 102 BetrVG)",
                "details": "Mitteilung der Kündigungsgründe an den Betriebsrat mit Frist von drei Tagen (falls ein Betriebsrat existiert).",
                "beweislast": "Arbeitgeber"
            }
        ],
        "rechtsfolge": "Sofortige Auflösung des Arbeitsverhältnisses mit Zugang der schriftlichen Kündigungserklärung (ex nunc)."
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
    },
    "OWIG_67": {
        "norm": "§ 67 OWiG",
        "title": "Einspruch gegen den Bußgeldbescheid",
        "tatbestandsmerkmale": [
            {
                "merkmal": "Erlass und wirksame Zustellung eines Bußgeldbescheides",
                "details": "Verwaltungsakt einer Bußgeldbehörde (§§ 65, 66 OWiG) mit Postzustellungsurkunde oder persönlicher Übergabe.",
                "beweislast": "Verwaltungsbehörde (Zustellungsurkunde)"
            },
            {
                "merkmal": "Statthaftigkeit und Form des Einspruchs (§ 67 Abs. 1 Satz 1 OWiG)",
                "details": "Schriftlich oder zur Niederschrift bei der erlassenden Verwaltungsbehörde.",
                "beweislast": "Betroffener"
            },
            {
                "merkmal": "Einhaltung der Einspruchsfrist (§ 67 Abs. 1 Satz 1 OWiG)",
                "details": "Einspruch innerhalb von zwei Wochen nach Zustellung eingegangen (Ereignisfrist gem. § 46 Abs. 1 OWiG i.V.m. § 43 StPO).",
                "beweislast": "Betroffener (Eingangsdatum bei Behörde)"
            },
            {
                "merkmal": "Beschwer und Postulationsfähigkeit",
                "details": "Betroffener ist Adressat des Bußgeldbescheides und durch die Festsetzung beschwert.",
                "beweislast": "Betroffener"
            }
        ],
        "rechtsfolge": "Hemmung der Rechtskraft des Bußgeldbescheides (§ 67 Abs. 1 Satz 2 OWiG), Überprüfung im behördlichen Zwischenverfahren (§ 69 OWiG) und ggf. gerichtliche Entscheidung durch das Amtsgericht."
    }
}

def analyze_subsumption(law: str, section: str) -> Dict[str, Any]:
    """
    Returns the structured subsumption model for a given norm,
    including individual elements of proof, factual requirements, and burden of proof.
    """
    sec_clean = section.replace('§', '').replace('Abs.', '').strip().replace(' ', '_')
    key = f"{law.upper()}_{sec_clean}"
    
    # Direct match
    if key in STATUTORY_BLUEPRINTS:
        return {
            "success": True,
            "blueprint": STATUTORY_BLUEPRINTS[key]
        }
        
    # Match without paragraph suffix or with prefix match
    base_sec = sec_clean.split('_')[0]
    base_key = f"{law.upper()}_{base_sec}"
    if base_key in STATUTORY_BLUEPRINTS:
        return {
            "success": True,
            "blueprint": STATUTORY_BLUEPRINTS[base_key]
        }
        
    for k, v in STATUTORY_BLUEPRINTS.items():
        if k.startswith(f"{base_key}_"):
            return {
                "success": True,
                "blueprint": v
            }
        
    return {
        "success": False,
        "message": f"Kein vordefinierter Subsumptions-Graph für {law} § {section} vorhanden. Bitte Gesetzestext via get_norm analysieren."
    }
