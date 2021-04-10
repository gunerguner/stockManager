#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json,logging,sys

from .models import Operation
from .utils import *
from .convert import *

# Create your views here.

def index(request):  
    return HttpResponse("Hello world! ")

def show_stocks(request):
    logger = logging.getLogger(__name__)
    logging.info(sys._getframe().f_code.co_name+" "+get_ip(request))

    operations = Operation.objects.all().order_by('date')  #获取所有操作记录
    new_operation_list = format_operations(operations)   #操作记录格式化

    realtime_price_list = query_realtime_price(list(new_operation_list.keys()))  #持仓股票的现价
    merged_data = caculate_target(new_operation_list,realtime_price_list)

    return JsonResponse(merged_data,safe=False, json_dumps_params={'ensure_ascii':False})

def convert_from_excel(request):
    import_excel('xueqiu.csv')

    return HttpResponse()

@csrf_exempt
def refresh_divident(request):

    json_result = json.loads(request.body)
    num = generate_divident(json_result)
        
    response = {'number':num}
    return JsonResponse(response,safe=False, json_dumps_params={'ensure_ascii':False})


def get_ip(request):
    '''获取请求者的IP信息'''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
    return ip
