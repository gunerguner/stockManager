"""用户数据与计算结果缓存"""
from typing import Iterable, cast

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from backend.common.cache import Cache
from backend.common import logger
from backend.common.market import markets_in_codes
from backend.common.utils import format_operations
from backend.common.types import CalculatedResult, CashFlowData, CashFlowList, OperationDict
from backend.models import Operation, Info, CashFlow
from backend.services.cache import keys
from backend.services.cache import operation_codec
from backend.services.cache import refresh_policy


def get_user_operations_cache(user: User) -> OperationDict | None:
    key = keys.KEY_USER_OPERATIONS.format(user_id=user.pk)
    data = cache.get(key)
    return operation_codec.deserialize_operations(data, user) if data else None


def set_user_operations_cache(user: User, operations: OperationDict) -> None:
    key = keys.KEY_USER_OPERATIONS.format(user_id=user.pk)
    data = operation_codec.serialize_operations(operations)
    cache.set(key, data, keys.TTL_USER_DATA)


def clear_user_operations(user_id: int) -> None:
    cache.delete(keys.KEY_USER_OPERATIONS.format(user_id=user_id))


def get_user_cash_info_cache(user: User) -> tuple | None:
    key = keys.KEY_USER_CASH_INFO.format(user_id=user.pk)
    data = cache.get(key)
    return (data['income_cash'], data['cash_flow_list']) if data else None


def set_user_cash_info_cache(user: User, income_cash: float, cash_flow_list: CashFlowList) -> None:
    cache.set(
        keys.KEY_USER_CASH_INFO.format(user_id=user.pk),
        {'income_cash': income_cash, 'cash_flow_list': cash_flow_list},
        keys.TTL_USER_DATA,
    )


def clear_user_cash_info(user_id: int) -> None:
    cache.delete(keys.KEY_USER_CASH_INFO.format(user_id=user_id))


def should_invalidate_calculated_cache(user_codes: Iterable[str]) -> bool:
    return any(
        refresh_policy.should_refresh_market(market)
        for market in markets_in_codes(user_codes)
    )


def get_calculated_target(
    user: User,
    user_codes: Iterable[str] | None = None,
) -> CalculatedResult | None:
    codes = list(user_codes) if user_codes is not None else list(get_user_operations(user).keys())
    cached = cache.get(keys.KEY_CALCULATED_TARGET.format(user_id=user.pk))
    if not cached:
        return None
    if should_invalidate_calculated_cache(codes):
        return None
    return cached


def set_calculated_target(
    user_id: int,
    result: CalculatedResult,
    user_codes: Iterable[str],
) -> None:
    markets = markets_in_codes(user_codes)
    if refresh_policy.any_market_in_trading_hours(markets):
        return
    cache.set(keys.KEY_CALCULATED_TARGET.format(user_id=user_id), result, keys.TTL_CALCULATED_TARGET)


def clear_calculated_target(user_id: int) -> None:
    cache.delete(keys.KEY_CALCULATED_TARGET.format(user_id=user_id))


def clear_all_calculated_targets() -> None:
    deleted_count = Cache.delete_pattern("user:*:calculated_target")
    if deleted_count > 0:
        logger.info(f"[Redis] 价格更新，清除 {deleted_count} 个用户的计算结果缓存")


def get_user_operations(user: User) -> OperationDict:
    cached = get_user_operations_cache(user)
    if cached is not None:
        return cached
    operations = format_operations(Operation.objects.filter(user=user).order_by('date', 'sortOrder', 'id'))
    set_user_operations_cache(user, operations)
    return operations


def get_user_cash_info(user: User) -> tuple[float, CashFlowList]:
    cached = get_user_cash_info_cache(user)
    if cached is not None:
        return cached
    income_info = Info.objects.filter(user=user, info_type=Info.InfoType.INCOME_CASH).first()
    income_cash = float(income_info.value) if income_info else 0.0
    cash_flow_list: CashFlowList = [
        cast(
            CashFlowData,
            {'date': str(flow.transaction_date), 'amount': float(flow.amount)},
        )
        for flow in CashFlow.objects.filter(user=user).order_by('-transaction_date')
    ]
    set_user_cash_info_cache(user, income_cash, cash_flow_list)
    return income_cash, cash_flow_list


def clear_user_cache(user_id: int) -> None:
    clear_user_operations(user_id)
    clear_user_cash_info(user_id)
    clear_calculated_target(user_id)


@receiver([post_save, post_delete], sender=Operation)
@receiver([post_save, post_delete], sender=CashFlow)
@receiver([post_save, post_delete], sender=Info)
def clear_user_cache_on_model_change(sender, instance, **kwargs) -> None:
    if sender == Info and instance.info_type != Info.InfoType.INCOME_CASH:
        return
    if not instance.user_id:
        return
    clear_user_cache(instance.user_id)
    logger.info(f"[Redis] {sender.__name__} 变化，清除用户 {instance.user_id} 的缓存")
