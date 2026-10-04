#!/usr/bin/env python3
"""
Example 05: Laya System 1 Legal Triage & Decision Layer.
Integrates Laya (https://brainfunctioncollapse.com/laya) with the German Legal Engine.

Demonstrates:
1. Fast local classification (Rechtsgebiet, Dringlichkeit, Fristrisiko) in ~20-30 ms.
2. Zero data leakage: PII is anonymized locally before processing.
3. Seamless cascade into German Legal Engine Ground Truth (Norms & Deadlines).
"""

from german_legal_engine import LegalEngine
from german_legal_engine.triage import LegalTriage

def main():
    print("=" * 70)
    print("DEMO: Laya Non-Generative Decision Model (System 1) + German Legal Engine")
    print("Referenz: https://brainfunctioncollapse.com/laya")
    print("=" * 70)

    # 1. Typische Kanzleieingänge (unstrukturiert)
    inquiries = [
        {
            "title": "Mandant A: Fristlose Kündigung im Arbeitsrecht",
            "text": "Guten Tag, ich habe am Freitag, 02.10.2026, eine fristlose Kündigung erhalten. Mein Arbeitgeber verweigert die Weiterbeschäftigung. Müssen wir sofort Klage einreichen?",
            "state": "BY"
        },
        {
            "title": "Mandant B: Einbehaltene Mietkaution und Mängel",
            "text": "Mein ehemaliger Vermieter zahlt seit 7 Monaten die Mietkaution in Höhe von 2.400 Euro nicht zurück, obwohl das Übergabeprotokoll mängelfrei war.",
            "state": "NW"
        },
        {
            "title": "Mandant C: Anhörungsbogen wegen Geschwindigkeitsüberschreitung",
            "text": "Ich habe einen Bußgeldbescheid mit 1 Monat Fahrverbot erhalten, Datum des Bescheids ist der 28.09.2026. Lohnt sich ein Einspruch?",
            "state": "BW"
        }
    ]

    for item in inquiries:
        print(f"\n--- {item['title']} ---")
        print(f"Eingangstext: \"{item['text']}\"")
        
        # Triage via LegalEngine (nutzt Laya multilingual oder robusten Fallback)
        triage = LegalEngine.triage_mandate(item["text"], state=item["state"])
        
        print(f"\n[Laya System 1 Entscheidungsergebnis]:")
        print(f"  * Rechtsgebiet:         {triage['domain'].upper()} (Konfidenz: {triage['domain_confidence']:.2f})")
        print(f"  * Dringlichkeits-Score: {triage['urgency_score']:.1f} / 2.0")
        print(f"  * Fristablauf-Risiko:   {triage['deadline_risk_prob']:.2f}")
        print(f"  * Anwaltliche Eilprüfung: {'SOFORT ERFORDERLICH' if triage['requires_escalation'] else 'Reguläre Kanzleiroutine'}")
        
        if triage.get("detected_event_dates"):
            print(f"  * Erkannte Daten:       {', '.join(triage['detected_event_dates'])}")
            
        print("\n[Automatisch verknüpfte German Legal Engine Normen]:")
        for norm in triage["suggested_statutory_norms"]:
            print(f"  -> {norm['norm']}: {norm['title']} ({norm['tatbestandsmerkmale_count']} Tatbestandsmerkmale)")

    print("\n" + "=" * 70)
    print("Vorteil für Kanzleien:")
    print("- Vorhersagbare, typisierte Entscheidungen ohne teure LLM-Aufrufe")
    print("- Latenz: ca. 20-35 ms auf lokaler Hardware (CPU/MPS)")
    print("- Kein PII-Leakage: Daten verlassen niemals die Kanzlei-Infrastruktur")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
