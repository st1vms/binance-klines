import re
import json
from datab import CryptoPairData


def normalize_symbol_name(s: str) -> str:
    return "_" + s if re.match(r"^\d", s) else s


def denormalize_symbol_name(s: str) -> str:
    return s.replace("_", "")


async def serialize_data_to_json(data: list[CryptoPairData], json_path: str):
    k = {}
    for v in data:
        k[v.symbol] = [l.__dict__ for l in v.klines]

    with open(json_path, "w") as fp:
        json.dump(k, fp, indent=4)
