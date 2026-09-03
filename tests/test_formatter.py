from formatter import TelegramFormatter


def test_format_error_fare():
    deal = {
        "title": "Error Fare: Roma a Miami a soli 189€ A/R",
        "category": "🚨 ERRORE DI PREZZO",
        "price": "189€",
        "departure": "Roma",
        "destination": "Miami",
        "is_error_fare": True,
        "is_italy_departure": True,
        "description": "Incredibile errore tariffario con TAP Portugal",
        "destination_emoji": "🇺🇸"
    }
    formatted = TelegramFormatter.format_deal(deal)
    assert "ERRORE DI PREZZO" in formatted
    assert "189€" in formatted
    assert "Roma" in formatted
    assert "Miami" in formatted
    assert "#ErroreDiPrezzo" in formatted


def test_format_guide():
    guide = {
        "title": "Zaino Cabina Ryanair",
        "content": "Ecco come risparmiare senza pagare il trolley."
    }
    formatted = TelegramFormatter.format_guide(guide)
    assert "Zaino Cabina Ryanair" in formatted
    assert "#GuideDiViaggio" in formatted
