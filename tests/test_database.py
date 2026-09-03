import os
import pytest
from database import Database


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_deals.db"
    return Database(str(db_file))


def test_database_save_and_deduplicate(temp_db):
    deal = {
        "title": "Milano a Madrid da 15€",
        "original_url": "https://example.com/madrid-15",
        "category": "VOLO LOW COST",
        "price": "15€",
        "departure": "Milano",
        "destination": "Madrid",
        "is_error_fare": False
    }

    # First insert should succeed
    inserted = temp_db.save_deal(deal)
    assert inserted is True

    deal_id = Database.generate_deal_id(deal["title"], deal["original_url"])
    assert temp_db.is_deal_posted(deal_id) is True

    # Duplicate insert should be ignored
    inserted_again = temp_db.save_deal(deal)
    assert inserted_again is False

    # Check recent deals
    recent = temp_db.get_recent_deals(limit=5)
    assert len(recent) == 1
    assert recent[0]["destination"] == "Madrid"


def test_database_guide_history(temp_db):
    guide_id = "test_guide_1"
    assert temp_db.was_guide_recently_published(guide_id) is False

    temp_db.record_guide_published(guide_id, "Titolo Guida", "GUIDA")
    assert temp_db.was_guide_recently_published(guide_id) is True
