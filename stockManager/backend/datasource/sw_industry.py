"""申万一级行业：同花顺 A 股 F10 行业对比页"""
import re

from backend.common import logger
from backend.datasource.http_client import get_text

_FIELD_URL = "https://basic.10jqka.com.cn/{code}/field.html"
_L1_RE = re.compile(r"三级行业分类：(?:\s|<[^>]+>)*([^\s<]+)\s*--")
_HEADERS = {
    "Referer": "https://basic.10jqka.com.cn/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}
_A_SHARE_PREFIXES = ("sh", "sz", "bj")


def fetch_sw_industry_name(code: str, *, timeout: int = 10) -> str | None:
    """返回申万 2021 一级行业名称；失败返回 None。"""
    if len(code) < 8 or code[:2] not in _A_SHARE_PREFIXES:
        return None
    pure = code[2:]
    try:
        html = get_text(
            _FIELD_URL.format(code=pure),
            headers=_HEADERS,
            timeout=timeout,
            encoding="gbk",
        )
    except Exception as e:
        logger.error(f"同花顺申万一级获取失败 {code}: {e}")
        return None
    if match := _L1_RE.search(html):
        return match.group(1).strip()
    logger.warning(f"同花顺申万一级未解析到一级名称 {code}")
    return None
