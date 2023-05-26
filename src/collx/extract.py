import datetime as dt
import re
from typing import Dict, Optional, List, Tuple, Union

from sqlalchemy.sql.expression import select
from thefuzz import fuzz

from collx.db import get_engine, CARD_TABLE, PLAYER_TABLE, SET_TABLE
from collx.utils import capitalize_separated_name

# from collx.extract import query_for_double; query_for_double()


def query_for_double():
    with get_engine().begin() as conn:
        results = conn.execute(select(SET_TABLE.c.name).distinct())
        results = [re.sub(r"\d{4}", "", info[0]) for info in results]
        print(results[0:100])


def _query_for_set_name(name):
    with get_engine().begin() as conn:
        return conn.execute(
            select(SET_TABLE.c.name, SET_TABLE.c.id)
            .where(SET_TABLE.c.name.like(f"%{name}%"))
            .distinct()
        ).all()


def _query_for_player_name(name):
    with get_engine().begin() as conn:
        return conn.execute(
            select(PLAYER_TABLE.c.name, PLAYER_TABLE.c.id)
            .where(PLAYER_TABLE.c.name.like(f"%{name}%"))
            .distinct()
        ).all()


def _validate_item_from_matches(
    item: str, db_matches: List[Tuple[str, int]]
) -> Optional[str]:
    ordered_db_matches = sorted(
        [
            (*db_match[0:2], fuzz.token_sort_ratio(item, db_match[0]))
            for db_match in db_matches
        ],
        key=lambda info: info[-1],
        reverse=True,
    )
    if ordered_db_matches:
        return ordered_db_matches[0][0:2]
    return [None, None]


def _extract_possible_player_from_title(title: str) -> Optional[str]:
    name_pattern = r"[^\d\W]+\s+[^\d\W]+"
    name_match = None
    name_db_matches = []
    while title:
        name_match = (match := re.search(name_pattern, title)) and match[0]
        if not name_match:
            break
        name_db_matches = _query_for_player_name(name_match)
        if name_db_matches:
            break
        title = (
            (split_title := title.split(" "))
            and len(split_title) > 2
            and " ".join(split_title[1:])
        )
    return name_match, name_db_matches


def _extract_possible_set_from_title(title: str, year: int) -> Optional[str]:
    # XXX: Refactor to use sliding window as with extract_player
    card_set_pattern = rf"{year}\s?\w+"
    card_set_name = None
    set_db_matches = []
    while True:
        set_match = (match := re.search(card_set_pattern, title)) and match[0]
        if not set_match:
            break
        if possible_set_db_matches := _query_for_set_name(f"{set_match}"):
            card_set_name = set_match
            set_db_matches = possible_set_db_matches
        else:
            break
        card_set_pattern += r"\s+\w+"
    return card_set_name, set_db_matches


def _extract_year_from_title(title: str) -> Optional[int]:
    # XXX: Use sliding window to try multiple numbers if one fails to be valid date
    year = (match := re.search(r"\d{4}", title)) and match[0]
    if year and 1900 <= int(year) <= 3000:  # Reduce false positives
        return year
    return None


def extract_data(
    data: Dict[str, Optional[Union[str, int, float, bool]]]
) -> Dict[str, Optional[Union[str, int, float, bool]]]:
    """
    Reuse or extract (from tile)` required trading card information (if available).

    Note: If there is a high chance of an extraction being a false positive, we avoid
    returning anything for said key, value.
    """
    card_set_name = card_set_id = None
    card_player_name = card_player_id = None
    if not data and data.get("title"):
        raise ValueError(f"No title in data: {data}")

    parsed_title = data.get("title").lower()
    if not (
        card_year := (epoch := data.get("date_stamp"))
        and (converted_year := dt.datetime.fromtimestamp(epoch).year)
        and str(converted_year)
    ):
        card_year = _extract_year_from_title(parsed_title)

    if possible_card_set_name := data.get("attributes", {}).get(
        "Set"
    ):  # This may not match what's in db
        set_db_matches = _query_for_set_name(possible_card_set_name)
    elif card_year:
        possible_card_set_name, set_db_matches = _extract_possible_set_from_title(
            parsed_title, card_year
        )
    else:
        set_db_matches = []

    if set_db_matches:
        card_set_name, card_set_id = _validate_item_from_matches(
            possible_card_set_name, set_db_matches
        )

    if card_set_name:
        parsed_title = parsed_title.replace(card_set_name.lower(), "")
    elif card_year:
        parsed_title = parsed_title.replace(card_year, "")

    if possible_card_player_name := data.get("attributes", {}).get(
        "Player/Athlete"
    ):  # This may not match what's in db
        player_db_matches = _query_for_player_name(possible_card_player_name)
    else:
        (
            possible_card_player_name,
            player_db_matches,
        ) = _extract_possible_player_from_title(parsed_title)
    if player_db_matches:
        card_player_name, card_player_id = _validate_item_from_matches(
            possible_card_player_name, player_db_matches
        )

    return {
        "year": card_year and int(card_year),
        "set": card_set_name and capitalize_separated_name(card_set_name),
        "set_id": card_set_id,
        "player": card_player_name and capitalize_separated_name(card_player_name),
        "player_id": card_player_id,
    }
