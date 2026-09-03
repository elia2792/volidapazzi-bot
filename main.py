import asyncio
import logging
import sys
import os
import argparse
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from config import settings
from database import Database
from worker import TravelDealWorker
from bot import get_bot_router


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def create_web_app(worker: TravelDealWorker, db: Database) -> web.Application:
    """
    Lightweight HTTP health-check server for free cloud hosts (Render, Koyeb, Railway).
    Allows keeping the bot alive 24/7 on free tier web services.
    """
    app = web.Application()

    async def handle_root(request):
        stats = db.get_stats()
        return web.json_response({
            "status": "online",
            "service": "Voli Da Pazzi Telegram Bot 24/7",
            "stats": stats
        })

    async def handle_health(request):
        return web.Response(text="OK", status=200)

    async def handle_scan(request):
        # Trigger an immediate scan via HTTP webhook
        published = await worker.run_cycle()
        return web.json_response({"status": "scan_complete", "published_deals": published})

    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    app.router.add_post("/scan", handle_scan)
    return app


async def run_scheduler(worker: TravelDealWorker):
    """
    Runs the 24/7 scheduler executing hourly checks.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        worker.run_cycle,
        "interval",
        minutes=settings.CHECK_INTERVAL_MINUTES,
        id="hourly_deal_scanner",
        replace_existing=True
    )
    scheduler.start()
    logging.info(f"⏰ Scheduler 24/7 attivo: scansione automatica ogni {settings.CHECK_INTERVAL_MINUTES} minuti.")

    # Run initial cycle
    await worker.run_cycle()


async def main():
    setup_logging()
    logger = logging.getLogger("TravelBot")
    logger.info("Avvio Travel & Flight Deals Telegram Bot...")

    parser = argparse.ArgumentParser(description="Bot Telegram Viaggi & Voli Low Cost 24/7")
    parser.add_argument("--scan-once", action="store_true", help="Esegue una sola scansione ed esce")
    parser.add_argument("--test-guides", action="store_true", help="Stampa l'anteprima di una guida monetizzata")
    parser.add_argument("--web-only", action="store_true", help="Avvia solo il server HTTP")
    args = parser.parse_args()

    db = Database(settings.DB_PATH)

    bot = None
    if settings.TELEGRAM_BOT_TOKEN and "YOUR" not in settings.TELEGRAM_BOT_TOKEN:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    else:
        logger.warning("⚠️ TELEGRAM_BOT_TOKEN non configurato o default! Modalità simulazione attiva.")
        bot = Bot(token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")

    worker = TravelDealWorker(bot=bot, db=db)

    try:
        if args.scan_once:
            logger.info("Esecuzione scansione singola...")
            published = await worker.run_cycle()
            logger.info(f"Scansione completata: {published} nuove offerte pubblicate.")
            stats = db.get_stats()
            logger.info(f"Stato Database: {stats}")
            return

        if args.test_guides:
            from guide_manager import GuideManager
            from formatter import TelegramFormatter
            gm = GuideManager(db)
            guide = gm.get_next_guide_to_publish()
            if guide:
                print("\n" + "="*50)
                print("ANTEPRIMA GUIDA MONETIZZATA:")
                print("="*50)
                print(TelegramFormatter.format_guide(guide))
                print("="*50 + "\n")
            return

        # Start HTTP Web Server (for cloud platforms like Render / Koyeb / Railway)
        port = int(os.environ.get("PORT", 8080))
        app = await create_web_app(worker, db)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"🌐 Server Web attivo su porta {port} (Endpoint: /health, /)")

        # Continuous 24/7 Daemon Mode with Scheduler
        dp = Dispatcher()
        dp.include_router(get_bot_router(db))

        asyncio.create_task(run_scheduler(worker))

        if settings.TELEGRAM_BOT_TOKEN and "YOUR" not in settings.TELEGRAM_BOT_TOKEN:
            logger.info("🤖 Bot in ascolto comandi Telegram (/start, /offerte, /errori, /guide)...")
            await dp.start_polling(bot)
        else:
            logger.info("ℹ️ Bot in esecuzione in modalità scheduler continua.")
            while True:
                await asyncio.sleep(3600)

    finally:
        if bot and bot.session:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Arresto del bot.")
