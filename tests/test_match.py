from collx.extract import extract_data
from collx.match import match_card_info_to_db


def test_match_card():
    test_data = {
        "card_id": 11540,
        "title": "1959 topps #211 bob blaylock rc",
    }
    extracted_info = extract_data(test_data)
    card_id, _ = match_card_info_to_db(extracted_info)
    assert card_id == test_data.get("card_id")
