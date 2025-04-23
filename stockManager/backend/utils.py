from .models import Operation
import urllib.request
import re

import baostock as bs

# 拉取当前数据
def query_realtime_price(list):
    to_return = {}
    if len(list) == 0:
        return to_return

    # url = 'http://hq.sinajs.cn/list='
    url = 'http://qt.gtimg.cn/q='
    for code in list:
        url = url+code+','
        
    res_data=urllib.request.urlopen(url).read()
    
    res_array = str(res_data,encoding="gb18030").split(';')


    for i,single in enumerate(res_array):
        if len(single) > 10:
            content = re.search(r'\"([^\"]*)\"',single).group()
            
            single_info = eval(content).split('~')
            offset = float(single_info[3]) - float(single_info[4])

            offset_ratio = "0" if float(single_info[4]) == 0.0 else ("%.2f%%" % (offset/float(single_info[4]) * 100))
            
            single_real_time = [single_info[1],single_info[3],offset,offset_ratio,single_info[4]] #名称，现价，涨跌额，涨跌幅，昨收
            
            to_return[list[i]] = single_real_time
    return to_return

# 操作记录的预处理
def format_operations(list):
    to_return = {}
    for operation in list:
        if (operation.code not in to_return.keys()):
            to_return[operation.code] = []
            
        to_return[operation.code].append(operation)

    return to_return


#获取请求者的IP信息
def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
    return ip


def generate_dividend_single(code,first_year):

    if (code is None) or (first_year is None):
        return 0

    to_return = 0
    exist_operations = Operation.objects.filter(code=code,operationType = 'DV')
    date_array = list(map(lambda x: str(x.date),exist_operations))

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

            find = False
            for exist_date in date_array:
                if exist_date == date:
                    find = True

            if find == False:
                Operation.objects.create(date=date,code = code,operationType = 'DV',cash = cash,reserve = reserve,stock = stock)
                to_return += 1

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
                to_return -= 1
            else :
                operation.count = current_hold
                operation.save()
                current_hold += current_hold * (operation.reserve + operation.stock)

    #如果有更新了除权信息，返回code
    if to_return > 0:
        return code
    else: 
        return ''
