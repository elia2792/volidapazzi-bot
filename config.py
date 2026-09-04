import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram Credentials
    TELEGRAM_BOT_TOKEN: str = "YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHANNEL_ID: str = "@your_travel_channel"  # e.g. @OfferteVoliLowCost or -100xxxxxxxxxx
    TELEGRAM_ADMIN_ID: Optional[int] = None            # Telegram user ID for admin alerts and status

    # Scheduling and Deal Flow
    CHECK_INTERVAL_MINUTES: int = 60                   # Check every hour (24/7)
    MAX_DEALS_PER_RUN: int = 3                         # Max deals posted per run to prevent spam
    PUBLISH_GUIDES_DAILY: bool = True                  # Automatically publish travel tips/guides
    GUIDE_PUBLISH_HOUR: int = 14                       # Preferred hour to post a travel guide (e.g. 14:00)

    # Filter settings
    PRIORITIZE_ITALY: bool = True                      # Boost/prioritize Italian departures
    ALLOW_WORLDWIDE_ERROR_FARES: bool = True           # Always allow crazy global error fares

    # Monetization / Affiliate Settings
    ENABLE_AFFILIATES: bool = False                    # Set to False to suspend affiliate links
    TRAVELPAYOUTS_MARKER: str = "773567"               # Travelpayouts Partner Marker
    BOOKING_AID: str = "2400000"                       # Booking.com Affiliate ID
    SKYSCANNER_AFFILIATE_TAG: str = "travelbot"        # Skyscanner affiliate tracking
    CIVITATIS_AFFILIATE_ID: str = "travelbot"          # Civitatis affiliate tracking
    GETYOURGUIDE_PARTNER_ID: str = "travelbot"         # GetYourGuide tracking ID
    AMAZON_AFFILIATE_TAG: str = "scontai-21"           # Amazon Associates Tag

    # Storage
    DB_PATH: str = "deals.db"
    LOG_LEVEL: str = "INFO"


settings = Settings()
