import json
import logging
import sys
from pathlib import Path
from typing import Iterable, Optional
from sqlalchemy.sql.expression import select
from collx.db import get_engine, CARD_TABLE
from collx.extract import extract_data
from collx.match import match_card_info_to_db

LOGGER = logging.getLogger(__file__)


def _query_card_by_id(card_id: int) -> Optional[int]:
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
    # XXX: Use log file instead of stream to handle large amount of output
    total_count = correct_count = 0
    valid_files_count = 0
    for ebay_data_file in list(_get_ebay_data_dir_as_iter()):
        file_specific_count = 0
        LOGGER.info("Checking file: %s", ebay_data_file)
        ebay_data = json.loads(ebay_data_file.read_bytes())
        for ebay_item in ebay_data:
            if (card_id := ebay_item.get("card_id")) and _query_card_by_id(card_id):
                total_count += 1
                file_specific_count += 1
                if extracted_data := extract_data(ebay_item):
                    matched_info = match_card_info_to_db(extracted_data)
                    if matched_info:
                        matched_id, _ = matched_info
                    else:
                        matched_id = None
                    if not card_id == matched_id:
                        LOGGER.debug(
                            "Title: %s and card_id: %s",
                            ebay_item.get("title"),
                            ebay_item.get("card_id"),
                        )
                        LOGGER.debug("Extracted data: %s", extracted_data)
                        LOGGER.debug(
                            "FAILED TO MATCH card_id: %s, extracted: %s, matched_id: %s",
                            card_id,
                            extracted_data,
                            matched_id,
                        )
                    else:
                        correct_count += 1
        if file_specific_count > 500:
            valid_files_count += 1
        LOGGER.info(
            "FAILED: %s, SUCCEEDED: %s, TOTAL: %s",
            total_count - correct_count,
            correct_count,
            total_count,
        )
        if valid_files_count > 4:
            break


def match_unmatched_cards():
    # XXX: Adjust false positives with min match value
    checked = ()
    total_count = match_count = 0
    valid_files_count = 0
    for ebay_data_file in list(_get_ebay_data_dir_as_iter()):
        if not any([check in str(ebay_data_file) for check in checked]):
            file_specific_count = file_match_count = 0
            LOGGER.info("Checking file: %s", ebay_data_file)
            ebay_data = json.loads(ebay_data_file.read_bytes())
            for ebay_item in ebay_data:
                if not ebay_item.get("card_id"):
                    total_count += 1
                    file_specific_count += 1
                    LOGGER.debug(
                        "Title: %s and card_id: %s",
                        ebay_item.get("title"),
                        ebay_item.get("card_id"),
                    )
                    if extracted_data := extract_data(ebay_item):
                        matched_info = match_card_info_to_db(extracted_data)
                        if matched_info:
                            match_count += 1
                            file_match_count += 1
                        else:
                            LOGGER.debug(
                                "FAILED TO MATCH extracted: %s", extracted_data
                            )
            if file_specific_count > 500:
                valid_files_count += 1
            LOGGER.info(
                "FAILED:  %, SUCCEEDED: %s, TOTAL: %s",
                file_specific_count - file_match_count,
                file_match_count,
                file_specific_count,
            )
        LOGGER.info(
            "FAILED:  %, SUCCEEDED: %s, TOTAL: %s",
            total_count - match_count,
            match_count,
            total_count,
        )


def run():
    if sys.argv[1] == "test_accuracy":
        test_accuracy()
    elif sys.argv[1] == "match_cards":
        match_unmatched_cards()


if __name__ == "__main__":
    run()
