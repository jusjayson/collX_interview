from typing import Dict, Optional, Union

from sqlalchemy.sql.expression import join, select

from collx.db import get_engine, CARD_TABLE, PLAYER_TABLE, SET_TABLE


def match_card_info_to_db(card_data: Dict[str, Optional[Union[str, int]]]):
    player_id = card_data.get("player_id")
    card_year = card_data.get("year")
    set_id = card_data.get("set_id")
    with get_engine().begin() as conn:
        return conn.execute(
            select(CARD_TABLE.c.id, CARD_TABLE.c.name).where(
                CARD_TABLE.c.set_id == set_id,
                CARD_TABLE.c.year == card_year,
                CARD_TABLE.c.player_id == player_id,
            )
        ).first()  # Could be more than one
