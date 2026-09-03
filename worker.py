import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from aiogram import Bot
from aiogram.enums import ParseMode

from config import settings
from database import Database
from classifier import DealClassifier
from monetization import monetization_engine
from formatter import TelegramFormatter
from guide_manager import GuideManager
from sources.feed_sources import get_all_deal_sources, BaseSource, RawDeal

logger = logging.getLogger(__name__)


class TravelDealWorker:
    def __init__(self, bot: Optional[Bot], db: Database, dry_run: bool = False):
        self.bot = bot
        self.db = db
        self.dry_run = dry_run
        self.guide_manager = GuideManager(db)
        self.sources: List[BaseSource] = get_all_deal_sources()

    def is_mock_mode(self) -> bool:
        if self.dry_run:
            return True
        if not settings.TELEGRAM_BOT_TOKEN:
            return True
        if "YOUR" in settings.TELEGRAM_BOT_TOKEN:
            return True
        if settings.TELEGRAM_BOT_TOKEN.startswith("123456789:"):
            return True
        return False

    async def run_cycle(self) -> int:
        """
        Executes one fetch-classify-monetize-publish cycle.
        Returns the number of new deals successfully published.
        """
        logger.info("=== [WORKER] Avvio scansione automatica offerte ===")
        all_raw_deals: List[RawDeal] = []

        # 1. Fetch from all sources concurrently
        fetch_tasks = [source.fetch() for source in self.sources]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        for src, res in zip(self.sources, results):
            if isinstance(res, Exception):
                logger.error(f"[{src.name}] Errore durante il fetch: {res}")
            elif isinstance(res, list):
                logger.info(f"[{src.name}] Trovate {len(res)} offerte.")
                all_raw_deals.extend(res)

        logger.info(f"[WORKER] Totale offerte grezze recuperate: {len(all_raw_deals)}")

        # 2. Filter out already posted deals
        unposted_deals: List[Dict[str, Any]] = []
        for raw in all_raw_deals:
            deal_id = Database.generate_deal_id(raw.title, raw.original_url)
            if not self.db.is_deal_posted(deal_id):
                classification = DealClassifier.classify(
                    title=raw.title,
                    description=raw.description,
                    price_hint=raw.price
                )

                if raw.raw_category and not classification["is_error_fare"]:
                    classification["category"] = raw.raw_category

                deal_dict = {
                    "id": deal_id,
                    "source": raw.source,
                    "title": raw.title,
                    "original_url": raw.original_url,
                    "description": raw.description,
                    "image_url": raw.image_url,
                    "published_at": raw.published_at or datetime.now(timezone.utc).isoformat(),
                    **classification
                }
                unposted_deals.append(deal_dict)

        logger.info(f"[WORKER] Nuove offerte inedite da valutare: {len(unposted_deals)}")

        # 3. Prioritization:
        # Error fares are #1 priority! Then Italian departures, then others.
        def sort_priority(d: Dict[str, Any]):
            if d.get("is_error_fare"):
                return 0
            if d.get("is_italy_departure"):
                return 1
            return 2

        unposted_deals.sort(key=sort_priority)

        # 4. Limit per run to avoid overwhelming the channel (e.g., max 3 per hour)
        to_publish = unposted_deals[:settings.MAX_DEALS_PER_RUN]
        published_count = 0

        for deal in to_publish:
            success = await self._publish_deal(deal)
            if success:
                self.db.save_deal(deal)
                published_count += 1
                if not self.is_mock_mode():
                    await asyncio.sleep(4)

        # 5. Check if we should publish a daily travel guide
        if settings.PUBLISH_GUIDES_DAILY:
            await self._check_and_publish_guide()

        logger.info(f"=== [WORKER] Ciclo completato: {published_count} nuove offerte pubblicate ===")
        return published_count

    async def _publish_deal(self, deal: Dict[str, Any]) -> bool:
        """
        Publishes a single deal to the channel with monetized keyboard.
        """
        caption = TelegramFormatter.format_deal(deal)
        is_package = "PACCHETTO" in deal.get("category", "").upper()
        keyboard = monetization_engine.build_deal_keyboard(
            original_url=deal["original_url"],
            departure=deal.get("departure"),
            destination=deal.get("destination"),
            is_package=is_package
        )

        if self.is_mock_mode():
            print("\n" + "—"*60)
            print(f"📢 [SIMULAZIONE CANALE: {settings.TELEGRAM_CHANNEL_ID}]")
            print("—"*60)
            print(caption)
            print("\n🔘 PULSANTI MONETIZZATI COLLEGATI:")
            for row in keyboard.inline_keyboard:
                row_str = " | ".join([f"[{btn.text}] -> {btn.url[:50]}..." for btn in row])
                print(f"  {row_str}")
            print("—"*60 + "\n")
            return True

        try:
            if deal.get("image_url") and self.bot:
                try:
                    await self.bot.send_photo(
                        chat_id=settings.TELEGRAM_CHANNEL_ID,
                        photo=deal["image_url"],
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard
                    )
                    return True
                except Exception as img_err:
                    logger.warning(f"Invio foto fallito per {deal['id']}, fallback a messaggio testo: {img_err}")

            if self.bot:
                await self.bot.send_message(
                    chat_id=settings.TELEGRAM_CHANNEL_ID,
                    text=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=False
                )
            return True

        except Exception as e:
            logger.error(f"Errore invio Telegram per offerta {deal['id']}: {e}")
            return False

    async def _check_and_publish_guide(self):
        """
        Publishes a travel guide if one hasn't been published today.
        """
        guide = self.guide_manager.get_next_guide_to_publish()
        if not guide:
            return

        text = TelegramFormatter.format_guide(guide)
        keyboard = monetization_engine.build_guide_keyboard(
            destination=guide.get("destination"),
            amazon_query=guide.get("amazon_query")
        )

        if self.is_mock_mode():
            print("\n" + "—"*60)
            print(f"📖 [SIMULAZIONE GUIDA DI VIAGGIO: {guide['title']}]")
            print("—"*60)
            print(text)
            print("\n🔘 PULSANTI MONETIZZATI GUIDA:")
            for row in keyboard.inline_keyboard:
                row_str = " | ".join([f"[{btn.text}] -> {btn.url[:50]}..." for btn in row])
                print(f"  {row_str}")
            print("—"*60 + "\n")
            self.guide_manager.mark_published(guide)
            return

        try:
            if self.bot:
                await self.bot.send_message(
                    chat_id=settings.TELEGRAM_CHANNEL_ID,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
                self.guide_manager.mark_published(guide)
                logger.info(f"[GUIDE] Guida pubblicata con successo: {guide['title']}")
        except Exception as e:
            logger.error(f"[GUIDE] Errore pubblicazione guida: {e}")
