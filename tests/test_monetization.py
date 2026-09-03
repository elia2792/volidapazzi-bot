from monetization import MonetizationEngine


def test_monetization_links():
    engine = MonetizationEngine(
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


def test_keyboard_generation():
    engine = MonetizationEngine(travelpayouts_marker="773567", amazon_tag="scontai-21")
    kb_package = engine.build_deal_keyboard(
        original_url="https://www.piratinviaggio.it/vacanza-santorini",
        departure="Roma",
        destination="Santorini",
        is_package=True
    )
    first_btn = kb_package.inline_keyboard[0][0]
    assert first_btn.text == "🏝️ Vedi e Prenota Pacchetto Completo"
    assert first_btn.url == "https://www.piratinviaggio.it/vacanza-santorini"
