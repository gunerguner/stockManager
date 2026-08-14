"""HKD/CNY 汇率外部数据源（新浪外汇：即期 + 中行历史牌价）"""
import re
from datetime import date
from html.parser import HTMLParser

from backend.datasource.http_client import get_text

_SINA_FX_URL = "https://hq.sinajs.cn/list=fx_shkdcny"
_SINA_REFERER = "https://finance.sina.com.cn/"
_SINA_BOC_URL = "https://biz.finance.sina.com.cn/forex/forex.php"
_SINA_HEADERS = {"Referer": _SINA_REFERER}
_BOC_QUOTE_UNIT = 100.0
_MAX_PAGES = 100

# 表头列：日期, 中行汇买价, 中行钞买价, 中行钞卖价/汇卖价, 央行中间价, 中行折算价
_COL_DATE = 0
_COL_BUY = 1
_COL_MID = 4
_COL_CONVERT = 5


class _BocTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.page_nums: list[int] = []
        self._row: list[str] = []
        self._cell: list[str] = []
        self._in_td = False
        self._in_page_link = False
        self._page_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._in_td = True
            self._cell = []
        elif tag == "a" and (attrs_d.get("class") or "") == "page":
            self._in_page_link = True
            self._page_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._in_td:
            self._row.append("".join(self._cell).strip())
            self._in_td = False
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = []
        elif tag == "a" and self._in_page_link:
            text = "".join(self._page_text).strip()
            if text.isdigit():
                self.page_nums.append(int(text))
            self._in_page_link = False

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._cell.append(data)
        if self._in_page_link:
            self._page_text.append(data)


def _parse_quoted_rate(raw: str) -> float | None:
    text = raw.replace(",", "").replace("\xa0", "").strip()
    if not text or text in ("--", "-", "—"):
        return None
    try:
        per_hundred = float(text)
    except ValueError:
        return None
    if per_hundred <= 0:
        return None
    return per_hundred / _BOC_QUOTE_UNIT


def _pick_row_rate(cells: list[str]) -> float | None:
    for idx in (_COL_MID, _COL_CONVERT, _COL_BUY):
        if idx < len(cells) and (rate := _parse_quoted_rate(cells[idx])) is not None:
            return rate
    return None


def parse_boc_hkd_page(html: str) -> tuple[dict[date, float], int]:
    """解析中行牌价 HTML 表。返回 (日期→每 1 HKD 的 CNY, 总页数)。"""
    parser = _BocTableParser()
    parser.feed(html)
    rates: dict[date, float] = {}
    for cells in parser.rows:
        if len(cells) <= _COL_DATE:
            continue
        try:
            day = date.fromisoformat(cells[_COL_DATE][:10])
        except ValueError:
            continue
        if (rate := _pick_row_rate(cells)) is None:
            continue
        rates[day] = rate
    page_count = max(parser.page_nums) if parser.page_nums else 1
    return rates, page_count


def fetch_hkd_cny_rate() -> float:
    """从新浪外汇获取 HKD/CNY 即期汇率（1 HKD = X CNY）"""
    text = get_text(
        _SINA_FX_URL,
        headers=_SINA_HEADERS,
    )
    if not (match := re.search(r'="([^"]+)"', text)):
        raise ValueError("sina 外汇响应格式异常")
    parts = match.group(1).split(",")
    if len(parts) < 2:
        raise ValueError(f"sina 外汇字段不足: {parts}")
    rate = float(parts[1])
    if rate <= 0:
        raise ValueError(f"无效汇率: {rate}")
    return rate


def fetch_hkd_cny_daily_rates(start: date, end: date) -> dict[date, float]:
    """拉取 [start, end] 中行港币牌价，换算为 1 HKD = X CNY。"""
    if start > end:
        return {}
    merged: dict[date, float] = {}
    page_count = 1
    page = 1
    while page <= page_count and page <= _MAX_PAGES:
        html = get_text(
            _SINA_BOC_URL,
            params={
                "money_code": "HKD",
                "type": "0",
                "startdate": start.isoformat(),
                "enddate": end.isoformat(),
                "page": str(page),
                "call_type": "ajax",
            },
            headers=_SINA_HEADERS,
        )
        page_rates, detected_pages = parse_boc_hkd_page(html)
        if page == 1:
            page_count = min(max(detected_pages, 1), _MAX_PAGES)
        merged.update(page_rates)
        page += 1
    return {day: rate for day, rate in merged.items() if start <= day <= end}
