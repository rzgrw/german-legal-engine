# Rechtlicher Rahmen, Urheberrecht & DSGVO-Compliance (GLE)

> **Dokumentenstatus:** Offizielle Compliance- und Rechtsrichtlinie für die Nutzung der German Legal Engine (GLE).  
> **Rechtsraum:** Bundesrepublik Deutschland / Europäische Union (DSGVO).

---

## 1. Leitbild & Grundsatz

Die **German Legal Engine (GLE)** dient als deterministische, quellenintegrierte Recherche- und Fristen-Runtime für KI-Agenten und Juristen. Im deutschen Rechts- und Kanzleialltag stehen anwaltliche Sorgfaltspflichten (*§ 43a BRAO*), berufsrechtliche Verschwiegenheit (*§ 203 StGB*) und Haftungsvermeidung (*§ 280 Abs. 1 BGB*) an oberster Stelle. 

Dieses Dokument legt verbindlich dar, wie die Engine die Vorgaben des deutschen Urheberrechtsgesetzes (*UrhG*), des Gesetzes gegen den unlauteren Wettbewerb (*UWG*) und der Datenschutz-Grundverordnung (*DSGVO*) technisch und konzeptionell einhält.

---

## 2. Amtliche Werke & Urheberrechtsschutz (§ 5 UrhG)

### 2.1 Gemeinfreiheit amtlicher Texte gem. § 5 Abs. 1 UrhG
Gemäß **§ 5 Abs. 1 UrhG** genießen Gesetze, Verordnungen, amtliche Erlasse und Bekanntmachungen sowie Entscheidungen und amtlich verfasste Leitsätze von Gerichten **keinen urheberrechtlichen Schutz**. 
- Die GLE ruft Gesetzestexte des Bundes (*BGB, ZPO, KSchG, StGB, AufenthG etc.*) direkt aus dem amtlichen Informationsportal *gesetze-im-internet.de* ab.
- Gerichtsentscheidungen werden direkt von *Rechtsprechung im Internet* (*BGH, BAG, BVerfG*) sowie der bayerischen Staatskanzlei (*gesetze-bayern.de*) bezogen.
- Das Abrufen, Normalisieren und Bereitstellen dieser amtlichen Volltexte als Entscheidungsgrundlage für KI-Modelle ist urheberrechtlich uneingeschränkt zulässig.

### 2.2 Strikter Ausschluss privater Normen gem. § 5 Abs. 3 UrhG
Private Regelwerke und technische Standards (*wie DIN-, EN-, ISO- oder VDI-Normen*) werden **nicht** als amtliche Werke privilegiert, selbst wenn Gesetze auf sie verweisen (*§ 5 Abs. 3 UrhG*).
- Die German Legal Engine bindet **keine** kostenpflichtigen oder urheberrechtlich geschützten Normen-Datenbanken (z. B. Nautos / Beuth Verlag) ein.
- Urheberrechtlich geschützte juristische Fachliteratur, Zeitschriftenaufsätze und Verlagskommentare sind ausdrücklich von der automatisierten Volltexterfassung ausgeschlossen.

---

## 3. Schutz von Datenbanken (§§ 87a, 87b UrhG) & Text and Data Mining (§ 44b UrhG)

### 3.1 Keine unbefugte Datenbankvervielfältigung
Portale wie *gesetze-im-internet.de* oder *gesetze-bayern.de* genießen für ihre Systematik, Metadaten und Indexstrukturen den Schutz als Datenbankhersteller gem. **§§ 87a, 87b UrhG**.
- **On-Demand-Prinzip:** Die GLE betreibt kein massenhaftes, systematisches "Crawling" oder Spiegeln ganzer Urteilsdatenbanken auf eigene Server.
- Alle Abfragen erfolgen rein punktuell, anlassbezogen und unmittelbar auf Anforderung des Anwenders für eine konkrete rechtliche Prüfungsaufgabe.
- Es findet keine unautorisierte kommerzielle Weiterverbreitung geschützter Datenbankstrukturen Dritter statt.

