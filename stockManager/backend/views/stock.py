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
)
from backend.common.tradingCalendar import get_trading_time_statuses


@require_authentication
@handle_exception
def operations(request: HttpRequest) -> JsonResponse:
    """获取操作列表接口 - GET /api/operations"""
    logger.info(f"operations - 用户: {request.user.username}, IP: {get_client_ip(request)}")
    operations_data = Integrate.get_operations(request.user)
    return json_response(status=ResponseStatus.SUCCESS, data=operations_data)


@require_authentication
@handle_exception
def stocks(request: HttpRequest) -> JsonResponse:
    """获取股票计算结果接口 - GET /api/stocks"""
    logger.info(f"stocks - 用户: {request.user.username}, IP: {get_client_ip(request)}")
    result = Integrate.get_calculated_result(request.user)
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
    
    Integrate.update_income_cash(request.user, income_cash)
    return json_response(status=ResponseStatus.SUCCESS, message="更新收益现金成功")


@require_authentication
@require_methods(['POST'])
@handle_exception
def refresh_dividend(request: HttpRequest) -> JsonResponse:
    """
    刷新除权除息信息接口
    """
    logger.info(f"refresh_dividend - 用户: {request.user.username}, IP: {get_client_ip(request)}")

    codes = Integrate.generate_dividend(request.user)
    return json_response(status=ResponseStatus.SUCCESS, data=codes, message="刷新除权除息信息成功")


@require_authentication
@handle_exception
def watchlist(request: HttpRequest) -> JsonResponse:
    """获取关注列表 - GET /api/watchlist"""
    logger.info(f"watchlist - 用户: {request.user.username}, IP: {get_client_ip(request)}")
    data = Integrate.get_watchlist(request.user)
    return json_response(status=ResponseStatus.SUCCESS, data=data)


@require_superuser
@require_methods(['POST'])
@handle_exception
def clear_cache(request: HttpRequest) -> JsonResponse:
    """清理本应用全部 Redis 缓存 - POST /api/clearCache"""
    logger.info(f"clear_cache - 用户: {request.user.username}, IP: {get_client_ip(request)}")
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