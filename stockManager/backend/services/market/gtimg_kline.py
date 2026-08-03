"""腾讯 gtimg K 线公共请求与节点解析"""
from __future__ import annotations

from backend.common.market import is_hk_code
from backend.services.market.http_client import get_json

CN_KLINE_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
HK_KLINE_URL = "https://proxy.finance.qq.com/ifzqgtimg/appstock/app/hkfqkline/get"


def kline_url_for_code(code: str) -> str:
    return HK_KLINE_URL if is_hk_code(code) else CN_KLINE_URL


def extract_kline_rows(node: dict, preferred_keys: tuple[str, ...]) -> list[list]:
    """按 preferred_keys 优先取 K 线 list，再回退任意 list-of-list。"""
    for key in preferred_keys:
        if isinstance(value := node.get(key), list) and value and isinstance(value[0], list):
            return value
    for value in node.values():
        if isinstance(value, list) and value and isinstance(value[0], list):
            return value
    return []


def fetch_kline_node(
    code: str,
    *,
    period: str,
    start: str,
    end: str,
    count: int,
    adjust: str,
    timeout: int,
    url: str | None = None,
) -> dict | None:
    """拉取 gtimg K 线并返回单票 data 节点。

    网络/API 错误抛异常（供调用方重试）；空 payload 返回 None。
    """
    endpoint = url or kline_url_for_code(code)
    param = f"{code},{period},{start},{end},{count},{adjust}"
    data = get_json(endpoint, params={"param": param}, timeout=timeout)
    api_code = data.get("code")
    if api_code not in (0, "0", None) and not data.get("data"):
        raise RuntimeError(f"gtimg code={api_code} msg={data.get('msg')}")
    if not (payload := data.get("data") or {}):
        return None
    return node if isinstance(node := next(iter(payload.values())), dict) else None
