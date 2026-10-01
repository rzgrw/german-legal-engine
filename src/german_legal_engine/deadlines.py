"""
deadlines.py
German Procedural Deadline Engine under §§ 187-193 BGB and ZPO.
Calculates Ereignisfristen, beginning, expiration, and weekend/holiday shifts
across all 16 German Bundesländer (Feiertagsgesetze).
"""

from datetime import date, timedelta
from typing import Dict, Any, Optional, List

# Official statutory public holidays per Bundesland
# Fixed holidays across Germany:
# - Neujahr (01.01)
# - Karfreitag (Easter - 2d)
# - Ostermontag (Easter + 1d)
# - Tag der Arbeit (01.05)
# - Christi Himmelfahrt (Easter + 39d)
# - Pfingstmontag (Easter + 50d)
# - Tag der Deutschen Einheit (03.10)
# - 1. Weihnachtstag (25.12)
# - 2. Weihnachtstag (26.12)

def calculate_easter_sunday(year: int) -> date:
    """Computes Easter Sunday using Butcher's algorithm."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_public_holidays(year: int, state: str = "BY") -> Dict[date, str]:
    """Returns all public holidays for a given German state and year."""
    easter = calculate_easter_sunday(year)
    
    holidays = {
        date(year, 1, 1): "Neujahr",
        easter - timedelta(days=2): "Karfreitag",
        easter + timedelta(days=1): "Ostermontag",
        date(year, 5, 1): "Tag der Arbeit",
        easter + timedelta(days=39): "Christi Himmelfahrt",
        easter + timedelta(days=50): "Pfingstmontag",
        date(year, 10, 3): "Tag der Deutschen Einheit",
        date(year, 12, 25): "1. Weihnachtstag",
        date(year, 12, 26): "2. Weihnachtstag"
    }
    
    state_upper = state.upper()
    
    # State-specific holidays:
    # Heilige Drei Könige (06.01): BW, BY, ST
    if state_upper in ["BW", "BY", "ST"]:
        holidays[date(year, 1, 6)] = "Heilige Drei Könige"
        
    # Fronleichnam (Easter + 60d): BW, BY, HE, NW, RP, SL
    if state_upper in ["BW", "BY", "HE", "NW", "RP", "SL"]:
        holidays[easter + timedelta(days=60)] = "Fronleichnam"
        
    # Mariä Himmelfahrt (15.08): SL, BY (teilweise)
    if state_upper in ["SL", "BY"]:
        holidays[date(year, 8, 15)] = "Mariä Himmelfahrt"
        
    # Reformationstag (31.10): BB, HB, HH, MV, NI, SN, ST, SH, TH
    if state_upper in ["BB", "HB", "HH", "MV", "NI", "SN", "ST", "SH", "TH"]:
        holidays[date(year, 10, 31)] = "Reformationstag"
        
    # Allerheiligen (01.11): BW, BY, NW, RP, SL
    if state_upper in ["BW", "BY", "NW", "RP", "SL"]:
        holidays[date(year, 11, 1)] = "Allerheiligen"
        
    return holidays


def calculate_deadline(
    ereignis_datum: date,
    dauer_wert: int,
    dauer_einheit: str = "wochen", # "tage", "wochen", "monate"
    state: str = "BY"
) -> Dict[str, Any]:
    """
    Computes German procedural deadlines according to §§ 187 Abs. 1, 188 Abs. 2, 193 BGB.
    - Ereignisfrist (§ 187 Abs. 1 BGB): Der Tag des Ereignisses zählt nicht mit.
    - Fristbeginn: Folgetag 00:00 Uhr.
    - Fristende (§ 188 Abs. 2 BGB): Ablauf mit dem Tag, der dem Ereignistag entspricht.
    - Feiertagsverschiebung (§ 193 BGB): Fällt das Ende auf Samstag, Sonntag oder Feiertag,
      verschiebt es sich auf den nächsten Werktag.
    """
    # 1. Fristbeginn (§ 187 Abs. 1 BGB)
    frist_beginn = ereignis_datum + timedelta(days=1)
    
    # 2. Reguläres Fristende (§ 188 BGB)
    unit = dauer_einheit.lower().strip()
    if unit in ["tage", "tag", "days"]:
        regulaeres_ende = ereignis_datum + timedelta(days=dauer_wert)
    elif unit in ["wochen", "woche", "weeks"]:
        regulaeres_ende = ereignis_datum + timedelta(weeks=dauer_wert)
    elif unit in ["monate", "monat", "months"]:
        # Add months properly
        year = ereignis_datum.year
        month = ereignis_datum.month + dauer_wert
        while month > 12:
            year += 1
            month -= 12
        day = min(ereignis_datum.day, 28) # safe handling
        regulaeres_ende = date(year, month, day)
    else:
        raise ValueError(f"Unknown deadline unit: {dauer_einheit}")
        
    # 3. Check weekend and holiday shift (§ 193 BGB)
    holidays = get_public_holidays(regulaeres_ende.year, state=state)
    # Also add next year's holidays if close to year end
    if regulaeres_ende.month == 12:
        holidays.update(get_public_holidays(regulaeres_ende.year + 1, state=state))
        
    endgueltiges_ende = regulaeres_ende
    shift_reasons = []
    
    while True:
        # Check Saturday (weekday 5) or Sunday (weekday 6)
        if endgueltiges_ende.weekday() == 5:
            shift_reasons.append(f"{endgueltiges_ende.strftime('%d.%m.%Y')} ist Samstag (§ 193 BGB)")
            endgueltiges_ende += timedelta(days=2) # skip to Monday
            continue
        elif endgueltiges_ende.weekday() == 6:
            shift_reasons.append(f"{endgueltiges_ende.strftime('%d.%m.%Y')} ist Sonntag (§ 193 BGB)")
            endgueltiges_ende += timedelta(days=1) # skip to Monday
            continue
            
        # Check public holiday
        if endgueltiges_ende in holidays:
            h_name = holidays[endgueltiges_ende]
            shift_reasons.append(f"{endgueltiges_ende.strftime('%d.%m.%Y')} ist gesetzlicher Feiertag ({h_name}, § 193 BGB)")
            endgueltiges_ende += timedelta(days=1)
            continue
            
        # If neither weekend nor holiday, we found the final valid business day
        break
        
    was_shifted = (endgueltiges_ende != regulaeres_ende)
    
    return {
        "ereignis_datum": ereignis_datum.isoformat(),
        "dauer": f"{dauer_wert} {dauer_einheit}",
        "jurisdiction_state": state.upper(),
        "frist_beginn": frist_beginn.isoformat(),
        "regulaeres_ende": regulaeres_ende.isoformat(),
        "endgueltiges_ende": endgueltiges_ende.isoformat(),
        "shifted_by_193_bgb": was_shifted,
        "shift_reasons": shift_reasons,
        "citation": f"Fristablauf am {endgueltiges_ende.strftime('%d.%m.%Y')} um 24:00 Uhr gem. §§ 187 Abs. 1, 188 Abs. 2, 193 BGB"
    }
