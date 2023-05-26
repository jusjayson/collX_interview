from pathlib import Path

PROJECT_NAME = "collx"


def capitalize_separated_name(name):
    return " ".join([part_name.capitalize() for part_name in name.split()])


def get_config_folder_path():
    return Path(Path(".").parent.parent.parent, "config")
