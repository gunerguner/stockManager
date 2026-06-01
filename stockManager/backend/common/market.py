"""股票市场抽象（CN / HK）"""
from enum import Enum
from typing import Iterable


class Market(str, Enum):
    CN = "cn"
    HK = "hk"


def code_to_market(code: str) -> Market:
    if code.lower().startswith("hk"):
        return Market.HK
    return Market.CN


def split_codes_by_market(codes: Iterable[str]) -> tuple[list[str], list[str]]:
    cn_codes: list[str] = []
    hk_codes: list[str] = []
    for code in codes:
        if code_to_market(code) == Market.HK:
            hk_codes.append(code)
        else:
            cn_codes.append(code)
    return cn_codes, hk_codes


def markets_in_codes(codes: Iterable[str]) -> set[Market]:
    return {code_to_market(c) for c in codes}
