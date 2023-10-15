from dateutil.parser import parse
import re
import json
import requests
from datetime import datetime

# '2021-06-02T09:14:43Z'
def get_date(date_time=None):
    if date_time is None:
        # print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.date()
    except:
        # print('ngày tháng không đúng định dạng')
        return ""
    
def get_time(date_time=None):
    if date_time is None:
        # print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.time()
    except:
        # print('ngày tháng không đúng định dạng')
        return ""
    
def format_date(date_format, to_format, from_format):
    try:
        date_format = datetime.strptime(date_format, to_format)
        return date_format.strftime(from_format)
    except:
        return date_format
    
def convert_vi_to_en(s):
    try:
        s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
        s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
        s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
        s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
        s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
        s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
        s = re.sub(r'[ìíịỉĩ]', 'i', s)
        s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
        s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
        s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
        s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
        s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
        s = re.sub(r'[Đ]', 'D', s)
        s = re.sub(r'[đ]', 'd', s)
        return s
    except:
        return str
    
def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host+func, headers=headers, data=payload)
        return response.text
    except:
        None
        
def import_vi_en(**kwargs):
    table = kwargs.pop('table', None)


def convert_str_date_import_db(str_date, fname):
    try:
        str_date_new = datetime.strptime(str_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        return str_date_new


    except Exception as ex:
        print("================convert_str_date_import_db======================")
        return None