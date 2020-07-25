import pandas as pd
import baostock as bs
import os,datetime
import math

from .models import Operation

def import_excel(path):
    #解析交易记录文件，这块不具有通用性
    lg = bs.login()
    current_dir = os.path.abspath(os.path.dirname(__file__))
    df=pd.read_csv(current_dir+'/'+path,header=None)
    first_year_map = {}
    for row in df.values:
        
        code = row[1].lower()
        conditions = lambda x: {x == '买入': 'BUY',x == '卖出': 'SELL', x == '除权除息':'DV'}
        
        opType = conditions (row[3])[True]
        
        if (code.startswith('sh') or code.startswith('sz')) and opType != 'DV':
            date = row[4]
            price = row[5] if math.isnan(row[10]) else row[10]
            count = row[6]
            value = price * count
            fee = row[9]

            if code not in first_year_map.keys():
                first_year_map[code] = '3000'

            if date[0:4] < first_year_map[code]:
                first_year_map[code] = date[0:4]

            Operation.objects.create(date=date,code = code,operationType = opType,price = price,count = count,fee = fee)

    for k,v in first_year_map.items():
        generate_divident(k,v)

    bs.logout()


#自动生成除权记录
def generate_divident(code,first_year):

    year_now = datetime.date.today().year
    new_code = code[0:2]+'.'+code[2:]
    for year in range(int(first_year),int(year_now)+1,1):
        rs = bs.query_dividend_data(code=new_code, year=str(year), yearType="operate")
        while (rs.error_code == '0') & rs.next():
            data = rs.get_row_data()    
            date = data[6]
            cash = 0 if data[9] == '' else float(data[9])
            reserve = 0 if data[11] == '' else float(data[11])
            stock = 0 if data[13] == '' else float(data[13])

            Operation.objects.create(date=date,code = code,operationType = 'DV',cash = cash,reserve = reserve,stock = stock)

    operations = Operation.objects.filter(code = code).order_by('date')
    current_hold = 0
    for operation in operations:
        if operation.operationType == 'BUY':
            current_hold += operation.count
        elif operation.operationType == 'SELL':
            current_hold -= operation.count
        elif operation.operationType == 'DV':
            if current_hold == 0:
                operation.delete()
            else :
                operation.count = current_hold
                operation.save()
                current_hold += current_hold * (operation.reserve + operation.stock)

        


