from monetization import MonetizationEngine


def test_monetization_links_enabled():
    engine = MonetizationEngine(
        enable_affiliates=True,
        travelpayouts_marker="773567",
        booking_aid="2400000",
        skyscanner_tag="mytag",
        civitatis_id="civ123",
        amazon_tag="scontai-21"
    )

    flight_url = engine.generate_flight_search_url("Milano", "Tokyo", "https://example.com")
    assert "marker=773567" in flight_url
    assert "origin=Milano" in flight_url

    hotel_url = engine.generate_hotel_search_url("Parigi")
    assert "booking.com" in hotel_url
    assert "Parigi" in hotel_url

    amazon_url = engine.generate_amazon_travel_gear_url("zaino cabina")
    assert "tag=scontai-21" in amazon_url


def test_monetization_links_disabled():
    engine = MonetizationEngine(enable_affiliates=False)

    flight_url = engine.generate_flight_search_url("Milano", "Tokyo", "https://example.com/original-deal")
    assert flight_url == "https://example.com/original-deal"

    hotel_url = engine.generate_hotel_search_url("Parigi")
    assert "aid=" not in hotel_url

    kb = engine.build_deal_keyboard(
        original_url="https://example.com/deal",
        departure="Milano",
        destination="Londra",
        is_package=False
    )
    # Ensure NO Amazon button is present when disabled
    for row in kb.inline_keyboard:
        for btn in row:
            assert "Amazon" not in btn.text
            assert "scontai-21" not in btn.url
            assert "marker=" not in btn.url
