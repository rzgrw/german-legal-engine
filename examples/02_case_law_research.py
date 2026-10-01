#!/usr/bin/env python3
"""
Example 02: Searching Federal Court Case Law (BGH, BAG).
"""

from german_legal_engine import LegalEngine

def main():
    print("=== Case Law Precedents Search ===")
    query = "Mietkaution Rückzahlung Einbehalt"
    print(f"Suche nach: '{query}'...")
    
    results = LegalEngine.search_precedents(query, limit=3)
    for i, r in enumerate(results, 1):
        if "error" in r:
            print("Error:", r["error"])
            continue
        print(f"\n[{i}] {r['citation']}")
        print(f"    Titel: {r['title']}")
        print(f"    DocId: {r['doc_id']}")

if __name__ == "__main__":
    main()
