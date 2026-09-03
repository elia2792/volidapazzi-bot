import urllib.parse
from typing import Dict, List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import settings


class MonetizationEngine:
    def __init__(
        self,
        travelpayouts_marker: str = settings.TRAVELPAYOUTS_MARKER,
        booking_aid: str = settings.BOOKING_AID,
        skyscanner_tag: str = settings.SKYSCANNER_AFFILIATE_TAG,
        civitatis_id: str = settings.CIVITATIS_AFFILIATE_ID,
        amazon_tag: str = settings.AMAZON_AFFILIATE_TAG
    ):
        self.tp_marker = travelpayouts_marker
        self.booking_aid = booking_aid
        self.skyscanner_tag = skyscanner_tag
        self.civitatis_id = civitatis_id
        self.amazon_tag = amazon_tag

    def generate_flight_search_url(self, departure: Optional[str], destination: Optional[str], fallback_url: str) -> str:
        """
        Generates a direct monetized Aviasales flight search URL.
        Never wraps external URLs in tp.media to prevent 403 Forbidden.
        """
        if departure and destination:
            dep_clean = urllib.parse.quote_plus(departure.strip())
            dest_clean = urllib.parse.quote_plus(destination.strip())
            return f"https://www.aviasales.com/search?marker={self.tp_marker}&origin={dep_clean}&destination={dest_clean}"
        
        # Fallback to direct Aviasales landing with marker
        return f"https://www.aviasales.com/?marker={self.tp_marker}"

    def generate_hotel_search_url(self, destination: Optional[str]) -> str:
        """
        Generates a direct Booking.com hotel search URL.
        """
        dest_query = destination if destination else "Offerte Hotel"
        encoded = urllib.parse.quote_plus(dest_query)
        base = f"https://www.booking.com/searchresults.html?ss={encoded}&lang=it"
        if self.booking_aid and self.booking_aid != "2400000":
            return f"{base}&aid={self.booking_aid}"
        return base

    def generate_amazon_travel_gear_url(self, query: str = "zaino da viaggio cabina 40x20x25 ryanair") -> str:
        """
        Generates an Amazon affiliate search link with clean quote_plus and scontai-21 tag.
        """
        encoded = urllib.parse.quote_plus(query)
        return f"https://www.amazon.it/s?k={encoded}&tag={self.amazon_tag}"

    def build_deal_keyboard(
        self,
        original_url: str,
        departure: Optional[str] = None,
        destination: Optional[str] = None,
        is_package: bool = False
    ) -> InlineKeyboardMarkup:
        """
        Builds clear, 100% working, monetized buttons for each deal.
        """
        buttons: List[List[InlineKeyboardButton]] = []

        if is_package:
            # 1. For packages: direct link to the package deal page (contains exact hotel + flights)
            buttons.append([
                InlineKeyboardButton(text="🏝️ Vedi e Prenota Pacchetto Completo", url=original_url)
            ])
            # 2. Hotel comparison option
            if destination:
                buttons.append([
                    InlineKeyboardButton(text=f"🏨 Confronta Hotel a {destination}", url=self.generate_hotel_search_url(destination))
                ])
        else:
            # 1. Flight / Error fare: Direct flight search + Original source
            flight_search = self.generate_flight_search_url(departure, destination, original_url)
            buttons.append([
                InlineKeyboardButton(text="✈️ Cerca Volo / Tariffe", url=flight_search)
            ])
            buttons.append([
                InlineKeyboardButton(text="🔎 Dettagli Offerta & Date Esatte", url=original_url)
            ])
            if destination:
                buttons.append([
                    InlineKeyboardButton(text=f"🏨 Cerca Hotel a {destination}", url=self.generate_hotel_search_url(destination))
                ])

        # Always include Amazon travel accessories button with scontai-21
        amazon_url = self.generate_amazon_travel_gear_url("zaino cabina 40x20x25 ryanair")
        buttons.append([
            InlineKeyboardButton(text="🎒 Zaini & Accessori Cabina (Amazon)", url=amazon_url)
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def build_guide_keyboard(self, destination: Optional[str] = None, amazon_query: Optional[str] = None) -> InlineKeyboardMarkup:
        """
        Builds inline buttons for travel guides.
        """
        buttons: List[List[InlineKeyboardButton]] = []

        if destination:
            buttons.append([
                InlineKeyboardButton(text=f"🏨 Hotel Consigliati a {destination}", url=self.generate_hotel_search_url(destination))
            ])

        gear_query = amazon_query or "zaino da viaggio cabina 40x20x25 ryanair"
        gear_url = self.generate_amazon_travel_gear_url(gear_query)
        buttons.append([
            InlineKeyboardButton(text="🎒 Zaino & Accessori da Viaggio Consigliati", url=gear_url)
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)


monetization_engine = MonetizationEngine()
