#!/usr/bin/env python3
"""
Example 04: Dual-System Architecture for Law Firms (Kanzleiprozesse).

Demonstrates the hybrid "System 1 + System 2" paradigm:
- System 1 (LLM / Semantic Agent): Parses unstructured mandate text, drafts pleadings.
- System 2 (German Legal Engine): Deterministischer Ground Truth Layer für
  1. Lokale PII-Anonymisierung (DSGVO Art. 5, keine Weitergabe sensibler Daten)
  2. Wortlautgetreuen Gesetzesabruf (ohne LLM-Halluzinationen)
  3. Mathematisch exakte Fristenberechnung gem. §§ 187-193 BGB mit lückenlosem Audit-Trail
  4. Strukturierte Subsumtion und gesetzliche Beweislastprüfung
"""

import json
from datetime import date
from german_legal_engine import LegalEngine

def simulate_system_1_mandate_parser(mandate_text: str) -> dict:
    """
    Simuliert System 1 (LLM Semantic Extraction):
    Extrahiert strukturierte Sachverhaltsmerkmale aus rohem Kanzleieingang.
    """
    # System 1 identifiziert aus dem Freitext das Ereignis und die Rechtsmaterie:
    return {
        "event_date": "2026-10-02", # Freitag, Zugang Kündigung
        "matter": "Arbeitsrecht",
        "action": "Kündigungsschutzklage",
        "governing_norm_law": "KSchG",
        "governing_norm_section": "4",
        "deadline_val": 3,
        "deadline_unit": "wochen",
        "state": "BY"
    }

def main():
    print("=" * 70)
    print("DEMO: System 1 (LLM Agent) + System 2 (German Legal Engine)")
    print("=" * 70)

    # 1. Roher, unstrukturierter Mandanteneingang mit sensiblen PII
    raw_mandate_email = """
    Sehr geehrter Herr Rechtsanwalt,
    ich, Max Mustermann, wohnhaft in der Leopoldstraße 42, 80802 München,
    habe von meinem Arbeitgeber am Freitag, den 02.10.2026, eine fristlose Kündigung erhalten.
    Mein Gehalt (IBAN DE89370400440532013000, max.mustermann@example.com) wurde nicht mehr gezahlt.
    Ich möchte mich unbedingt dagegen wehren. Was müssen wir tun und bis wann?
    """

    print("\n[Schritt 1] Unstrukturierter Mandanteneingang (Rohdaten):")
    print(raw_mandate_email.strip())

    # 2. System 2: Lokale DSGVO-Schutzschicht (PII Anonymisierung)
    print("\n[Schritt 2] System 2 Ground Truth: Lokale PII-Schwärzung gem. Art. 5 DSGVO...")
    sanitized_text = LegalEngine.anonymize_text(raw_mandate_email)
    print("Bereinigter Text für externe Weiterverarbeitung (Zero PII Leakage):")
    print(sanitized_text.strip())

    # 3. System 1: Semantische Analyse und Parametrisierung
    print("\n[Schritt 3] System 1: Semantische Extraktion von Anspruch und Fristparametern...")
    params = simulate_system_1_mandate_parser(sanitized_text)
    print(f"Erkannte Parameter: {params}")

    # 4. System 2: Deterministische Gesetzesprüfung (KSchG § 4)
    print(f"\n[Schritt 4] System 2: Wortlautgetreuer Abruf der Klagefrist (§ {params['governing_norm_section']} {params['governing_norm_law']})...")
    norm_res = LegalEngine.get_norm(params["governing_norm_law"], params["governing_norm_section"])
    if norm_res.get("success"):
        print(f"Amtlicher Wortlaut: {norm_res['title']}")
        print(norm_res["content_clean"][:280] + "...\n")

    # 5. System 2: Deterministische Fristenberechnung mit lückenlosem Audit-Trail
    print("[Schritt 5] System 2: Mathematische Fristenberechnung nach §§ 187-193 BGB...")
    ereignis = date.fromisoformat(params["event_date"])
    deadline_res = LegalEngine.compute_deadline(
        ereignis_datum=ereignis,
        dauer_wert=params["deadline_val"],
        dauer_einheit=params["deadline_unit"],
        state=params["state"]
    )

    print(f"Ereignistag:         {deadline_res['ereignis_datum']} (Freitag)")
    print(f"Fristbeginn:         {deadline_res['frist_beginn']} (Samstag, 00:00 Uhr gem. § 187 Abs. 1 BGB)")
    print(f"Reguläres Fristende: {deadline_res['regulaeres_ende']} (Freitag, 24:00 Uhr gem. § 188 Abs. 2 BGB)")
    print(f"Endgültiges Fristende:{deadline_res['endgueltiges_ende']} (24:00 Uhr)")
    print(f"Verschiebung § 193:  {'Ja' if deadline_res['shifted_by_193_bgb'] else 'Nein'}")
    print(f"Offizielle Zitation: {deadline_res['citation']}")

    print("\nLückenloser gesetzlicher Audit-Trail (System 2 Verifikation):")
    for step in deadline_res["audit_trail"]:
        print(f"  [{step['rule']}] Schritt {step['step']}: {step['title']}")
        print(f"    -> {step['description']}")

    # 6. System 2: Strukturierte Subsumtion für Klagebegründung (§ 1 KSchG)
    print("\n[Schritt 6] System 2: Gesetzliche Tatbestandsmerkmale & Beweislastverteilung:")
    subsume_res = LegalEngine.get_subsumption_blueprint("KSchG", "1")
    if subsume_res.get("success"):
        bp = subsume_res["blueprint"]
        print(f"Norm: {bp['norm']} - {bp['title']}")
        for m in bp["tatbestandsmerkmale"][:2]:
            print(f"  * Merkmal: {m['merkmal']}")
            print(f"    Beweislast: {m['beweislast']}")

    # 7. Synthese: Zuverlässiges, halluzinationsfreies Fristenkontrollblatt
    print("\n[Schritt 7] Finales Fristenkontrollblatt für das Kanzlei-DMS:")
    print("-" * 50)
    print(f"AKTE:              Arbeitsrecht / Kündigungsschutz")
    print(f"MANDANT:           [DSGVO-GESCHWÄRZT / LOKAL VORHANDEN]")
    print(f"KLAGEFRIST:        3 Wochen (§ 4 Satz 1 KSchG)")
    print(f"FRISTABLAUF:       {deadline_res['endgueltiges_ende']} um 24:00 Uhr")
    print(f"PRÜFUNGSERGEBNIS:  Mathematisch verifiziert (GLE Engine v1.0)")
    print(f"AUDIT-STATUS:      Vollständig nachvollziehbar gem. §§ 187-193 BGB")
    print("-" * 50)
    print("\nErgebnis: Vollständige Trennung von semantischer Modell-Intelligenz (System 1)")
    print("und deterministischer, rechtsverbindlicher Ausführung (System 2).\n")

if __name__ == "__main__":
    main()
