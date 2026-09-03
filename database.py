import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


class Database:
    def __init__(self, db_path: str = "deals.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Deals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id TEXT PRIMARY KEY,
                    source TEXT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price TEXT,
                    departure TEXT,
                    destination TEXT,
                    original_url TEXT NOT NULL,
                    affiliate_url TEXT,
                    image_url TEXT,
                    is_error_fare BOOLEAN DEFAULT 0,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Guides history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guides_history (
                    guide_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Bot subscribers (optional: for users who want direct DM alerts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notify_error_fares BOOLEAN DEFAULT 1,
                    notify_all_deals BOOLEAN DEFAULT 0
                )
            """)
            conn.commit()

    @staticmethod
    def generate_deal_id(title: str, url: str) -> str:
        raw = f"{title.strip().lower()}_{url.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def is_deal_posted(self, deal_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM deals WHERE id = ?", (deal_id,))
            return cursor.fetchone() is not None

    def save_deal(self, deal: Dict[str, Any]) -> bool:
        deal_id = deal.get("id") or self.generate_deal_id(deal["title"], deal["original_url"])
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO deals (
                    id, source, title, category, price,
                    departure, destination, original_url, affiliate_url,
                    image_url, is_error_fare, published_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deal_id,
                deal.get("source", "generic"),
                deal["title"],
                deal.get("category", "VOLO LOW COST"),
                deal.get("price"),
                deal.get("departure"),
                deal.get("destination"),
                deal["original_url"],
                deal.get("affiliate_url"),
                deal.get("image_url"),
                1 if deal.get("is_error_fare") else 0,
                deal.get("published_at", datetime.now(timezone.utc).isoformat())
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_recent_deals(self, limit: int = 5, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT * FROM deals 
                    WHERE category = ? 
                    ORDER BY published_at DESC 
                    LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT * FROM deals 
                    ORDER BY published_at DESC 
                    LIMIT ?
                """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_error_fares(self, limit: int = 5) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM deals 
                WHERE is_error_fare = 1 
                ORDER BY published_at DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def record_guide_published(self, guide_id: str, title: str, category: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO guides_history (guide_id, title, category, published_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (guide_id, title, category))
            conn.commit()

    def was_guide_recently_published(self, guide_id: str, days: int = 14) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM guides_history 
                WHERE guide_id = ? 
                  AND julianday('now') - julianday(published_at) < ?
            """, (guide_id, days))
            return cursor.fetchone() is not None

    def add_subscriber(self, user_id: int, username: Optional[str], first_name: Optional[str]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO subscribers (user_id, username, first_name)
                VALUES (?, ?, ?)
            """, (user_id, username, first_name))
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM deals")
            total_deals = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM deals WHERE julianday('now') - julianday(published_at) < 1")
            deals_24h = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM deals WHERE is_error_fare = 1")
            total_errors = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM subscribers")
            total_subscribers = cursor.fetchone()[0]

            return {
                "total_deals": total_deals,
                "deals_24h": deals_24h,
                "total_errors": total_errors,
                "total_subscribers": total_subscribers,
            }
