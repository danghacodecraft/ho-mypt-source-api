from datetime import datetime, timedelta, time, date
from app.core.helpers.global_variable import *


def strToTime(_str, _str_format=FORMAT_DATETIME_DEFAULT):
    try:
        return datetime.strptime(_str, _str_format)
    except:
        return None


def strToDate(_str, _str_format=FORMAT_DATE_DEFAULT):
    try:
        return datetime.strptime(_str, _str_format)
    except:
        return None


def checkDatetimeFormat(_str, _str_format=FORMAT_DATETIME_DEFAULT):
    try:
        return bool(datetime.strptime(_str, _str_format))
    except:
        return False


def checkDateFormat(_str, _str_format=FORMAT_DATE_DEFAULT):
    try:
        return bool(datetime.strptime(_str, _str_format))
    except:
        return False


def strFirstDayOfMonth(char='/'):
    return datetime.now().strftime('01' + char + "%m" + char + "%Y")


def curentDay(subDay=0, char='/'):
    return (datetime.today() - timedelta(days=subDay)).strftime('%d' + char + "%m" + char + "%Y")


def createDatetime(_year, _month, _day, _hour=0, _minute=0, _second=0):
    return datetime(_year, _month, _day, _hour, _minute, _second)


def getDate(day=0):
    return datetime.today() + timedelta(days=day)


def today():
    return datetime.today()


def firstDayOfMonth(_datetime):
    return _datetime.replace(day=1)


def lastDayOfMonth(_datetime):
    m = _datetime.replace(day=28) + timedelta(days=4)  # tháng tiếp theo
    return m.replace(day=1) - timedelta(days=1)


def getNextMonth(_datetime):
    m = _datetime.replace(day=28) + timedelta(days=4)  # tháng tiếp theo
    try:
        return datetime(m.year, m.month, _datetime.day)
    except:
        return lastDayOfMonth(m)


def getPrevMonth(_datetime):
    m = _datetime.replace(day=1) - timedelta(days=1)
    try:
        return datetime(m.year, m.month, _datetime.day)
    except:
        return lastDayOfMonth(m)


def getFirstDayOfPrevMonth(_datetime):
    m = _datetime.replace(day=1) - timedelta(days=1)
    return m.replace(day=1)


def getLastDayOfPrevMonth(_datetime):
    return _datetime.replace(day=1) - timedelta(days=1)


def getDateOfNextYear(_datetime, year=1):
    return _datetime.replace(year=_datetime.year + year)


# func: getSecondFromNowToLastOfDay:  Trả về số giây còn lại đến thời điểm cuối ngày
def getSecondFromNowToLastOfDay():
    return (datetime.today().max - datetime.today()).seconds


# func: getSecondFromNowToLastOfDay:  Trả về số giây còn lại đến thời điểm cuối tháng
def getSecondFromNowToLastOfMonth():
    lastDay = lastDayOfMonth(datetime.today())
    return (lastDay.max - datetime.today()).seconds


# func: getSecondFromNowToNextMonth : Trả về số giây còn lại từ thời điểm hiện tại tới ngày này tháng sau
def getSecondFromNowToNextMonth():
    lastDay = getNextMonth(datetime.today())
    return (lastDay.max - datetime.today()).seconds
# def today():
#     return datetime.now().astimezone(pytz.timezone('Asia/Bangkok'))
