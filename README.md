# German Legal Engine (GLE) ⚖️

> **Souveräne juristische Recherche-, Subsumtions- und Fristen-Engine für autonome KI-Agenten**  
> *Souveräne Open-Source-Distribution von Agentiqa*

[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Spezifikation 1.0](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)
[![Zero Dashes](https://img.shields.io/badge/Stil-Zero--Dashes-green.svg)](https://github.com/rzgrw/german-legal-engine)

---

## 🎯 Vision und Zweck

Bestehende Legal-Tech-Suchwerkzeuge und MCP-Wrapper für deutsches Recht (wie z. B. `german-legal-mcp`) agieren primär als **unstrukturierte Text-Scraper**: Sie liefern unstrukturierte 40-seitige Urteilsprotokolle zurück, ohne ein Verständnis für **juristische Subsumtion**, **Beweislastverteilung** oder **prozessuale Fristenberechnung** mitzubringen.

Die **German Legal Engine (GLE)** wurde von praktizierenden Rechtsanwälten und KI-Systemarchitekten von Grund auf konzipiert, um KI-Agenten im deutschen Rechtsraum eine verlässliche Entscheidungs- und Recherchebasis (*Ground Truth*) bereitzustellen:

1. **Deterministischer Normenabruf (Gesetzeswahrheit):** Wortlautgetreuer Abruf von Bundesgesetzen (BGB, ZPO, KSchG, StGB, RVG, HGB, etc.) direkt über *gesetze-im-internet.de* ohne Halluzinationen.
2. **Strukturierte Subsumtions-Modelle (Tatbestands-Graphen):** Zerlegung von Gesetzesnormen in konkrete Tatbestandsmerkmale, Tatsachenanforderungen und gesetzliche Beweislastverteilung (Kläger versus Beklagter).
3. **Mathematische Fristen-Engine (§§ 187–193 BGB & ZPO):** Exakte Berechnung zivil- und arbeitsgerichtlicher Fristen (Ereignistag, Fristbeginn, Fristende) inklusive automatischer Verschiebung bei Wochenenden und Feiertagen aller 16 Bundesländer (*Feiertagsgesetze*).
4. **Authentische Rechtsprechung (RII-Integration):** Volltextsuche und zitiersichere Nachweise höchstrichterlicher Entscheidungen (BGH, BAG, BVerfG, BVerwG) mit gezielter Randnummern-Extraktion (`[Rn. X]`).
5. **Einhaltung anwaltlicher Schriftsatzstandards (Zero-Dashes & Urteilsstil):** Automatische Bereinigung störender Gedankenstriche (`—`, `–`) in prozessual saubere Zitiersyntax.

---

## 🏗️ Architekturübersicht

```text
german-legal-engine/
├── README.md                  # Vollständige Dokumentation in deutscher Sprache
├── AGENT_INSTRUCTIONS.md      # Technisches Briefing & Entwicklungsleitfaden für KI-Agenten
├── pyproject.toml             # Modernes Packaging via Hatchling / pip / uv
├── LICENSE                    # MIT-Lizenz
├── src/
│   └── german_legal_engine/
│       ├── __init__.py        # Öffentliche API-Exporte
│       ├── client.py          # Einheitliches Python-SDK (LegalEngine)
│       ├── server.py          # FastMCP-Server (stdio und sse) für Claude Desktop, Cursor etc.
│       ├── norms.py           # Autarker Normen-Parser für gesetze-im-internet.de
│       ├── case_law.py        # Rechtsprechungs-Client für BGH, BAG, BVerfG (100% Python)
│       ├── bayern.py          # Nativer Scraper für bayerische Gerichte (gesetze-bayern.de)
│       ├── subsumption.py     # Subsumtions-Blueprints (Merkmale & Beweislast)
│       ├── deadlines.py       # Exakte Fristenmathematik gem. §§ 187-193 BGB
│       ├── sanitizer.py       # Zero-Dashes Bereinigung & BGH-Zitierweise
│       └── cli.py             # Komfortables Terminal-Tool (gle)
├── tests/
│   ├── test_deadlines.py      # BGB-Fristen- und Feiertagstests
│   ├── test_subsumption.py    # Subsumtions- und Bereinigungstests
│   ├── test_case_law.py       # Rechtsprechungs- und Bayern-Tests
│   └── test_norms.py          # Gesetzesabruf- und Slug-Tests
└── examples/
    ├── 01_statutory_lookup.py # Gesetzesabruf in der Praxis
    ├── 02_case_law_research.py # Recherche von Leitentscheidungen
    └── 03_procedural_deadline.py # Fristenberechnung mit Feiertagsprüfung
```

---

## 🚀 Schnellstart

### Installation

```bash
# Repository klonen und im Editable-Modus installieren
git clone https://github.com/rzgrw/german-legal-engine.git
cd german-legal-engine
pip install -e .
```

---

### 1. Terminal-Nutzung über die CLI (`gle`)

Das mitgelieferte CLI-Werkzeug `gle` ermöglicht die sofortige Abfrage direkt im Terminal:

```bash
# 1. Gesetzestext wortlautgetreu abrufen (z. B. § 823 BGB, § 81 AufenthG)
gle norm BGB 823

# 2. Rechtsprechung durchsuchen (Bundesgerichte + bayerische Gerichte)
gle search "Mietkaution Rückzahlung" --limit 3 --source ALL

# 3. Volltext einer Entscheidung abrufen
gle decision Y-300-Z-BECKRS-B-2021-N-30750

# 4. Prozessuale Notfrist berechnen (§§ 187-193 BGB)
# Kündigungszugang am 03.10.2026 + 1 Woche Frist in Bayern (BY):
# Fällt regulär auf Samstag, den 10.10. -> automatische Verschiebung auf Montag, den 12.10.2026!
gle deadline 2026-10-03 1 wochen --state BY

# 5. Tatbestandsmerkmale und Beweislast analysieren
gle subsume BGB 280
```

---

### 2. Einbindung als Python-SDK

```python
from datetime import date
from german_legal_engine import LegalEngine

# 1. Gesetzliche Norm abrufen
norm = LegalEngine.get_norm("BGB", "551")
print(norm["title"])
print(norm["content_clean"])

# 2. Frist berechnen (inklusive Feiertagsverschiebung)
frist = LegalEngine.compute_deadline(
    ereignis_datum=date(2026, 10, 3),
    dauer_wert=1,
    dauer_einheit="wochen",
    state="BY"
)
print(frist["citation"])
# Ausgabe: "Fristablauf am 12.10.2026 um 24:00 Uhr gem. §§ 187 Abs. 1, 188 Abs. 2, 193 BGB"

# 3. Präzedenzfälle recherchieren
urteil = LegalEngine.search_precedents("Kündigungsschutz Wartezeit", limit=2)
for u in urteil:
    print(f"- {u['citation']}: {u['title']}")
```

---

### 3. Model Context Protocol (MCP) Konfiguration

Die Engine stellt einen standardkonformen MCP-Server bereit, der sich nahtlos in **Claude Desktop**, **Claude Code**, **Cursor**, **OpenCode** und **Hermes Agent** einklinkt.

#### Konfiguration in Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "german-legal-engine": {
      "command": "python3",
      "args": ["-m", "german_legal_engine.server"]
    }
  }
}
```

#### Bereitgestellte MCP-Tools:
* `get_norm(law, section)`: Liefert den amtlichen Volltext der gesuchten Rechtsnorm (Bund und Länder).
* `search_precedents(query, limit, court)`: Durchsucht die amtliche Datenbank *Rechtsprechung im Internet* (BGH, BAG, BVerfG).
* `compute_deadline(ereignis_datum, dauer_wert, dauer_einheit, state)`: Mathematisch exakte Fristenberechnung gem. §§ 187–193 BGB mit Feiertagskontrolle.
* `get_subsumption_blueprint(law, section)`: Liefert strukturierte Tatbestandsmerkmale mit zugehöriger Darlegungs- und Beweislast.
* `prepare_pleading_dossier(norms, query)`: Erzeugt einen fertigen, zitatgesicherten Rechercheblock für Klageschriften und Schriftsätze.

---

## ⚖️ Rechtlicher Rahmen & Compliance (§ 5 UrhG & DSGVO)

Die German Legal Engine wurde unter strikter Beachtung des deutschen Urheber- und Datenschutzrechts konzipiert:

1. **Amtliche Werke gem. § 5 Abs. 1 UrhG:** Die Engine ruft ausschließlich Gesetze, Verordnungen und gerichtliche Entscheidungen aus amtlichen Bundes- und Landesquellen ab. Diese genießen als amtliche Werke keinen urheberrechtlichen Schutz.
2. **Keine proprietären Normen oder Literatur:** Das Framework verzichtet bewusst auf die Einbindung privater DIN/ISO-Normen (Ausschluss des § 5 Abs. 3 UrhG) oder urheberrechtlich geschützter Sekundärliteratur.
3. **Schutz von Datenbankrechten (§§ 87a, 87b UrhG):** Kein massenhaftes systematisches Scraping oder unautorisiertes Spiegeln fremder Datenbanken. Die Abfragen erfolgen on-demand als punktuelle Referenzrecherchen mit direkter Quellenverlinkung (*Source Provenance*).
4. **Datenschutz durch lokale Ausführung (DSGVO):** Die Engine läuft als lokale Open-Source-Runtime on-premise auf dem Rechner des Nutzers. Es existiert kein zentraler Server, der Mandantendaten, IP-Adressen oder vertrauliche Suchanfragen speichert oder verarbeitet.

---

## 🏛️ Qualitätssicherung & Tests

Das Testset prüft die exakte Einhaltung der gesetzlichen Fristenlogik und Bereinigungsregeln:

```bash
# Tests ausführen
python3 -m unittest discover tests
```

---

## 📄 Lizenz

Dieses Projekt steht unter der freien **MIT-Lizenz**.  
Copyright (c) 2026 Agentiqa Core Team.
