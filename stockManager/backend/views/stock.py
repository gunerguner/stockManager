from django.http import HttpRequest, JsonResponse

from ..services.integrate import Integrate
from ..common import (
    ResponseStatus,
    logger,
    require_authentication,
    get_client_ip,
    json_response,
    require_methods,
    handle_exception,
    parse_json_body,
)


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