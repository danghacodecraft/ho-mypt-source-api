import base64
import json
import re
from ast import literal_eval

import requests
from dateutil.parser import parse

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


# '2021-06-02T09:14:43Z'
def get_date(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.date()
    except:
        print('ngày tháng không đúng định dạng')
        return ""


def get_time(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.time()
    except:
        print('ngày tháng không đúng định dạng')
        return ""


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


def base64_decode_array(str):
    base64_bytes = base64.b64decode(str)
    base64_string = base64_bytes.decode("ascii")
    base64_data = literal_eval(base64_string)
    return base64_data


def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        print(method, host + func, headers, payload)
        response = requests.request(method, host + func, headers=headers, data=payload)
        return response.text
    except Exception as e:
        print(e)
        return None


def check_data_with_re(pattern, data):
    if re.search(pattern, data):
        return True
    return False


def is_email(email, regex=email_regex):
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def is_digit(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
    

def request_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host + func, headers=headers, data=payload)
        return response
    except Exception as e:
        print(e)
        return None
