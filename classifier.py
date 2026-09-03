import re
from typing import Dict, Any, Optional, Tuple


ITALIAN_CITIES = [
    "milano", "milan", "roma", "rome", "napoli", "naples", "venezia", "venice",
    "bologna", "bari", "catania", "palermo", "pisa", "torino", "turin",
    "bergamo", "firenze", "florence", "genova", "cagliari", "verona", "treviso",
    "brindisi", "lamezia", "trieste", "alghero", "olbia", "pescara", "italia", "italy"
]

ERROR_FARE_KEYWORDS = [
    "error fare", "errore di prezzo", "price glitch", "glitch", "errore tariffario",
    "prezzo pazzo", "prezzo stracciato", "tariff error", "mispriced", "fuel dump"
]

PACKAGE_KEYWORDS = [
    "volo + hotel", "volo+hotel", "flight + hotel", "pacchetto", "package",
    "all inclusive", "mezza pensione", "resort", "hotel 4*", "hotel 5*", "soggiorno",
    "weekend a", "vacanza a", "notti in"
]

DESTINATION_EMOJIS = {
    "giappone": "🇯🇵", "tokyo": "🇯🇵", "japan": "🇯🇵",
    "usa": "🇺🇸", "new york": "🇺🇸", "miami": "🇺🇸", "stati uniti": "🇺🇸", "los angeles": "🇺🇸",
    "spagna": "🇪🇸", "barcellona": "🇪🇸", "madrid": "🇪🇸", "tenerife": "🇪🇸", "mallorca": "🇪🇸", "ibiza": "🇪🇸",
    "grecia": "🇬🇷", "santorini": "🇬🇷", "mykonos": "🇬🇷", "creta": "🇬🇷", "atene": "🇬🇷",
    "francia": "🇫🇷", "parigi": "🇫🇷", "paris": "🇫🇷",
    "regno unito": "🇬🇧", "londra": "🇬🇧", "london": "🇬🇧",
    "thailandia": "🇹🇭", "bangkok": "🇹🇭", "phuket": "🇹🇭",
    "maldive": "🇲🇻", "maldives": "🇲🇻",
    "emirati": "🇦🇪", "dubai": "🇦🇪", "abu dhabi": "🇦🇪",
    "portogallo": "🇵🇹", "lisbona": "🇵🇹", "porto": "🇵🇹",
    "islanda": "🇮🇸", "reykjavik": "🇮🇸",
    "marocco": "🇲🇦", "marrakech": "🇲🇦",
    "egitto": "🇪🇬", "sharm": "🇪🇬", "il cairo": "🇪🇬",
    "germania": "🇩🇪", "berlino": "🇩🇪",
    "olanda": "🇳🇱", "amsterdam": "🇳🇱",
}


