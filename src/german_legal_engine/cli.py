"""
cli.py
Command Line Interface for the German Legal Engine (gle).
"""

import sys
import json
import argparse
from datetime import date
from .client import LegalEngine

def main():
    parser = argparse.ArgumentParser(
        prog="gle",
        description="German Legal Engine CLI: Sovereign Legal Research & Procedural Deadlines"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # norm
    norm_p = subparsers.add_parser("norm", help="Fetch authentic statutory text")
    norm_p.add_argument("law", help="Law abbreviation (e.g. BGB, ZPO, KSchG)")
    norm_p.add_argument("section", help="Paragraph or section number (e.g. 823, 253)")
    
    # search
    search_p = subparsers.add_parser("search", help="Search federal court case law (BGH, BAG, BVerfG)")
    search_p.add_argument("query", help="Keywords or legal search terms")
    search_p.add_argument("--limit", type=int, default=5, help="Max results")
    search_p.add_argument("--court", default=None, help="Filter by court (e.g. BGH, BAG)")
    
    # deadline
    dl_p = subparsers.add_parser("deadline", help="Calculate procedural deadline (§§ 187-193 BGB)")
    dl_p.add_argument("date", help="Trigger event date (YYYY-MM-DD)")
    dl_p.add_argument("value", type=int, help="Duration value (e.g. 2, 3)")
    dl_p.add_argument("unit", choices=["tage", "wochen", "monate"], help="Duration unit")
    dl_p.add_argument("--state", default="BY", help="German state code for public holidays (default: BY)")
    
    # subsumption
    sub_p = subparsers.add_parser("subsume", help="Get legal subsumption blueprint (Tatbestandsmerkmale)")
    sub_p.add_argument("law", help="Law abbreviation (e.g. BGB, KSchG)")
    sub_p.add_argument("section", help="Paragraph number (e.g. 823, 551, 1)")
    
    args = parser.parse_args()
    
    if args.command == "norm":
        res = LegalEngine.get_norm(args.law, args.section)
        if res.get("success"):
            print(f"\n=== {res['title']} ===")
            print(f"Quelle: {res.get('source_url', 'gesetze-im-internet.de')}\n")
            print(res["content_clean"])
        else:
            print(f"Error: {res.get('error')}")
            
    elif args.command == "search":
        res = LegalEngine.search_precedents(args.query, limit=args.limit, court=args.court)
        print(f"\nTreffer für '{args.query}':\n")
        for i, r in enumerate(res, 1):
            if "error" in r:
                print("Error:", r["error"])
                continue
            print(f"{i}. {r['citation']}")
            print(f"   {r['title']}\n")
            
    elif args.command == "deadline":
        try:
            d = date.fromisoformat(args.date)
            res = LegalEngine.compute_deadline(d, args.value, args.unit, args.state)
            print(f"\n=== Fristenberechnung gem. §§ 187-193 BGB ({args.state}) ===")
            print(f"Ereignisdatum:     {res['ereignis_datum']}")
            print(f"Fristbeginn:       {res['frist_beginn']} (00:00 Uhr)")
            print(f"Reguläres Fristende: {res['regulaeres_ende']}")
            print(f"Endgültiges Fristende: {res['endgueltiges_ende']} (24:00 Uhr)")
            if res['shifted_by_193_bgb']:
                print(f"Verschiebung:      JA gem. § 193 BGB")
                for s in res['shift_reasons']:
                    print(f"  - {s}")
            print(f"\n{res['citation']}\n")
        except Exception as e:
            print("Error calculating deadline:", e)
            
    elif args.command == "subsume":
        res = LegalEngine.get_subsumption_blueprint(args.law, args.section)
        if res.get("success"):
            bp = res["blueprint"]
            print(f"\n=== Subsumptions-Modell: {bp['norm']} ===")
            print(f"Titel: {bp['title']}\n")
            print("Tatbestandsmerkmale & Beweislast:")
            for m in bp["tatbestandsmerkmale"]:
                print(f"  [+] {m['merkmal']}")
                print(f"      Details:    {m['details']}")
                print(f"      Beweislast: {m['beweislast']}")
            print(f"\nRechtsfolge: {bp['rechtsfolge']}\n")
        else:
            print(res.get("message"))
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
