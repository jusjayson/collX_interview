import logging.config
from pathlib import Path
from collx import utils

logging_conf_path = Path(utils.get_config_folder_path(), "logging.conf")

try:
    logging.config.fileConfig(logging_conf_path)
except KeyError:
    msg = "COULD NOT SET UP LOGGING"
    if not logging_conf_path.exist():
        msg = f"{msg}, {logging_conf_path}, does not exist"
    raise Exception(msg)
