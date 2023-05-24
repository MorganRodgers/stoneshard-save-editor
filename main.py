#!/usr/bin/env python3
from pathlib import Path
from typing import Dict
import configparser
import hashlib
import json
import sys
import zlib


def load_config() -> Dict:
    config = {"character": {}, "inventory": {}, "filesystem": {}}

    parser = configparser.ConfigParser()
    parser.read("config.ini")

    for section in config.keys():
        for key, value in (parser[section] or {}).items():
            config[section][key] = value

    # If output file is not set don't clobber the input
    if "output_save_file_path" not in config["filesystem"]:
        config["filesystem"]["output_save_file_path"] = (
            config["filesystem"]["input_save_file_path"] + ".new"
        )
    elif config["filesystem"]["output_save_file_path"] == "overwrite":
        config["filesystem"]["output_save_file_path"] = config["filesystem"][
            "input_save_file_path"
        ]

    return config


def decompress_stoneshard_sav(sav_path: Path) -> Dict:
    if not sav_path.exists():
        print(f"Unable to find save file at {sav_path}")
        sys.exit(1)

    content = sav_path.open("rb").read()
    decompressed_content = zlib.decompress(content)
    decoded_content = decompressed_content[:-33].decode("utf8")

    return json.loads(decoded_content)


def generate_salt(sav_path: Path):
    dir_2 = sav_path.parent.name
    dir_1 = sav_path.parent.parent.name

    return f"stOne!characters_v1!{dir_1}!{dir_2}!shArd"


def compress_stoneshard_sav(content: Dict, sav_path: Path) -> Dict:
    salt = generate_salt(sav_path)
    serialized_content = json.dumps(content)
    checksum = (
        hashlib.md5((serialized_content + salt).encode("utf8"))
        .hexdigest()
        .encode("utf8")
    )
    compressed_content = zlib.compress(
        serialized_content.encode("utf8") + checksum + b"\x00"
    )

    with sav_path.open("wb") as output_file:
        output_file.write(compressed_content)

    print(f"Updated save file written to {sav_path}")


def mutate_character(save_content: Dict, character_config: Dict):
    character = save_content["characterDataMap"]

    for key, value in character_config.items():
        if key == "xp":
            character["XP"] = int(value)
        elif key == "ability_points":
            character["AP"] = int(value)
        elif key == "str":
            character["STR"] = int(value)
        elif key == "level":
            character["LVL"] = int(value)


def mutate_inventory(save_content: Dict, inventory_config: Dict):
    inventory = save_content["inventoryDataList"]
    for key, value, *ignored in inventory:
        if inventory_config["moneybag"] and key == "o_inv_moneybag":
            value["Stack"] = int(inventory_config["moneybag"])


def main():
    config = load_config()

    path = Path(config["filesystem"]["input_save_file_path"]).expanduser()
    save_content = decompress_stoneshard_sav(path)

    mutate_character(save_content, config["character"])

    mutate_inventory(save_content, config["inventory"])

    path = Path(config["filesystem"]["output_save_file_path"]).expanduser()
    compress_stoneshard_sav(save_content, path)


if __name__ == "__main__":
    main()
