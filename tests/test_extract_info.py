from unittest import mock
from collx.extract import extract_data

no_year_or_set = {"title": "kyle lewis - aaron"}


bad_set_year_order = {
    "title": "justin crawford 1st chrome rookie card rc 2023 bowman prospects bcp-3 phillies",
}


good_year_and_set = {
    "title": "2021 topps update shane mcclanahan debut black parallel 70",
}


def test_extract_player_from_title():
    """Basic case in which player name follows set and preceeds team"""
    test_data = {
        "title": "2023 bowman colby thomas 1st bowman green refractor autograph 4299 sp on card",
    }
    assert extract_data(test_data).get("player") == "Colby Thomas"


def test_extract_player_from_compound_set():
    """Player name follows a multi word set"""
    test_data = {"title": "2012 panini cooperstown #58 ted williams boston red sox"}
    result = extract_data(test_data)
    assert result.get("player") == "Ted Williams"
    assert result.get("set") == "2012 Panini Cooperstown"


@mock.patch("collx.extract._extract_possible_set_from_title")
@mock.patch("collx.extract._extract_possible_player_from_title")
def test_extract_from_full_data(mock_xtract_player, mock_xtract_set):
    """
    Don't use unnecessary extracts if we already have the info we need
    """
    # These should not be used, but help w/ debugging
    mock_xtract_set.return_value = "abc"

    test_data = {
        "card_id": None,
        "title": "2023 bowman colby thomas 1st bowman green refractor autograph 4299 sp on card",
        "image_url": "https://i.ebayimg.com/images/g/fXYAAOSwkytkWmR9/s-l1600.jpg",
        "url": "https://www.ebay.com/itm/195753735025",
        "condition": "Fair",
        "date_stamp": 1683809265,
        "price": 90.0,
        "source": "ebay",
        "source_id": "ebay-195753735025",
        "grader_id": None,
        "grade": None,
        "certification_number": None,
        "autographed": True,
        "sites": ["https://www.ebay.com/itm/195753735025"],
        "alternates": [],
        "attributes": {
            "Condition": "Used An item that has been used previously See the sellers listing for full details and Read moreabout the conditionUsed An item that has been used previously See the sellers listing for full details and description of any imperfectionsSee all condition definitionsopens in a new window or tab",
            "League": "Major League MLB",
            "Autographed": "Yes",
            "Set": "2023 Bowman",
            "Player/Athlete": "Colby Thomas",
            "Graded": "No",
            "Type": "Sports Trading Card",
            "Sport": "Baseball",
            "Parallel/Variety": "Green Refractor",
            "Manufacturer": "Bowman",
            "Features": "Serial Numbered Short Print Auto",
            "Team": "Oakland Athletics",
            "Card Number": "CPA-CT",
            "Season": "2023",
        },
    }
    result = extract_data(test_data)
    assert result.get("year") == 2023
    assert result.get("player") == "Colby Thomas"
    mock_xtract_set.assert_not_called()
    mock_xtract_player.assert_not_called()


def test_fallback_to_name():
    """No set present before name should currently get only get year and player"""
    result = extract_data(bad_set_year_order)
    assert not result.get("set")
    assert result.get("player") == "Justin Crawford"
    assert result.get("year") == 2023


def test_extract_year():
    assert extract_data(good_year_and_set).get("year") == 2021


def test_extract_year_incorrect_order():
    """Year does not appear before title. Since year still exists, should be returned."""
    assert extract_data(bad_set_year_order).get("year") == 2023


def test_no_year():
    assert not extract_data(no_year_or_set).get("year")


def test_extract_set():
    assert extract_data(good_year_and_set).get("set") == "2021 Topps Update"


def test_no_set():
    assert not no_year_or_set.get("set")
