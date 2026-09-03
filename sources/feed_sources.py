import re
import asyncio
import logging
from typing import List, Optional, Any
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from .base_source import BaseSource, RawDeal

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
}


class RSSFeedSource(BaseSource):
    def __init__(self, name: str, feed_url: str, default_category: Optional[str] = None):
        super().__init__(name)
        self.feed_url = feed_url
        self.default_category = default_category

    async def fetch(self) -> List[RawDeal]:
        deals: List[RawDeal] = []
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout) as session:
                async with session.get(self.feed_url) as resp:
                    if resp.status != 200:
                        logger.warning(f"[{self.name}] HTTP Error {resp.status} fetching feed {self.feed_url}")
                        return deals
                    content = await resp.read()

            # Parse with feedparser in a threadpool so we don't block asyncio
            loop = asyncio.get_running_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, content)

            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                if not title or not link:
                    continue

                summary = entry.get("summary", "") or ""
                # Clean html tags for description
                clean_desc = ""
                if summary:
                    soup = BeautifulSoup(summary, "html.parser")
                    clean_desc = soup.get_text(separator=" ").strip()

                image_url = self._extract_image(entry, summary)
                published = entry.get("published", "") or entry.get("updated", "")

                deal = RawDeal(
                    title=title,
                    original_url=link,
                    source=self.name,
                    description=clean_desc,
                    image_url=image_url,
                    published_at=published,
                    raw_category=self.default_category
                )
                deals.append(deal)

        except Exception as e:
            logger.error(f"[{self.name}] Error fetching feed {self.feed_url}: {e}")

        return deals

    def _extract_image(self, entry: Any, summary_html: str) -> Optional[str]:
        # 1. Check enclosures
        enclosures = entry.get("enclosures", [])
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")

        # 2. Check media_content or media_thumbnail
        media_content = entry.get("media_content", [])
        if media_content and isinstance(media_content, list):
            url = media_content[0].get("url")
            if url:
                return url

        media_thumb = entry.get("media_thumbnail", [])
        if media_thumb and isinstance(media_thumb, list):
            url = media_thumb[0].get("url")
            if url:
                return url

        # 3. Search <img> tag in HTML summary
        if summary_html:
            match = re.search(r'<img[^>]+src=[\"\']([^\"\']+)[\"\']', summary_html, re.IGNORECASE)
            if match:
                return match.group(1)

        return None


def get_all_deal_sources() -> List[BaseSource]:
    """
    Returns the list of active curated deal sources.
    """
    return [
        # Dedicated Error Fares Feed
        RSSFeedSource(
            name="Fly4free Error Fares",
            feed_url="https://www.fly4free.com/flight-deals/error-fare/feed/",
            default_category="🚨 ERRORE DI PREZZO"
        ),
        # Italian Market (Flights, Packages, Luxury on budget)
        RSSFeedSource(
            name="PiratinViaggio",
            feed_url="https://www.piratinviaggio.it/feed",
            default_category=None
        ),
        # Low Cost Flights Europe & Worldwide
        RSSFeedSource(
            name="TravelFree",
            feed_url="https://travelfree.info/feed/",
            default_category="✈️ VOLO LOW COST"
        ),
        # European Flight Deals
        RSSFeedSource(
            name="Fly4free Europe",
            feed_url="https://www.fly4free.com/flight-deals/europe/feed/",
            default_category="✈️ VOLO LOW COST"
        ),
        # Holiday Packages
        RSSFeedSource(
            name="HolidayPirates",
            feed_url="https://www.holidaypirates.com/feed",
            default_category="🏝️ PACCHETTO VACANZA"
        ),
    ]