### 3.2 Flüchtige Speicherung gem. § 44b UrhG
Soweit Abrufe unter die Schranke des Text and Data Mining (**§ 44b UrhG**) fallen, fordert Abs. 2 Satz 2 die Löschung der Vervielfältigungen, sobald sie für den Zweck nicht mehr erforderlich sind:
- Die GLE verzichtet auf persistente Offline-Datenbanken fremder Portale.
- Temporäre Caches werden strikt sitzungsgebunden (*in-memory / transient*) gehalten und nach Abschluss des Vorgangs verworfen.
- Vorhandene maschinenlesbare Nutzungsvorbehalte und Sperren (*robots.txt, HTTP-Header gem. § 44b Abs. 3 UrhG*) werden respektiert.

---

## 4. Quellenintegrität & Nachweiserfordernis (Source Provenance)

Um Halluzinationen und Fehlzitate in gerichtlichen Schriftsätzen auszuschließen, trennt die GLE streng zwischen amtlicher Primärquelle und analytischer Hilfestellung:

1. **Amtliche Primärdaten (`is_official_verbatim: True`):**  
   Volltexte von Gesetzen und Entscheidungen werden wortlautgetreu wiedergegeben. Jedes Ergebnisobjekt enthält:
   - `source_name`: Offizielle Bezeichnung des Primärregisters
   - `source_url`: Direkte, unveränderliche Verlinkung zur Fundstelle
   - `retrieved_at`: Präziser Abrufzeitstempel (ISO 8601 UTC)
2. **Analytische Subsumtions-Graphen (`is_official_verbatim: False`):**  
   Strukturierte Tatbestandsmerkmale und Beweislastverteilungen sind explizit als juristische Struktur- und Arbeitshilfen gekennzeichnet. Sie stellen keinen amtlichen Gesetzestext dar und erfordern die eigenverantwortliche Prüfung durch den Rechtsanwender.
3. **Redaktionelle Leitsätze:**  
   Leitsätze aus Rechtsprechungsdatenbanken, die nicht vom Spruchkörper selbst, sondern von Verlags- oder Portalredaktionen stammen (*redaktionelle Leitsätze*), werden gesondert ausgewiesen.

---

## 5. Datenschutz (DSGVO) & anwaltliche Verschwiegenheit

### 5.1 Local-First-Architektur (Keine zentrale Verarbeitung)
- Die German Legal Engine wird als Open-Source-Software lokal oder in der gesicherten Kanzleiinfrastruktur des Nutzers betrieben.
- Es gibt keinen zentralen Telemetrie- oder Proxy-Server von Agentiqa.
- Suchanfragen, Mandantendaten, IP-Adressen und Prompts verbleiben vollständig in der Hoheit des Anwenders. Ein Vertrag zur Auftragsverarbeitung (*Art. 28 DSGVO*) mit den Maintainern ist mangels Datenzugriffs weder erforderlich noch einschlägig.

### 5.2 Datenminimierung und PII-Redaktion (Art. 5 DSGVO)
Zur Unterstützung von Berufsgeheimnisträgern (*§ 203 StGB*) und zur Wahrung des Grundsatzes der Datenminimierung (*Art. 5 Abs. 1 lit. c DSGVO*) stellt das Framework die Funktion `anonymize_legal_text` bereit:
- Automatische Erkennung und Schwärzung von sensiblen personenbezogenen Daten (IBANs, Steuernummern, Anschriften, Telefonnummern, E-Mail-Adressen).
- Ermöglicht das Bereinigen von Sachverhalten vor der Weitergabe an LLM-Inferenzschnittstellen.

---

## 6. Haftungsausschluss

Die German Legal Engine ist ein juristisches Assistenz- und Recherchewerkzeug. Die Nutzung entbindet den handelnden Volljuristen nicht von der eigenständigen berufsrechtlichen Pflicht zur inhaltlichen und prozessualen Überprüfung von Fristen, Normenständen und Urteilszitaten vor Einreichung bei Gericht (*§ 43a Abs. 1, 2 BRAO*).
