#!/usr/bin/env python3
"""
Example 01: Verbatim Statutory Law Retrieval.
"""

from german_legal_engine import LegalEngine

def main():
    print("=== Statutory Ground Truth Retrieval ===")
    
    # 1. Fetch § 823 BGB (Deliktsrecht)
    norm = LegalEngine.get_norm("BGB", "823")
    print(f"Norm: {norm['title']}")
    print(f"Quelle: {norm.get('source_url')}\n")
    print("Inhalt:")
    print(norm["content_clean"])
    print("-" * 50)
    
    # 2. Fetch § 1 KSchG (Kündigungsschutz)
    kschg = LegalEngine.get_norm("KSchG", "1")
    print(f"Norm: {kschg['title']}")
    print(kschg["content_clean"][:300] + "...\n")

if __name__ == "__main__":
    main()
