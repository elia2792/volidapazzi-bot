import html
from typing import Dict, Any, Optional


class TelegramFormatter:
    @staticmethod
    def format_deal(deal: Dict[str, Any]) -> str:
        """
        Formats a deal into a high-converting Telegram HTML post.
        """
        category = deal.get("category", "✈️ VOLO LOW COST")
        title = html.escape(deal.get("title", ""))
        price = deal.get("price")
        departure = deal.get("departure")
        destination = deal.get("destination")
        dest_emoji = deal.get("destination_emoji", "🌍")
        desc = deal.get("description", "")

        # Clean short snippet of description (first 250 chars)
        short_desc = ""
        if desc:
            clean = html.escape(desc[:260])
            if len(desc) > 260:
                clean += "..."
            short_desc = f"\n📝 <i>{clean}</i>\n"

        lines = []

        # Header Badge
        if deal.get("is_error_fare"):
            lines.append("🚨 <b>ALLERTA: ERRORE DI PREZZO SUI VOLI!</b> 🚨")
            lines.append("⚡ <i>Tariffa anomala da bloccare subito!</i>\n")
        elif "PACCHETTO" in category.upper():
            lines.append("🏝️ <b>PACCHETTO VACANZA LOW COST</b> 🏝️\n")
        else:
            lines.append("✈️ <b>OFFERTA VOLO LOW COST</b> ✈️\n")

        # Main Title
        lines.append(f"<b>{title}</b>\n")

        # Key Specs
        if departure:
            flag = "🇮🇹 " if deal.get("is_italy_departure") else "🛫 "
            lines.append(f"{flag}<b>Partenza:</b> {html.escape(departure)}")

        if destination:
            lines.append(f"{dest_emoji} <b>Destinazione:</b> {html.escape(destination)}")

        if price:
            lines.append(f"💰 <b>Prezzo:</b> <b>{html.escape(price)}</b>")

        if short_desc:
            lines.append(short_desc)

        # Urgency notice for error fares
        if deal.get("is_error_fare"):
            lines.append("\n⚠️ <i>Regola d'oro: Non contattare la compagnia aerea! Prenota subito prima che il bug venga corretto.</i>")

        lines.append("\n👇 <b>Prenota ai link qui sotto prima che le tariffe aumentino:</b>")

        # Hashtags for Telegram search
        tags = ["#VoliLowCost", "#OfferteViaggi"]
        if deal.get("is_error_fare"):
            tags.insert(0, "#ErroreDiPrezzo")
        if "PACCHETTO" in category.upper():
            tags.insert(0, "#PacchettiVacanze")
        if destination:
            clean_tag = destination.replace(" ", "").replace("-", "")
            tags.append(f"#{clean_tag}")

        lines.append("\n" + " ".join(tags))

        return "\n".join(lines)

    @staticmethod
    def format_guide(guide: Dict[str, Any]) -> str:
        """
        Formats a travel guide or travel tips for Telegram.
        """
        title = guide.get("title", "Guida di Viaggio")
        content = guide.get("content", "")
        tags = "#GuideDiViaggio #ConsigliDiViaggio #ViaggiareLowCost"

        return f"📖 <b>{title}</b>\n\n{content}\n\n{tags}"
