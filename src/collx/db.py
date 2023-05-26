from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String
from sqlalchemy.engine import Engine

metadata_obj = MetaData()
CARD_TABLE = Table(
    "cards",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(254)),
    Column("set_id", ForeignKey("cards.set_id")),
    Column("player_id", ForeignKey("cards.player_id")),
    Column("year", Integer()),
)
PLAYER_TABLE = Table(
    "players",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(254)),
)
SET_TABLE = Table(
    "sets",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(254)),
    Column("collection", String(254)),
)


def get_engine() -> Engine:
    """ "
    Connect to mysql database.
    """
    return create_engine(
        "mysql+pymysql://collx:collx@collx-mysql/collx_prod", future=True
    )
