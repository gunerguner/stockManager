"""共享 HTTP 客户端（百度 opendata、腾讯 gtimg、sina 外汇等）"""
import requests

_DEFAULT_TIMEOUT = 10
_DEFAULT_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
    "AppleWebKit/605.1.15"
)

_session = requests.Session()
_session.headers.setdefault("User-Agent", _DEFAULT_UA)


def get_json(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> dict:
    merged = dict(_session.headers)
    if headers:
        merged.update(headers)
    resp = _session.get(url, params=params, headers=merged, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_text(
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> str:
    merged = dict(_session.headers)
    if headers:
        merged.update(headers)
    resp = _session.get(url, params=params, headers=merged, timeout=timeout)
    resp.raise_for_status()
    return resp.text
