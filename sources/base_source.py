from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod


@dataclass
class RawDeal:
    title: str
    original_url: str
    source: str
    description: str = ""
    price: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[str] = None
    raw_category: Optional[str] = None


class BaseSource(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def fetch(self) -> List[RawDeal]:
        """Fetch raw deals from the source."""
        pass
