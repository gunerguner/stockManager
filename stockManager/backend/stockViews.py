#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json, logging, sys

from .models import Operation, Info
from .utils import *
from .integrate import Integrate

# Create your views here.

def hello(request):
    return HttpResponse("Hello world! ")

def show_stocks(request):

    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    logging.info(sys._getframe().f_code.co_name + " " + get_ip(request))

    stock_caculator = Integrate.caculator(request.user.username,True)
    merged_data = stock_caculator.caculate_target()

    return JsonResponse(
        {"status": 1, "data": merged_data},
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )

@csrf_exempt
def update_origin_cash(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    try:
        cash = json.loads(request.body).get("cash")
        Info.objects.filter(key="originCash").update(value=cash)
    except:
        return JsonResponse({"status": 0})

    return JsonResponse({"status": 1})

@csrf_exempt
def update_income_cash(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    try:
        incomeCash = json.loads(request.body).get("incomeCash")
        Info.objects.filter(key="incomeCash").update(value=incomeCash)
    except:
        return JsonResponse({"status": 0})

    return JsonResponse({"status": 1})

@csrf_exempt
def refresh_divident(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    stock_caculator = Integrate.caculator(request.user.username,False)
    codes = stock_caculator.generate_dividend()

    return JsonResponse(
        {"status": 1, "data": codes},
        safe=False,
        json_dumps_params={"ensure_ascii": False},
    )

