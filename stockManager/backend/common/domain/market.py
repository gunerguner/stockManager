"""股票市场抽象（CN / HK）"""
import re
from enum import Enum
from typing import Iterable


class Market(str, Enum):
    CN = "cn"
    HK = "hk"


HK_CODE_PATTERN = re.compile(r"^hk\d{5}$")
CN_CODE_PATTERN = re.compile(r"^(sh|sz|bj)\d+$")


def is_hk_code(code: str) -> bool:
    """是否为项目支持的港股通代码格式：hk00700。"""
    return bool(HK_CODE_PATTERN.fullmatch(code or ""))


def hk_api_code(code: str) -> str:
    """转换为 easyquotation hkquote 使用的不带 hk 前缀的 5 位代码。"""
    return code[2:] if is_hk_code(code) else code


def code_to_market(code: str) -> Market:
    return Market.HK if is_hk_code(code) else Market.CN


def split_codes_by_market(codes: Iterable[str]) -> tuple[list[str], list[str]]:
    cn_codes: list[str] = []
    hk_codes: list[str] = []
    for code in codes:
        target = hk_codes if code_to_market(code) == Market.HK else cn_codes
        target.append(code)
    return cn_codes, hk_codes


def markets_in_codes(codes: Iterable[str]) -> set[Market]:
    return {code_to_market(c) for c in codes}


def to_baidu_params(code: str) -> tuple[str, str] | None:
    """转换为百度 opendata 的 (market, pure_code)；非 A 股/港股返回 None。"""
    if is_hk_code(code):
        return "hk", hk_api_code(code)
    if CN_CODE_PATTERN.fullmatch(code or ""):
        return "ab", code[2:]
    return None
