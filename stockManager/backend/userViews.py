from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib import auth


import json, logging, sys

@csrf_exempt
def login(request):
    if request.user.is_authenticated:  # 不允许重复登录
        return JsonResponse({"status": 0})
    if request.method == "POST":
        username = json.loads(request.body).get("username")
        password = json.loads(request.body).get("password")
        user_obj = auth.authenticate(username=username, password=password)
        
        if user_obj is not None:
            auth.login(request, user_obj)
            return JsonResponse({"status": 1}, safe=False)
        else :
            return JsonResponse({"status": 0})
        

@csrf_exempt
def logout(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    request.session.flush()
    return JsonResponse({"status": 1})


def currentUser(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 302})

    if request.user.is_authenticated:
        info = {
            "name": request.user.first_name,
            "avatar": "https://gw.alipayobjects.com/zos/antfincdn/XAosXuNZyF/BiazfanxmamNRoxxVxka.png",
            "access": "admin" if request.user.is_superuser else "",
        }
        return JsonResponse({"status": 1, "info": info}, safe=False)

    else:
        return JsonResponse({"status": 0}, safe=False)


    