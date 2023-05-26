import json
import logging
from pathlib import Path
from typing import Iterable
from sqlalchemy.sql.expression import select, join
from collx.db import get_engine, CARD_TABLE, SET_TABLE
from collx.extract import extract_data
from collx.match import match_card_info_to_db

LOGGER = logging.getLogger(__file__)
# engine = get_engine()
# with engine.begin() as conn:
#     card_sets = join(card_table, set_table, card_table.c.set_id == set_table.c.id)
#     results = conn.execute(
#         select(card_table.c.name, set_table.c.name).select_from(card_sets).limit(10)
#     ).all()


def _query_card_by_id(card_id):
    with get_engine().begin() as conn:
        return conn.execute(
            select(CARD_TABLE.c.id).where(CARD_TABLE.c.id == card_id)
        ).first()


def _get_ebay_data_dir_as_iter() -> Iterable[Path]:
    ebay_data_dir = Path(Path(".").parent.parent.parent, "data", "ebay-sales")
    if not ebay_data_dir.exists():
        raise Exception(f"{ebay_data_dir} DNE")
    return ebay_data_dir.iterdir()


def test_accuracy():
    total_count = correct_count = 0
    for ebay_data_file in _get_ebay_data_dir_as_iter():
        ebay_data = json.loads(ebay_data_file.read_bytes())
        for ebay_item in ebay_data:
            if (card_id := ebay_item.get("card_id")) and _query_card_by_id(card_id):
                total_count += 1
                extracted_data = extract_data(ebay_item)
                if extracted_data:
                    # LOGGER.debug("Extracted data: %s", extracted_data)
                    matched_id = (match_card_info_to_db(extracted_data) or {}).get(
                        "card_id"
                    )
                    if not card_id == matched_id:
                        # LOGGER.debug(
                        #     "FAILED TO MATCH card_id: %s, extracted: %s, matched_id: %s",
                        #     card_id,
                        #     extracted_data,
                        #     matched_id,
                        # )
                        pass
                    else:
                        # LOGGER.info("Successfully matched %s, %s", card_id, matched_id)
                        correct_count += 1
        print(
            f"FAILED: {total_count - correct_count}, SUCCEEDED: {correct_count}, TOTAL: {total_count}"
        )


test_accuracy()
