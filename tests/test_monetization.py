from monetization import MonetizationEngine


def test_monetization_links():
    engine = MonetizationEngine(
        travelpayouts_marker="123456",
        booking_aid="998877",
        skyscanner_tag="mytag",
        civitatis_id="civ123",
        amazon_tag="amz-21"
    )

    # Flight search URL should contain travelpayouts marker
    flight_url = engine.generate_flight_search_url("Milano", "Tokyo", "https://example.com")
    assert "marker=123456" in flight_url
    assert "origin=Milano" in flight_url or "origin=Milano" in flight_url or "Milano" in flight_url

    # Hotel search URL should contain Booking aid
    hotel_url = engine.generate_hotel_search_url("Parigi")
    assert "aid=998877" in hotel_url
    assert "Parigi" in hotel_url

    # Activities URL should contain Civitatis aff_id
    tours_url = engine.generate_activities_url("Roma")
    assert "aff_id=civ123" in tours_url

    # Amazon travel gear URL should contain Amazon tag
    amazon_url = engine.generate_amazon_travel_gear_url("zaino cabina")
    assert "tag=amz-21" in amazon_url


def test_keyboard_generation():
    engine = MonetizationEngine(travelpayouts_marker="123456", booking_aid="998877")
    kb = engine.build_deal_keyboard(
        original_url="https://example.com/deal",
        departure="Roma",
        destination="New York",
        is_package=False
    )
    # Check button rows
    assert len(kb.inline_keyboard) >= 2
    first_button = kb.inline_keyboard[0][0]
    assert "Prenota Volo" in first_button.text
    assert "tp.media" in first_button.url
