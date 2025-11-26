"""
股票视图模块
处理股票相关的 API 请求
"""
import json
from django.http import HttpRequest, JsonResponse

from ..models import Info
from ..services.integrate import Integrate
# 导入公共组件
from ..common import (
    ResponseStatus,
    logger,
    require_authentication,
    get_client_ip,
    json_response,
    require_methods,
)

@require_authentication
def show_stocks(request: HttpRequest) -> JsonResponse:
    """
    获取股票数据接口
    返回当前用户的所有股票的计算数据
    """
    try:
        logger.info(f"show_stocks - 用户: {request.user.username}, IP: {get_client_ip(request)}")
        
        merged_data = Integrate.calculate_target(request.user)
        
        return json_response(status=ResponseStatus.SUCCESS, data=merged_data)
    except Exception as e:
        logger.error(f"获取股票数据失败: {str(e)}", exc_info=True)
        return json_response(status=ResponseStatus.ERROR, message="获取股票数据失败")


@require_authentication
@require_methods(['POST'])
def update_income_cash(request: HttpRequest) -> JsonResponse:
    """
    更新收益现金接口（逆回购等收入）
    """
    try:
        request_data = json.loads(request.body)
        income_cash = request_data.get("incomeCash")
        
        if income_cash is None:
            return json_response(status=ResponseStatus.ERROR, message="参数incomeCash不能为空")
        
        Info.objects.update_or_create(
            user=request.user,
            info_type=Info.InfoType.INCOME_CASH,
            defaults={'value': str(income_cash)}
        )
        # 清除缓存，确保下次获取时使用最新数据
        Integrate.clear_cache(request.user.id)
        logger.info(f"用户 {request.user.username} 更新收益现金: {income_cash}")
        
        return json_response(status=ResponseStatus.SUCCESS, message="更新收益现金成功")
    except json.JSONDecodeError:
        logger.error("更新收益现金请求JSON解析失败")
        return json_response(status=ResponseStatus.ERROR, message="请求数据格式错误")
    except Exception as e:
        logger.error(f"更新收益现金失败: {str(e)}", exc_info=True)
        return json_response(status=ResponseStatus.ERROR, message="更新收益现金失败")


@require_authentication
@require_methods(['POST'])
def refresh_divident(request: HttpRequest) -> JsonResponse:
    """
    刷新除权除息信息接口
    """
    try:
        logger.info(f"refresh_divident - 用户: {request.user.username}, IP: {get_client_ip(request)}")
        
        # 使用分红服务生成分红数据
        codes = Integrate.generate_dividend(request.user)
        
        return json_response(status=ResponseStatus.SUCCESS, data=codes, message="刷新除权除息信息成功")
    except Exception as e:
        logger.error(f"刷新除权除息信息失败: {str(e)}", exc_info=True)
        return json_response(status=ResponseStatus.ERROR, message="刷新除权除息信息失败")


