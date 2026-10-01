# AGENT_INSTRUCTIONS.md - Technisches Übergabebriefing für KI-Entwickleragenten

> **Zielgruppe:** Autonome Coding-Agenten (Claude Code / OpenCode / Codex / Hermes).  
> **Ziel:** Weiterentwicklung, Ausbau und Härtung der **German Legal Engine (GLE)** zum führenden Open-Source-MCP-Server für das deutsche Rechtssystem.

---

## 🧭 Leitphilosophie des Projekts

Dieses Projekt ist **kein generischer LLM-Wrapper**. Es handelt sich um eine **deterministische Rechts-Runtime**, die lokal oder on-premise läuft und als unbestechliche Tatsachengrundlage (*Ground Truth*) für juristische Denkprozesse dient.

Im deutschen Zivil- und Prozessrecht (*BGB*, *ZPO*, *ArbGG*) führen halluzinierte Fristen, erfundene Aktenzeichen oder fehlerhafte Paragrafenzitate unmittelbar zur anwaltlichen Berufshaftung (*§ 280 BGB i.V.m. BRAO*). Jede Ausgabe dieses Systems muss strikt gegen amtliche Bundes- und Landesregister überprüfbar sein.

---

## 📁 Code-Topologie und Modulübersicht

| Datei | Zuständigkeit | Wichtige Funktionen und Klassen |
|---|---|---|
| `src/german_legal_engine/norms.py` | Amtlicher Gesetzesabruf | Extrahiert und parst Gesetze direkt von *gesetze-im-internet.de* ohne externe Node/NPM-Abhängigkeiten. Unterstützt BGB, ZPO, KSchG, StGB, RVG usw. |
| `src/german_legal_engine/deadlines.py` | Prozessuale Fristenmathematik | Strikte Umsetzung der §§ 187 Abs. 1, 188 Abs. 2, 193 BGB. Berechnet Ostern via Butcher-Algorithmus und berücksichtigt Feiertagsgesetze aller 16 Bundesländer. |
| `src/german_legal_engine/subsumption.py` | Strukturierte Tatbestandsmodelle | Zerlegt Normen in `Tatbestandsmerkmale`, Tatsachenanforderungen und gesetzliche `Beweislast` (Kläger versus Beklagter). |
| `src/german_legal_engine/case_law.py` | Höchstrichterliche Rechtsprechung | Durchsucht *Rechtsprechung im Internet* (RII) für BGH, BAG und BVerfG. Formatiert Zitationen im Urteilsstil. |
| `src/german_legal_engine/sanitizer.py` | Schriftsatz- und Zitieregeln | Erzwingt die strikte **Zero-Dashes-Regel** (Umwandlung von `—` und `–` in Kommata/Doppelpunkte) und BGH-konforme Zitate. |
| `src/german_legal_engine/client.py` | Einheitliches Python-SDK | Klasse `LegalEngine` mit statischen High-Level-Methoden für einfache Einbindung in Python-Projekte. |
| `src/german_legal_engine/server.py` | FastMCP-Server | Vollständige MCP-Implementierung mit 5 Werkzeugen für Claude Desktop, Cursor etc. (stdio/sse). |
| `src/german_legal_engine/cli.py` | Terminal-Interface | CLI-Befehl `gle` mit Unterbefehlen: `gle norm`, `gle search`, `gle deadline`, `gle subsume`. |

---

## 🛠️ Roadmap und nächste Arbeitspakete (Backlog)

Folgende Aufgaben sind vom nachfolgenden Agenten prioritär zu bearbeiten:

### Priorität 1: Erweiterung der Subsumtions-Blueprints (`subsumption.py`)
Erfolgreich implementierte Basis-Graphen:
* [x] `§ 823 Abs. 1 BGB` (Unerlaubte Handlungen)
* [x] `§ 280 Abs. 1 BGB` (Schadensersatz wegen Pflichtverletzung)
* [x] `§ 314 BGB` (Kündigung von Dauerschuldverhältnissen aus wichtigem Grund)
* [x] `§ 535 Abs. 1 Satz 2 BGB` (Mängelbeseitigung und Minderung im Mietrecht)
* [x] `§ 551 BGB` (Mietsicherheiten / Kaution)
* [x] `§ 626 BGB` (Außerordentliche fristlose Kündigung im Arbeitsrecht)
* [x] `§ 1 KSchG` (Kündigungsschutz)
* [x] `§ 67 OWiG` (Einspruch gegen den Bußgeldbescheid)

**Nächste Erweiterungen:** Weitere spezifische Anspruchsgrundlagen (z. B. § 812 BGB Bereicherungsrecht, § 437 BGB kaufrechtliche Gewährleistung).

### Priorität 2: Eigener nativer Scraper für bayerische Gerichte (`gesetze-bayern.de`)
* [x] Vollständig autark in Python in `bayern.py` implementiert (ohne Node/NPM).
* [x] Robuste Session-Verwaltung mit automatischer Token-Erneuerung (`__RequestVerificationToken`).
* [x] Entscheidungsabruf für AG München, LG München I und II, OLG München, BayObLG, BayVerfGH etc. inklusive Leitsätzen, Tenor, Tatbestand und `[Rn. X]`.
* [x] Vollständige Entkopplung von `case_law.py` von externen Node-Paketen.

### Priorität 3: Lokaler SQLite-Cache & Offline-Modus
Rechtsanwälte arbeiten häufig unterwegs im Zug oder benötigen Latenzen im Sub-Millisekundenbereich.  
**Aufgabe:** Integration eines lokalen Caches (`~/.cache/german_legal_engine/cache.db`) mit einer Time-to-Live (TTL) von 30 Tagen für abgerufene Paragrafen und Suchanfragen.

### Priorität 4: Gesetzlicher RVG-Gebührenrechner (§ 13 RVG / VV RVG)
Erstellung eines Moduls `rvg.py` zur exakten Berechnung der Rechtsanwaltsgebühren nach Gegenstandswert:
* Nr. 2300 VV RVG (Geschäftsgebühr, Rahmen 0,5 bis 2,5, Regelsatz 1,3)
* Nr. 3100 VV RVG (Verfahrensgebühr I. Instanz, 1,3)
* Nr. 3104 VV RVG (Terminsgebühr, 1,2)
* Nr. 1000 VV RVG (Einigungsgebühr, 1,5 bzw. 1,0)
* Nr. 7002 VV RVG (Auslagenpauschale für Post und Telekommunikation, max. 20,00 Euro)
* Nr. 7008 VV RVG (Umsatzsteuer 19 Prozent)

---

## 🧪 Richtlinien für Tests und Stil

1. Vor jedem Commit alle Unittests ausführen:
   ```bash
   PYTHONPATH=src python3 -m unittest discover tests
   ```
2. **Zero-Dashes-Regel einhalten:** Niemals Em-Dashes (`—`) oder En-Dashes (`–`) in Ausgabetexten, Tests oder Beispielen verwenden.
3. **Urteilsstil:** Begründungen und Zitate müssen der anwaltlichen Zivilprozesspraxis entsprechen.

*Gutes Gelingen! Machen wir deutsches Recht deterministisch und maschinenlesbar.*
