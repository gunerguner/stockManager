from backend.common.domain.market import (
    Market,
    code_to_market,
    is_hk_code,
    split_codes_by_market,
)


def test_is_hk_code_only_matches_hk_plus_five_digits():
    assert is_hk_code("hk00700") is True
    assert is_hk_code("HK00700") is False
    assert is_hk_code("hk700") is False
    assert is_hk_code("sh600519") is False
    assert is_hk_code("") is False


def test_code_to_market_and_split():
    assert code_to_market("hk00700") == Market.HK
    assert code_to_market("sh600519") == Market.CN
    assert code_to_market("sz000001") == Market.CN
    cn, hk = split_codes_by_market(["sh600519", "hk00700", "bj430047"])
    assert cn == ["sh600519", "bj430047"]
    assert hk == ["hk00700"]
