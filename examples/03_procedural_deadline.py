#!/usr/bin/env python3
"""
Example 03: Procedural Deadline Calculation under §§ 187-193 BGB & ZPO.
"""

from datetime import date
from german_legal_engine import LegalEngine

def main():
    print("=== Procedural Deadline Calculation ===")
    
    # Kündigung received on Friday, 02.10.2026.
    # 3-week statutory deadline for Kündigungsschutzklage (§ 4 KSchG).
    ereignis = date(2026, 10, 2)
    print(f"Zugang der Kündigung (Ereignistag): {ereignis.strftime('%d.%m.%Y')}")
    
    res = LegalEngine.compute_deadline(
        ereignis_datum=ereignis,
        dauer_wert=3,
        dauer_einheit="wochen",
        state="BY"
    )
    
    print(f"Fristbeginn gem. § 187 Abs. 1 BGB:     {res['frist_beginn']} (00:00 Uhr)")
    print(f"Reguläres Fristende gem. § 188 BGB:    {res['regulaeres_ende']}")
    print(f"Endgültiges Fristende gem. § 193 BGB:  {res['endgueltiges_ende']} (24:00 Uhr)")
    
    if res["shifted_by_193_bgb"]:
        print("\nFeiertags- oder Wochenendverschiebung:")
        for r in res["shift_reasons"]:
            print(f"  * {r}")
            
    print(f"\nOffizielle Urteilsstil-Zitation:\n{res['citation']}")

if __name__ == "__main__":
    main()
