#!/usr/bin/env python3
from pathlib import Path
from typing import Dict
import hashlib
import json
import zlib


# content = path.open("rb").read()
# decompressed_content = zlib.decompress(content)
# decoded_content = decompressed_content[:-33].decode("utf8")
# suffix = decompressed_content[-33:-1]
# salt = "stOne!characters_v1!character_1!save_1!shArd"
# print(suffix)
# # print(decoded_content)
# # md5(json + salt) + null
# print(hashlib.md5((decoded_content + salt).encode("utf8")).hexdigest())


def decompress_stoneshard_sav(sav_path: Path) -> Dict:
    content = sav_path.open("rb").read()
    decompressed_content = zlib.decompress(content)
    decoded_content = decompressed_content[:-33].decode("utf8")

    return json.loads(decoded_content)  # The json de/serialization


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


def main():
    path = Path("character_1/save_1/data.sav")
    content = decompress_stoneshard_sav(path)
    print(json.dumps(content))
    # compress_stoneshard_sav(content, path)


if __name__ == "__main__":
    main()
