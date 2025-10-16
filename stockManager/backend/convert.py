import pandas as pd
import baostock as bs
import os, datetime
import math

from .models import Operation, StockMeta

def import_excel(path):
    # 解析交易记录文件，这块不具有通用性
    bs.login()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    df = pd.read_csv(current_dir + "/" + path, header=None)
    first_year_map = {}
    for row in df.values:

        code = row[1].lower()
        conditions = lambda x: {x == "买入": "BUY", x == "卖出": "SELL", x == "除权除息": "DV"}

        opType = conditions(row[3])[True]

        if (code.startswith("sh") or code.startswith("sz")) and opType != "DV":
            date = row[4]
            price = row[5] if math.isnan(row[10]) else row[10]
            count = row[6]
            fee = row[9]

            if code not in first_year_map.keys():
                first_year_map[code] = "3000"

            if date[0:4] < first_year_map[code]:
                first_year_map[code] = date[0:4]

            Operation.objects.create(
                date=date,
                code=code,
                operationType=opType,
                price=price,
                count=count,
                fee=fee,
            )


    bs.logout()


def make_stock_tag():
    codes = Operation.objects.distinct().values("code")
    codes = list(map(lambda x: x["code"], codes))

    for code in codes:
        stockType = "OTHER"
        if code.startswith("sz150"):
            stockType = "FUNDAB"
        elif code.startswith("sz15") or code.startswith("sz16") or code.startswith("sh50"):
            stockType = "FUNDIN"
        elif code.startswith("sh11") or code.startswith("sz12"):
            stockType = "CONV"
        elif code.startswith("sh688"):
            stockType = "SH688"
        elif code.startswith("sz300"):
            stockType = "SZ300"
        elif code.startswith("sz00"):
            stockType = "SZ00"
        elif code.startswith("sh60"):
            stockType = "SH60"

        
        StockMeta.objects.create(code=code, stockType=stockType)

    return