"""
工具函数模块
提供股票数据查询、操作记录处理和分红信息生成等功能
"""
import datetime
import re
import urllib.request
from typing import Dict, List, Optional

import baostock as bs

from .common import logger
from .models import Operation

# 常量定义
STOCK_PRICE_API_URL = 'http://qt.gtimg.cn/q='
MIN_RESPONSE_LENGTH = 10
ENCODING_GB18030 = 'gb18030'


def query_realtime_price(code_list: List[str]) -> Dict[str, List]:
    """
    查询股票实时价格
    
    Args:
        code_list: 股票代码列表
        
    Returns:
        Dict[str, List]: 股票代码到实时数据的映射
        实时数据格式: [名称, 现价, 涨跌额, 涨跌幅, 昨收]
    """
    if not code_list:
        return {}

    try:
        # 构建请求URL
        url = STOCK_PRICE_API_URL + ','.join(code_list) + ','
        
        # 发送请求并获取响应
        response_data = urllib.request.urlopen(url, timeout=10).read()
        response_array = str(response_data, encoding=ENCODING_GB18030).split(';')

        result = {}
        for index, single_response in enumerate(response_array):
            if len(single_response) <= MIN_RESPONSE_LENGTH:
                continue
                
            # 提取引号内的内容
            content_match = re.search(r'\"([^\"]*)\"', single_response)
            if not content_match:
                continue
                
            # 解析股票信息
            stock_info = content_match.group().strip('"').split('~')
            
            if len(stock_info) < 5:
                logger.warning(f"股票 {code_list[index]} 数据格式不完整")
                continue
            
            # 计算涨跌信息
            current_price = _safe_float(stock_info[3])
            yesterday_close = _safe_float(stock_info[4])
            price_offset = current_price - yesterday_close
            
            # 计算涨跌幅
            offset_ratio = _calculate_offset_ratio(price_offset, yesterday_close)
            
            # 组装返回数据: [名称, 现价, 涨跌额, 涨跌幅, 昨收]
            result[code_list[index]] = [
                stock_info[1],
                stock_info[3],
                price_offset,
                offset_ratio,
                stock_info[4]
            ]
            
        return result
        
    except urllib.error.URLError as e:
        logger.error(f"网络请求失败: {e}")
        return {}
    except Exception as e:
        logger.error(f"查询实时价格失败: {e}")
        return {}


def format_operations(operation_list: List[Operation]) -> Dict[str, List[Operation]]:
    """
    格式化操作记录列表,按股票代码分组
    
    Args:
        operation_list: 操作记录列表
        
    Returns:
        Dict[str, List[Operation]]: 股票代码到操作记录列表的映射
    """
    result = {}
    for operation in operation_list:
        if operation.code not in result:
            result[operation.code] = []
        result[operation.code].append(operation)
    
    return result

# ========== 私有辅助函数 ==========

def _safe_float(value: str, default: float = 0.0) -> float:
    """安全地将字符串转换为浮点数"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default


def _calculate_offset_ratio(offset: float, base_price: float) -> str:
    """计算涨跌幅百分比"""
    if base_price == 0.0:
        return "0"
    ratio = (offset / base_price) * 100
    return f"{ratio:.2f}%"