class DealClassifier:
    @classmethod
    def classify(cls, title: str, description: str = "", price_hint: Optional[str] = None) -> Dict[str, Any]:
        text = f"{title} {description}".lower()

        # 1. Price extraction
        price = price_hint or cls._extract_price(title) or cls._extract_price(description)

        # 2. Category detection
        is_error_fare = False
        for kw in ERROR_FARE_KEYWORDS:
            if kw in text:
                is_error_fare = True
                break

        # Long-haul extreme low price heuristic (e.g., flight to Asia or USA under 230 EUR)
        if not is_error_fare and price:
            num_price = cls._parse_numeric_price(price)
            if num_price and num_price < 230:
                if any(k in text for k in ["new york", "usa", "tokyo", "giappone", "thailandia", "bangkok", "maldive", "brasile", "miami"]):
                    is_error_fare = True

        if is_error_fare:
            category = "🚨 ERRORE DI PREZZO"
        elif any(kw in text for kw in PACKAGE_KEYWORDS):
            category = "🏝️ PACCHETTO VACANZA"
        else:
            category = "✈️ VOLO LOW COST"

        # 3. Route parsing (Departure -> Destination)
        departure, destination = cls._extract_route(title, text)
        is_italy = cls._is_italy_departure(departure, text)

        # 4. Destination emoji
        emoji = "🌍"
        for key, val in DESTINATION_EMOJIS.items():
            if key in text or (destination and key in destination.lower()):
                emoji = val
                break

        return {
            "category": category,
            "is_error_fare": is_error_fare,
            "price": price,
            "departure": departure,
            "destination": destination,
            "is_italy_departure": is_italy,
            "destination_emoji": emoji
        }

    @staticmethod
    def _extract_price(text: str) -> Optional[str]:
        patterns = [
            r'(\d+[\.,]?\d*)\s*(?:€|euro|eur)',
            r'(?:€|euro|eur)\s*(\d+[\.,]?\d*)',
            r'\$\s*(\d+[\.,]?\d*)',
            r'(\d+[\.,]?\d*)\s*\$',
            r'£\s*(\d+[\.,]?\d*)'
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                val = match.group(1).replace(",", ".")
                try:
                    num = float(val)
                    return f"{int(num)}€" if num.is_integer() else f"{num:.2f}€"
                except ValueError:
                    continue
        return None

    @staticmethod
    def _parse_numeric_price(price_str: str) -> Optional[float]:
        clean = re.sub(r'[^\d\.]', '', price_str.replace(",", "."))
        try:
            return float(clean)
        except ValueError:
            return None

    @classmethod
    def _clean_location(cls, loc: str) -> str:
        loc = re.split(r'\b(?:da soli|a soli|a partire|con|soli|from|per|da|for|e|\d+|!|\(|\:)\b', loc, flags=re.IGNORECASE)[0]
        return loc.strip().strip("-–—,").title()

    @classmethod
    def _extract_route(cls, title: str, text: str) -> Tuple[Optional[str], Optional[str]]:
        # Strip noise words like "non-stop", "cheap flights", "flights", etc.
        clean_title = re.sub(r'\b(?:non-stop|non stop|cheap flights|cheap|flights|voli low cost|voli)\b', '', title, flags=re.IGNORECASE)

        # Pattern 1: "per [Destination] da [Departure]" (e.g. "Voli per New York da Milano")
        m_per_da = re.search(
            r'(?:per|to)\s+([A-Za-z\s]+?)\s+(?:da|from)\s+([A-Za-z\s]+?)(?:\s+for|\s+a\s+soli|\s+da\s+soli|\s+a\s+partire|\s+con|\s*\d|!|\(|$)',
            clean_title,
            re.IGNORECASE
        )
        if m_per_da:
            dest = cls._clean_location(m_per_da.group(1))
            dep = cls._clean_location(m_per_da.group(2))
            if dep and dest and dep.lower() not in ["non", "stop"] and dest.lower() not in ["non", "stop"]:
                return dep, dest

        # Pattern 2: "da [Departure] a [Destination]" (e.g. "da Bologna a Londra da soli 19€", "from Toronto to Rome for only C$353")
        m_da_a = re.search(
            r'(?:da|from)\s+([A-Za-z\s]+?)\s+(?:a|to)\s+([A-Za-z\s]+?)(?:\s+for|\s+da\s+soli|\s+a\s+soli|\s+a\s+partire|\s+con|\s+soli|\s+from|\s*\d|!|\(|\:|$)',
            clean_title,
            re.IGNORECASE
        )
        if m_da_a:
            dep = cls._clean_location(m_da_a.group(1))
            dest = cls._clean_location(m_da_a.group(2))
            if dep and dest and dep.lower() not in ["non", "stop"] and dest.lower() not in ["non", "stop"]:
                return dep, dest

        # Pattern 3: "[Departure] - [Destination]"
        m_dash = re.search(r'([A-Za-z]+)\s*(?:-|–|—|->)\s*([A-Za-z]+)', clean_title)
        if m_dash:
            dep = cls._clean_location(m_dash.group(1))
            dest = cls._clean_location(m_dash.group(2))
            if dep and dest and dep.lower() not in ["non", "stop"] and dest.lower() not in ["non", "stop"]:
                return dep, dest

        # Fallback: check Italian departure city in text
        departure = None
        for city in ITALIAN_CITIES:
            if re.search(rf'\b(?:da|from)\s+{city}\b', text):
                departure = city.title()
                break

        return departure, None

    @staticmethod
    def _is_italy_departure(departure: Optional[str], text: str) -> bool:
        if departure and departure.lower() in ITALIAN_CITIES:
            return True
        return any(f"da {city}" in text or f"from {city}" in text for city in ITALIAN_CITIES)
