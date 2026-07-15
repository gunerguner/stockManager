from django.http import HttpRequest, JsonResponse

from backend.services.cache import CacheRepository
from backend.services.integrate import Integrate
from backend.common import (
    ResponseStatus,
    logger,
    require_authentication,
    require_superuser,
    get_client_ip,
    json_response,
    require_methods,
    handle_exception,
    parse_json_body,
    authenticated_user,
)
from backend.common.tradingCalendar import get_trading_time_statuses
from backend.models import WatchItem


@require_authentication
@handle_exception
def operations(request: HttpRequest) -> JsonResponse:
    """获取操作列表接口 - GET /api/operations"""
    user = authenticated_user(request)
    logger.info(f"operations - 用户: {user.username}, IP: {get_client_ip(request)}")
    operations_data = Integrate.get_operations(user)
    return json_response(status=ResponseStatus.SUCCESS, data=operations_data)


@require_authentication
@handle_exception
def stocks(request: HttpRequest) -> JsonResponse:
    """获取股票计算结果接口 - GET /api/stocks"""
    user = authenticated_user(request)
    logger.info(f"stocks - 用户: {user.username}, IP: {get_client_ip(request)}")
    result = Integrate.get_calculated_result(user)
    return json_response(status=ResponseStatus.SUCCESS, data=result)


@require_authentication
@require_methods(['POST'])
@parse_json_body
@handle_exception
def update_income_cash(request: HttpRequest, data: dict) -> JsonResponse:
    """
    更新收益现金接口（逆回购等收入）
    """
    income_cash = data.get("incomeCash")
    
    if income_cash is None:
        return json_response(status=ResponseStatus.ERROR, message="参数incomeCash不能为空")
    
    Integrate.update_income_cash(authenticated_user(request), income_cash)
    return json_response(status=ResponseStatus.SUCCESS, message="更新收益现金成功")


@require_authentication
@require_methods(['POST'])
@handle_exception
def refresh_dividend(request: HttpRequest) -> JsonResponse:
    """
    刷新除权除息信息接口
    """
    user = authenticated_user(request)
    logger.info(f"refresh_dividend - 用户: {user.username}, IP: {get_client_ip(request)}")

    codes = Integrate.generate_dividend(user)
    return json_response(status=ResponseStatus.SUCCESS, data=codes, message="刷新除权除息信息成功")


@require_authentication
@handle_exception
def watchlist(request: HttpRequest) -> JsonResponse:
    """获取关注列表 - GET /api/watchlist"""
    user = authenticated_user(request)
    logger.info(f"watchlist - 用户: {user.username}, IP: {get_client_ip(request)}")
    data = Integrate.get_watchlist(user)
    return json_response(status=ResponseStatus.SUCCESS, data=data)


@require_authentication
@require_methods(['POST'])
@parse_json_body
@handle_exception
def update_watch_hidden(request: HttpRequest, data: dict) -> JsonResponse:
    """设置关注项隐藏状态 - POST /api/watchlist/hidden"""
    code = data.get("code")
    hidden = data.get("hidden")
    if not code:
        return json_response(status=ResponseStatus.ERROR, message="参数code不能为空")
    if not isinstance(hidden, bool):
        return json_response(status=ResponseStatus.ERROR, message="参数hidden必须为布尔值")

    try:
        Integrate.set_watch_hidden(authenticated_user(request), code, hidden)
    except WatchItem.DoesNotExist:
        return json_response(status=ResponseStatus.ERROR, message="关注项不存在")

    return json_response(status=ResponseStatus.SUCCESS, message="更新隐藏状态成功")


@require_superuser
@require_methods(['POST'])
@handle_exception
def clear_cache(request: HttpRequest) -> JsonResponse:
    """清理本应用全部 Redis 缓存 - POST /api/clearCache"""
    user = authenticated_user(request)
    logger.info(f"clear_cache - 用户: {user.username}, IP: {get_client_ip(request)}")
    deleted_count = CacheRepository.clear_all()
    return json_response(
        status=ResponseStatus.SUCCESS,
        message="缓存已清理",
        data={"deletedCount": deleted_count},
    )


@require_authentication
@handle_exception
def trading_status(request: HttpRequest) -> JsonResponse:
    """获取交易状态 Tag 数据 - GET /api/tradingStatus"""
    data = get_trading_time_statuses()
    return json_response(status=ResponseStatus.SUCCESS, data=data)
