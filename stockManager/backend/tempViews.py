from django.http import HttpResponse, JsonResponse

from .convert import *

def convert_from_excel(request):
    import_excel("xueqiu.csv")

    return HttpResponse()

def make_tag(request):
    make_stock_tag()

    return HttpResponse()