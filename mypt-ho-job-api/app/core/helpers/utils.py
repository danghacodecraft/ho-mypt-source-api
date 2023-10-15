from Cryptodome.Cipher import AES
import time
import string
import random
import base64
from Crypto.Util.Padding import pad
from ..entities.centralized_session import CentralizedSession
from datetime import datetime, timedelta, date
from ...configs.app_settings import SALARY_SECRET_KEY


def aes256():
    try:
        # 16s bit
        BS = 16
        # SECRET KEY of API SCM in Document
        # Staging
        # key =   b'8840240ce0ecbb703a9425b40a121d99'
        # Production
        key = b'33b8ddca078f4bbc85d90fb7d3b4fde4'
        # Key IV of API SCM in Document
        iv = b'bscKHn8REOJ2aikS'
        return BS, key, iv
    except Exception as e:
        print(e)


def encrypt_aes(iv, raw, fname=""):
    # BS = aes256()[0]
    key = aes256()[1]
    _iv = iv.encode()
    # pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    # raw = pad(raw)
    raw = pad(raw.encode(), 16)
    cipher = AES.new(key, AES.MODE_CBC, _iv)
    return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")


def decrypt_aes(iv, enc, fname=""):
    key = aes256()[1]
    # iv = aes256()[2]
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv.encode())
    return unpad(cipher.decrypt(enc)).decode("utf-8")


def decrypt_aes_salary(value, salary_secret_key=SALARY_SECRET_KEY):
    if value:
        return decrypt_aes(salary_secret_key, value)
    return "0"


def get_email_from_token(request):
    try:
        headerAuthToken = request.headers.get("Authorization")
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        redisObj = CentralizedSession()
        dataRedis = redisObj.validateSession(newHeaderAuthToken)
        return dataRedis['sessionData']['email']
    except:
        return None


def is_null_or_empty(_str):
    if is_none(_str):
        return True
    if isinstance(_str, str):
        if is_empty(_str):
            return True
        if len(_str.strip()) > 0:
            return _str.strip().isspace()
        return True
    return False


def is_none(v):
    if v is None:
        return True
    return False


def is_empty(_str):
    if isinstance(_str, str):
        return is_none(_str) or len(_str.strip()) == 0
    return False


def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    return time_now.strftime('%d/%m/%Y %H:%M:%S')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
