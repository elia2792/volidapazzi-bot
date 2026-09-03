import pytest
from classifier import DealClassifier


def test_classify_error_fare():
    title = "🔥 ERROR FARE: Voli A/R per New York da Milano a soli 180€!"
    res = DealClassifier.classify(title)
    assert res["is_error_fare"] is True
    assert "ERRORE DI PREZZO" in res["category"]
    assert res["price"] == "180€"
    assert res["departure"] == "Milano"
    assert res["destination"] == "New York"
    assert res["is_italy_departure"] is True


def test_classify_holiday_package():
    title = "7 notti a Santorini in Hotel 4* con colazione + Volo A/R da Roma a 220€"
    res = DealClassifier.classify(title)
    assert "PACCHETTO" in res["category"]
    assert res["price"] == "220€"
    assert res["is_italy_departure"] is True


def test_classify_low_cost_flight():
    title = "Voli low cost da Bologna a Londra da soli 19€ con Ryanair"
    res = DealClassifier.classify(title)
    assert "VOLO LOW COST" in res["category"]
    assert res["is_error_fare"] is False
    assert res["price"] == "19€"
    assert res["departure"] == "Bologna"
    assert res["destination"] == "Londra"


def test_extreme_low_price_heuristic():
    title = "Voli per Tokyo da Roma a soli 195€"
    res = DealClassifier.classify(title)
    # Tokyo under 230€ should trigger error fare alert
    assert res["is_error_fare"] is True
    assert "ERRORE DI PREZZO" in res["category"]
