from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

import json, logging, sys


@csrf_exempt
def login(request):
    if request.session.get("is_login", None):  # 不允许重复登录
        return JsonResponse({"status": 0})
    if request.method == "POST":
        request.session["is_login"] = True
        return JsonResponse({"status": 1, "currentAuthority": "admin"}, safe=False)

@csrf_exempt
def logout(request):
    if not request.session.get("is_login", None):
        return JsonResponse({"status": 0})

    request.session.flush()
    return JsonResponse({"status": 1})


def currentUser(request):
    if not request.session.get("is_login", None):
        return JsonResponse({"status": 0})
        
    info = {
        "name": "Serati Ma",
        "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
        "userid": "00000001",
        "email": "antdesign@alipay.com",
        "signature": "海纳百川，有容乃大",
        "title": "交互专家",
        "group": "蚂蚁金服－某某某事业群－某某平台部－某某技术部－UED",
    }
    return JsonResponse({"status": 1,"info":info}, safe=False)
