#!/usr/bin/env python3
from pathlib import Path
from typing import Dict
import hashlib
import json
import zlib


def decompress_stoneshard_sav(sav_path: Path) -> Dict:
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

    with Path("data.sav.altered").open("wb") as output_file:
        output_file.write(compressed_content)


def mutate_character(save_content: Dict, character_config: Dict):
    character = save_content["characterDataMap"]

    for key, value in character_config.items():
        if key == "xp":
            character["XP"] = value
        elif key == "ability_points":
            character["AP"] = value
        elif key == "str":
            character["STR"] = value
        elif key == "level":
            character["LVL"] = value


def mutate_inventory(save_content: Dict, inventory_config: Dict):
    inventory = save_content["inventoryDataList"]
    for key, value, *ignored in inventory:
        if inventory_config["moneybag"] and key == "o_inv_moneybag":
            value["Stack"] = inventory_config["moneybag"]


def main():
    path = Path("character_1/exitsave_1/data.sav")

    inventory_config = {"moneybag": 1998}  # todo load from json
    character_config = {
        "xp": 60000,
        "ability_points": 20,
    }  # todo load from json

    save_content = decompress_stoneshard_sav(path)

    mutate_character(save_content, character_config)

    mutate_inventory(save_content, inventory_config)

    compress_stoneshard_sav(save_content, path)


if __name__ == "__main__":
    main()
