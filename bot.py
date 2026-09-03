import logging
from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode

from config import settings
from database import Database
from formatter import TelegramFormatter
from monetization import monetization_engine
from guide_manager import GuideManager

logger = logging.getLogger(__name__)
router = Router()


def get_bot_router(db: Database) -> Router:
    guide_mgr = GuideManager(db)

    @router.message(CommandStart())
    async def cmd_start(message: Message):
        user = message.from_user
        if user:
            db.add_subscriber(user.id, user.username, user.first_name)

        welcome_text = (
            f"👋 Ciao <b>{user.first_name if user else 'Viaggiatore'}</b>!\n\n"
            "✈️ Benvenuto nel tuo <b>Bot Ufficiale di Viaggi & Voli Low Cost</b>!\n\n"
            "Monitoriamo 24 ore su 24, ogni singola ora, centinaia di fonti per trovare:\n"
            "🚨 <b>Errori di prezzo (Error Fares)</b> sui voli per viaggiare quasi gratis\n"
            "✈️ <b>Voli Low Cost</b> dall'Italia e dall'Europa\n"
            "🏝️ <b>Pacchetti Vacanze completi</b> (Volo + Hotel / All Inclusive)\n"
            "📖 <b>Guide e trucchi di viaggio</b> per risparmiare ovunque\n\n"
            f"📢 <b>Unisciti al Canale Ufficiale per le offerte in tempo reale:</b>\n"
            f"{settings.TELEGRAM_CHANNEL_ID}\n\n"
            "<b>Comandi veloci:</b>\n"
            "• /offerte - Le ultime offerte trovate\n"
            "• /errori - Solo errori di prezzo clamorosi\n"
            "• /pacchetti - Pacchetti vacanze volo+hotel\n"
            "• /guide - Guide e trucchi salva-portafoglio\n"
            "• /stats - Statistiche del bot"
        )

        buttons = [
            [InlineKeyboardButton(text="📢 Canale Offerte Telegram", url=f"https://t.me/{settings.TELEGRAM_CHANNEL_ID.replace('@', '')}")],
            [
                InlineKeyboardButton(text="🚨 Errori di Prezzo", callback_data="show_errors"),
                InlineKeyboardButton(text="✈️ Ultime Offerte", callback_data="show_deals")
            ],
            [InlineKeyboardButton(text="📖 Guide di Viaggio", callback_data="show_guides")]
        ]

        await message.answer(
            text=welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    @router.message(Command("offerte"))
    async def cmd_offerte(message: Message):
        deals = db.get_recent_deals(limit=5)
        if not deals:
            await message.answer("Nessuna offerta recente al momento. Il bot sta effettuando la scansione oraria!")
            return

        for deal in deals:
            text = TelegramFormatter.format_deal(deal)
            is_pkg = "PACCHETTO" in deal.get("category", "").upper()
            kb = monetization_engine.build_deal_keyboard(
                original_url=deal["original_url"],
                departure=deal.get("departure"),
                destination=deal.get("destination"),
                is_package=is_pkg
            )
            await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @router.message(Command("errori"))
    async def cmd_errori(message: Message):
        deals = db.get_error_fares(limit=4)
        if not deals:
            await message.answer("🚨 Al momento nessun errore di prezzo attivo nelle ultime ore. Il sistema controlla ogni ora!")
            return

        for deal in deals:
            text = TelegramFormatter.format_deal(deal)
            kb = monetization_engine.build_deal_keyboard(
                original_url=deal["original_url"],
                departure=deal.get("departure"),
                destination=deal.get("destination"),
                is_package=False
            )
            await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @router.message(Command("pacchetti"))
    async def cmd_pacchetti(message: Message):
        deals = db.get_recent_deals(limit=4, category="🏝️ PACCHETTO VACANZA")
        if not deals:
            # Fallback
            deals = [d for d in db.get_recent_deals(limit=10) if "PACCHETTO" in d.get("category", "").upper()]

        if not deals:
            await message.answer("🏝️ Nessun pacchetto vacanza trovato di recente. Riprova più tardi!")
            return

        for deal in deals:
            text = TelegramFormatter.format_deal(deal)
            kb = monetization_engine.build_deal_keyboard(
                original_url=deal["original_url"],
                departure=deal.get("departure"),
                destination=deal.get("destination"),
                is_package=True
            )
            await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @router.message(Command("guide"))
    async def cmd_guide(message: Message):
        guides = guide_mgr.get_all_guides()
        buttons = []
        for g in guides:
            buttons.append([InlineKeyboardButton(text=g["title"], callback_data=f"read_guide_{g['id']}")])

        await message.answer(
            "📚 <b>Guide & Consigli per Viaggiare Low Cost:</b>\n\nScegli un argomento per leggere la guida completa:",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )

    @router.message(Command("stats"))
    async def cmd_stats(message: Message):
        stats = db.get_stats()
        text = (
            "📊 <b>Statistiche Monitor Viaggi & Voli 24/7</b>\n\n"
            f"• Offerte totali tracciate: <b>{stats['total_deals']}</b>\n"
            f"• Offerte scovate nelle ultime 24h: <b>{stats['deals_24h']}</b>\n"
            f"• Errori di prezzo segnalati: <b>{stats['total_errors']}</b>\n"
            f"• Iscritti al bot: <b>{stats['total_subscribers']}</b>\n"
            f"• Frequenza di aggiornamento: <b>Ogni ora h24</b>"
        )
        await message.answer(text, parse_mode=ParseMode.HTML)

    # Callback Query Handlers
    @router.callback_query(F.data == "show_deals")
    async def cb_show_deals(cb: CallbackQuery):
        await cb.answer()
        if cb.message:
            deals = db.get_recent_deals(limit=3)
            for deal in deals:
                text = TelegramFormatter.format_deal(deal)
                is_pkg = "PACCHETTO" in deal.get("category", "").upper()
                kb = monetization_engine.build_deal_keyboard(deal["original_url"], deal.get("departure"), deal.get("destination"), is_pkg)
                await cb.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @router.callback_query(F.data == "show_errors")
    async def cb_show_errors(cb: CallbackQuery):
        await cb.answer()
        if cb.message:
            deals = db.get_error_fares(limit=3)
            if not deals:
                await cb.message.answer("🚨 Nessun errore di prezzo attivo nelle ultimissime ore!")
                return
            for deal in deals:
                text = TelegramFormatter.format_deal(deal)
                kb = monetization_engine.build_deal_keyboard(deal["original_url"], deal.get("departure"), deal.get("destination"), False)
                await cb.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    @router.callback_query(F.data == "show_guides")
    async def cb_show_guides(cb: CallbackQuery):
        await cb.answer()
        if cb.message:
            guides = guide_mgr.get_all_guides()
            buttons = [[InlineKeyboardButton(text=g["title"], callback_data=f"read_guide_{g['id']}")] for g in guides]
            await cb.message.answer("📚 <b>Guide di Viaggio:</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

    @router.callback_query(F.data.startswith("read_guide_"))
    async def cb_read_guide(cb: CallbackQuery):
        await cb.answer()
        guide_id = cb.data.replace("read_guide_", "")
        guide = guide_mgr.get_guide_by_id(guide_id)
        if guide and cb.message:
            text = TelegramFormatter.format_guide(guide)
            kb = monetization_engine.build_guide_keyboard(guide.get("destination"), guide.get("amazon_query"))
            await cb.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

    return router
