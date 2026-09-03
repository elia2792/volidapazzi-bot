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
        getyourguide_id: str = settings.GETYOURGUIDE_PARTNER_ID,
        amazon_tag: str = settings.AMAZON_AFFILIATE_TAG
    ):
        self.tp_marker = travelpayouts_marker
        self.booking_aid = booking_aid
        self.skyscanner_tag = skyscanner_tag
        self.civitatis_id = civitatis_id
        self.getyourguide_id = getyourguide_id
        self.amazon_tag = amazon_tag

    def generate_flight_search_url(self, departure: Optional[str], destination: Optional[str], fallback_url: str) -> str:
        """
        Generates a direct monetized flight search link (via Travelpayouts / Aviasales / WayAway).
        """
        if departure and destination:
            dep_clean = urllib.parse.quote_plus(departure.strip())
            dest_clean = urllib.parse.quote_plus(destination.strip())
            base_search = f"https://www.aviasales.com/search?origin={dep_clean}&destination={dest_clean}"
            return f"https://tp.media/r?marker={self.tp_marker}&p=4114&u={urllib.parse.quote(base_search)}"
        
        encoded_url = urllib.parse.quote(fallback_url)
        return f"https://tp.media/r?marker={self.tp_marker}&p=4114&u={encoded_url}"

    def generate_hotel_search_url(self, destination: Optional[str]) -> str:
        dest_query = destination if destination else "Offerte Hotel"
        encoded = urllib.parse.quote_plus(dest_query)
        booking_direct = f"https://www.booking.com/searchresults.html?ss={encoded}&lang=it"

        if self.booking_aid and self.booking_aid != "2400000":
            return f"{booking_direct}&aid={self.booking_aid}"
        
        return f"https://tp.media/r?marker={self.tp_marker}&p=844&u={urllib.parse.quote(booking_direct)}"

    def generate_activities_url(self, destination: Optional[str]) -> str:
        dest_query = destination if destination else "Tour e Attività"
        encoded = urllib.parse.quote_plus(dest_query)
        if self.civitatis_id and self.civitatis_id != "travelbot":
            return f"https://www.civitatis.com/it/search?q={encoded}&aff_id={self.civitatis_id}"
        return f"https://tp.media/r?marker={self.tp_marker}&p=648&u={urllib.parse.quote(f'https://www.tiqets.com/it/search/?q={encoded}')}"

    def generate_amazon_travel_gear_url(self, query: str = "zaino da viaggio cabina 40x20x25 ryanair") -> str:
        """
        Generates an Amazon affiliate link with clean quote_plus formatting.
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
        Builds a multi-button Telegram inline keyboard with monetized affiliate buttons.
        """
        buttons: List[List[InlineKeyboardButton]] = []

        # Row 1: Flight / Package booking
        flight_url = self.generate_flight_search_url(departure, destination, original_url)
        main_button_label = "🏝️ Prenota Pacchetto" if is_package else "✈️ Prenota Volo / Tariffe"
        buttons.append([
            InlineKeyboardButton(text=main_button_label, url=flight_url)
        ])

        # Row 2: Hotel & Activities
        second_row: List[InlineKeyboardButton] = []
        if destination:
            hotel_url = self.generate_hotel_search_url(destination)
            second_row.append(InlineKeyboardButton(text="🏨 Cerca Hotel", url=hotel_url))

            tours_url = self.generate_activities_url(destination)
            second_row.append(InlineKeyboardButton(text="🎟️ Tour & Attività", url=tours_url))

        if second_row:
            buttons.append(second_row)

        # Row 3: Amazon Travel Accessories (Direct monetization on EVERY deal!)
        amazon_url = self.generate_amazon_travel_gear_url("zaino cabina 40x20x25 ryanair")
        buttons.append([
            InlineKeyboardButton(text="🎒 Zaini & Accessori Cabina (Amazon)", url=amazon_url)
        ])

        # Row 4: Full source details
        buttons.append([
            InlineKeyboardButton(text="🔎 Dettagli Completi & Date", url=original_url)
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def build_guide_keyboard(self, destination: Optional[str] = None, amazon_query: Optional[str] = None) -> InlineKeyboardMarkup:
        """
        Builds inline buttons for travel guides.
        """
        buttons: List[List[InlineKeyboardButton]] = []

        row1: List[InlineKeyboardButton] = []
        if destination:
            hotel_url = self.generate_hotel_search_url(destination)
            row1.append(InlineKeyboardButton(text=f"🏨 Hotel a {destination}", url=hotel_url))
            tours_url = self.generate_activities_url(destination)
            row1.append(InlineKeyboardButton(text="🎟️ Tour Guidati", url=tours_url))
            buttons.append(row1)

        gear_query = amazon_query or "zaino da viaggio cabina 40x20x25 ryanair"
        gear_url = self.generate_amazon_travel_gear_url(gear_query)
        buttons.append([
            InlineKeyboardButton(text="🎒 Zaino & Accessori da Viaggio Consigliati", url=gear_url)
        ])

        return InlineKeyboardMarkup(inline_keyboard=buttons)


monetization_engine = MonetizationEngine()
