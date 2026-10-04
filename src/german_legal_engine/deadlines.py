"""
deadlines.py
German Procedural Deadline Engine under §§ 187-193 BGB and ZPO.
Calculates Ereignisfristen, beginning, expiration, and weekend/holiday shifts
across all 16 German Bundesländer (Feiertagsgesetze).
"""

import calendar
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
        
    # Internationaler Frauentag (08.03): BE, MV
    if state_upper in ["BE", "MV"]:
        holidays[date(year, 3, 8)] = "Internationaler Frauentag"
        
    # Fronleichnam (Easter + 60d): BW, BY, HE, NW, RP, SL
    if state_upper in ["BW", "BY", "HE", "NW", "RP", "SL"]:
        holidays[easter + timedelta(days=60)] = "Fronleichnam"
        
    # Mariä Himmelfahrt (15.08): SL, BY (in Gemeinden mit überwiegend katholischer Bevölkerung)
    if state_upper in ["SL", "BY"]:
        holidays[date(year, 8, 15)] = "Mariä Himmelfahrt"
        
    # Weltkindertag (20.09): TH
    if state_upper in ["TH"]:
        holidays[date(year, 9, 20)] = "Weltkindertag"
        
    # Reformationstag (31.10): BB, HB, HH, MV, NI, SN, ST, SH, TH
    if state_upper in ["BB", "HB", "HH", "MV", "NI", "SN", "ST", "SH", "TH"]:
        holidays[date(year, 10, 31)] = "Reformationstag"
        
    # Allerheiligen (01.11): BW, BY, NW, RP, SL
    if state_upper in ["BW", "BY", "NW", "RP", "SL"]:
        holidays[date(year, 11, 1)] = "Allerheiligen"
        
    # Buß- und Bettag (Mittwoch vor dem 23. November): SN
    if state_upper in ["SN"]:
        nov23 = date(year, 11, 23)
        # Weekday: Monday is 0, Wednesday is 2
        days_since_wed = (nov23.weekday() - 2) % 7
        if days_since_wed == 0:
            days_since_wed = 7
        holidays[nov23 - timedelta(days=days_since_wed)] = "Buß- und Bettag"
        
    return holidays


