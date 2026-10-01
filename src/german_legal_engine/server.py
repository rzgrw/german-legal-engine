"""
server.py
Model Context Protocol (MCP) Server for the German Legal Engine.
Compatible with Claude Desktop, Claude Code, Cursor, OpenCode, and Hermes Agent.
100% Pure Python - Zero Node/NPM dependencies.
"""

import sys
import json
from datetime import date
from typing import Optional, List

from mcp.server.mcpserver import MCPServer
from .client import LegalEngine

server = MCPServer("German Legal Engine", version="1.0.0")

@server.tool(description="Retrieve official, verbatim German federal or state statutory law (BGB, ZPO, KSchG, StGB, RVG, AufenthG, etc.) directly from official government repositories.")
def get_norm(law: str, section: str) -> str:
    """Retrieve authentic statutory text. law: e.g. 'BGB', 'ZPO', 'KSchG', 'AufenthG'. section: e.g. '823', '253', '1', '81'."""
    res = LegalEngine.get_norm(law, section)
    return json.dumps(res, ensure_ascii=False, indent=2)

@server.tool(description="Search authentic German court case law: federal courts (BGH, BAG, BVerfG, BVerwG, BFH) via Rechtsprechung im Internet and Bavarian courts (AG/LG/OLG München) via gesetze-bayern.de.")
def search_precedents(
    query: str,
    limit: int = 5,
    court: Optional[str] = None,
    source: str = "ALL"
) -> str:
    """Search court case law. query: legal keywords. court: optional court filter. source: 'ALL', 'BUND' (federal), or 'BY' (Bavaria)."""
    res = LegalEngine.search_precedents(query, limit=limit, court=court, source=source)
    return json.dumps(res, ensure_ascii=False, indent=2)

@server.tool(description="Retrieve the authentic full text and Randnummern of a court decision by document ID.")
def get_decision(doc_id: str) -> str:
    """Retrieve decision text. doc_id: e.g. 'jb-KORE...' or 'Y-300-Z-BECKRS-B-...'."""
    res = LegalEngine.get_decision(doc_id)
    return json.dumps(res, ensure_ascii=False, indent=2)

@server.tool(description="Calculate German procedural deadlines under §§ 187-193 BGB and ZPO with weekend and statutory holiday shifting across all 16 German states.")
def compute_deadline(
    ereignis_datum: str,
    dauer_wert: int,
    dauer_einheit: str = "wochen",
    state: str = "BY"
) -> str:
    """Compute procedural deadline. ereignis_datum: 'YYYY-MM-DD'. dauer_wert: int. dauer_einheit: 'tage', 'wochen', 'monate', 'jahre'. state: German state code (e.g. 'BY', 'NW', 'BE')."""
    try:
        d = date.fromisoformat(ereignis_datum)
        res = LegalEngine.compute_deadline(d, dauer_wert, dauer_einheit, state)
        return json.dumps(res, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@server.tool(description="Retrieve directed legal subsumption blueprints: Tatbestandsmerkmale, factual details, burden of proof (Beweislast), and statutory legal consequences.")
def get_subsumption_blueprint(law: str, section: str) -> str:
    """Retrieve structured legal elements. law: e.g. 'BGB', 'KSchG', 'OWiG'. section: e.g. '823', '280', '314', '535', '551', '626', '1', '67'."""
    res = LegalEngine.get_subsumption_blueprint(law, section)
    return json.dumps(res, ensure_ascii=False, indent=2)

@server.tool(description="Prepare an executive, citation-grounded legal context dossier for drafting court pleadings or legal briefs without hallucinations or dashes.")
def prepare_pleading_dossier(norms: List[List[str]], query: str) -> str:
    """Prepare legal dossier. norms: list of [law, section] pairs e.g. [['BGB', '823'], ['BGB', '249']]. query: case law search query."""
    tuple_norms = [(item[0], item[1]) for item in norms if len(item) >= 2]
    res = LegalEngine.prepare_dossier_context(tuple_norms, query)
    return res


def main():
    import argparse
    parser = argparse.ArgumentParser(description="German Legal Engine MCP Server (100% Pure Python)")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8002)
    args = parser.parse_args()
    
    if args.transport == "sse":
        server.run(transport="sse", host=args.host, port=args.port)
    else:
        server.run(transport="stdio")

if __name__ == "__main__":
    main()