def calculate_deadline(
    ereignis_datum: date,
    dauer_wert: int,
    dauer_einheit: str = "wochen", # "tage", "wochen", "monate", "jahre"
    state: str = "BY"
) -> Dict[str, Any]:
    """
    Computes German procedural deadlines according to §§ 187 Abs. 1, 188 Abs. 2, 193 BGB.
    - Ereignisfrist (§ 187 Abs. 1 BGB): Der Tag des Ereignisses zählt nicht mit.
    - Fristbeginn: Folgetag 00:00 Uhr.
    - Fristende (§ 188 Abs. 2 BGB): Ablauf mit dem Tag, der dem Ereignistag entspricht.
    - Fehlt der entsprechende Tag (§ 188 Abs. 3 BGB): Ablauf mit dem letzten Tag des Monats.
    - Feiertagsverschiebung (§ 193 BGB): Fällt das Ende auf Samstag, Sonntag oder Feiertag,
      verschiebt es sich auf den nächsten Werktag.
    """
    # 1. Fristbeginn (§ 187 Abs. 1 BGB)
    frist_beginn = ereignis_datum + timedelta(days=1)
    
    audit_trail: List[Dict[str, Any]] = [
        {
            "step": 1,
            "rule": "§ 187 Abs. 1 BGB",
            "title": "Ereignisfrist und Fristbeginn",
            "description": f"Der Tag des auslösenden Ereignisses ({ereignis_datum.strftime('%d.%m.%Y')}) wird bei der Fristberechnung nicht mitgerechnet. Die Frist beginnt am Folgetag ({frist_beginn.strftime('%d.%m.%Y')}) um 00:00 Uhr."
        }
    ]
    
    # 2. Reguläres Fristende (§ 188 BGB)
    unit = dauer_einheit.lower().strip()
    if unit in ["tage", "tag", "days"]:
        regulaeres_ende = ereignis_datum + timedelta(days=dauer_wert)
        audit_trail.append({
            "step": 2,
            "rule": "§ 188 Abs. 1 BGB",
            "title": "Ablauf der Tagesfrist",
            "description": f"Die nach Tagen bestimmte Frist ({dauer_wert} Tag(e)) endigt mit Ablauf des letzten Tages ({regulaeres_ende.strftime('%d.%m.%Y')}) um 24:00 Uhr."
        })
    elif unit in ["wochen", "woche", "weeks"]:
        regulaeres_ende = ereignis_datum + timedelta(weeks=dauer_wert)
        audit_trail.append({
            "step": 2,
            "rule": "§ 188 Abs. 2 Alt. 1 BGB",
            "title": "Ablauf der Wochenfrist",
            "description": f"Die nach Wochen bestimmte Frist ({dauer_wert} Woche(n)) endigt mit Ablauf desjenigen Tages der letzten Woche, welcher durch seine Benennung dem Ereignistag entspricht ({regulaeres_ende.strftime('%d.%m.%Y')}) um 24:00 Uhr."
        })
    elif unit in ["monate", "monat", "months"]:
        # Calculation according to § 188 Abs. 2 and Abs. 3 BGB
        total_months = (ereignis_datum.month - 1) + dauer_wert
        target_year = ereignis_datum.year + (total_months // 12)
        target_month = (total_months % 12) + 1
        days_in_target_month = calendar.monthrange(target_year, target_month)[1]
        
        # § 188 Abs. 2 BGB: same day number as trigger event
        # § 188 Abs. 3 BGB: if day doesn't exist, last day of the month
        target_day = min(ereignis_datum.day, days_in_target_month)
        regulaeres_ende = date(target_year, target_month, target_day)
        if target_day < ereignis_datum.day:
            audit_trail.append({
                "step": 2,
                "rule": "§ 188 Abs. 3 BGB",
                "title": "Ablauf der Monatsfrist bei fehlendem Kalendertag",
                "description": f"Fehlt dem Zielmonat der dem Ereignistag entsprechende Tag ({ereignis_datum.day}.), so endigt die Frist mit Ablauf des letzten Tages des Monats ({regulaeres_ende.strftime('%d.%m.%Y')}) um 24:00 Uhr gem. § 188 Abs. 3 BGB."
            })
        else:
            audit_trail.append({
                "step": 2,
                "rule": "§ 188 Abs. 2 Alt. 2 BGB",
                "title": "Ablauf der Monatsfrist",
                "description": f"Die nach Monaten bestimmte Frist ({dauer_wert} Monat(e)) endigt mit Ablauf desjenigen Tages des letzten Monats, welcher durch seine Zahl dem Ereignistag entspricht ({regulaeres_ende.strftime('%d.%m.%Y')}) um 24:00 Uhr."
            })
    elif unit in ["jahre", "jahr", "years"]:
        target_year = ereignis_datum.year + dauer_wert
        days_in_target_month = calendar.monthrange(target_year, ereignis_datum.month)[1]
        target_day = min(ereignis_datum.day, days_in_target_month)
        regulaeres_ende = date(target_year, ereignis_datum.month, target_day)
        audit_trail.append({
            "step": 2,
            "rule": "§ 188 Abs. 2 BGB",
            "title": "Ablauf der Jahresfrist",
            "description": f"Die nach Jahren bestimmte Frist ({dauer_wert} Jahr(e)) endigt mit Ablauf desjenigen Tages des letzten Jahres, welcher durch seine Zahl und seinen Monat dem Ereignistag entspricht ({regulaeres_ende.strftime('%d.%m.%Y')}) um 24:00 Uhr."
        })
    else:
        raise ValueError(f"Unknown deadline unit: {dauer_einheit}")
        
    # 3. Check weekend and holiday shift (§ 193 BGB)
    # Ensure holidays are populated for all involved years
    holidays = {}
    for y in {regulaeres_ende.year, regulaeres_ende.year + 1}:
        holidays.update(get_public_holidays(y, state=state))
        
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
            
        # Ensure holidays for endgueltiges_ende.year are present
        if endgueltiges_ende.year not in holidays:
            holidays.update(get_public_holidays(endgueltiges_ende.year, state=state))
            
        # Check public holiday
        if endgueltiges_ende in holidays:
            h_name = holidays[endgueltiges_ende]
            shift_reasons.append(f"{endgueltiges_ende.strftime('%d.%m.%Y')} ist gesetzlicher Feiertag ({h_name}, § 193 BGB)")
            endgueltiges_ende += timedelta(days=1)
            continue
            
        # If neither weekend nor holiday, we found the final valid business day
        break
        
    was_shifted = (endgueltiges_ende != regulaeres_ende)
    
    if was_shifted:
        audit_trail.append({
            "step": 3,
            "rule": f"§ 193 BGB i.V.m. Feiertagsrecht ({state.upper()})",
            "title": "Schutzvorschrift bei Wochenenden und Feiertagen",
            "description": f"Das reguläre Fristende ({regulaeres_ende.strftime('%d.%m.%Y')}) fiel auf einen Samstag, Sonntag oder gesetzlichen Feiertag. Gemäß § 193 BGB verschiebt sich der Ablauf auf den nächsten Werktag ({endgueltiges_ende.strftime('%d.%m.%Y')}, 24:00 Uhr). Festgestellte Hinderungsgründe: {'; '.join(shift_reasons)}."
        })
    else:
        audit_trail.append({
            "step": 3,
            "rule": f"§ 193 BGB i.V.m. Feiertagsrecht ({state.upper()})",
            "title": "Werktagsprüfung",
            "description": f"Das reguläre Fristende ({regulaeres_ende.strftime('%d.%m.%Y')}) fällt auf einen regulären Werktag in {state.upper()}. Eine Schutzverschiebung nach § 193 BGB ist nicht veranlasst."
        })

    audit_trail.append({
        "step": 4,
        "rule": "Prozessuale Feststellung",
        "title": "Rechtswirksamer Fristablauf",
        "description": f"Die Frist läuft endgültig ab am {endgueltiges_ende.strftime('%d.%m.%Y')} um 24:00 Uhr ({'mit Schutzverschiebung gem. § 193 BGB' if was_shifted else 'ohne Schutzverschiebung'})."
    })
    
    return {
        "ereignis_datum": ereignis_datum.isoformat(),
        "dauer": f"{dauer_wert} {dauer_einheit}",
        "jurisdiction_state": state.upper(),
        "frist_beginn": frist_beginn.isoformat(),
        "regulaeres_ende": regulaeres_ende.isoformat(),
        "endgueltiges_ende": endgueltiges_ende.isoformat(),
        "shifted_by_193_bgb": was_shifted,
        "shift_reasons": shift_reasons,
        "audit_trail": audit_trail,
        "citation": f"Fristablauf am {endgueltiges_ende.strftime('%d.%m.%Y')} um 24:00 Uhr gem. §§ 187 Abs. 1, 188 Abs. 2, 193 BGB"
    }
