import ast
import base64
import json
import random
import string
from datetime import datetime, timedelta, date

import redis
from Crypto.Util.Padding import pad
from Cryptodome.Cipher import AES
from dateutil.relativedelta import relativedelta
from django.conf import settings as project_settings
from kafka import KafkaProducer

from ..entities.centralized_session import CentralizedSession
from ...core.helpers import auth_session_handler as authSessionHandler
from ...core.helpers.global_variable import *

import calendar
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


def get_current_date():
    # str_datetime = "2022-07-01"
    _datetime = None
    try:
        time_now = get_current_datetime()
        str_time = time_now.strftime('%Y-%m-%d')
        _datetime = datetime.strptime(str_time, '%Y-%m-%d')
    except Exception as ex:
        print("---")
        print(ex)
        # print("convert_str_to_datetime >> {} >> Error/Loi: {}".format(fname, ex))
    return _datetime


def get_str_datetime_now_import_db():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime('%Y-%m-%d %H:%M:%S')
    return str_time_now


def get_str_date_now_import_db():
    time_now = get_current_datetime()
    str_time_now = time_now.strftime('%Y-%m-%d')
    return str_time_now


today = date.today()


def check_editable_emp_rank(year, month):
    lst_month = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

    if month in lst_month[0]:
        month_d = 4
    elif month in lst_month[1]:
        month_d = 7
    elif month in lst_month[2]:
        month_d = 10
    else:
        month_d = 1
        year = year + 1

    date_compare = date(year=year, month=month_d, day=15)

    if today <= date_compare:
        return True
    else:
        return False


def check_input_format_date(_date):
    # str_date dd/mm/yyyy
    ok = False
    try:
        # print("kkkkkkkkkkkk")
        # print(str_date)
        str_date = datetime.strftime(_date, "%d/%m/%Y")
        str_date_split = str_date.split("/")
        if len(str_date_split) == 3:
            if len(str_date_split[0]) == 2 and len(str_date_split[1]) == 2 and len(str_date_split[2]) == 4:
                convert = datetime.strptime(str_date, "%d/%m/%Y")
                ok = True

    except Exception as ex:
        # print(ex)
        pass
    return ok


def check_input_str_format_date(str_date):
    # str_date dd/mm/yyyy
    ok = False
    try:
        # print("kkkkkkkkkkkk")
        # print(str_date)
        _date = datetime.strptime(str_date, "%d/%m/%Y")
        # str_date = datetime.strftime(_date, "%d/%m/%Y")
        str_date_split = str_date.split("/")
        if len(str_date_split) == 3:
            if len(str_date_split[0]) == 2 and len(str_date_split[1]) == 2 and len(str_date_split[2]) == 4:
                convert = datetime.strptime(str_date, "%d/%m/%Y")
                ok = True

    except Exception as ex:
        # print(ex)
        pass
    return ok


def check_input_format_date_2(_date):
    # str_date dd/mm/yyyy
    ok = False
    try:
        # print("kkkkkkkkkkkk")
        # print(str_date)
        # str_date = datetime.strftime(_date, "%d/%m/%Y")
        str_date = _date
        str_date_split = str_date.split("/")
        if len(str_date_split) == 3:
            if len(str_date_split[0]) == 2 and len(str_date_split[1]) == 2 and len(str_date_split[2]) == 4:
                convert = datetime.strptime(str_date, "%d/%m/%Y")
                ok = True

    except Exception as ex:
        # print(ex)
        pass
    return ok


def convert_str_date_input_date_db(str_date, fname=""):
    # str_date dd/mm/yyyy
    str_db = None
    try:
        str_db = datetime.strptime(str_date, "%d/%m/%Y").strftime("%Y-%m-%d")

    except Exception as ex:
        print(str_date)
        print(fname)
        print(ex)
    return str_db

def convert_str_date_db_to_date(str_date, fname=""):
    # str_date %Y-%m-%d
    _date = None
    try:
        _date = datetime.strptime(str_date, "%Y-%m-%d")

    except Exception as ex:
        print(str_date)
        print(fname)
        print(ex)
    return _date



def convert_str_date_input_to_datetime(str_date, fname=""):
    # str_date dd/mm/yyyy
    try:
        _date = datetime.strptime(str_date, "%d/%m/%Y")
        return _date

    except Exception as ex:
        print("{} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), fname, ex))
        return None

def get_interval_list_train_safe_card():
    # today = datetime.now().date()



    today = get_current_datetime()


    date_now = today.day
    # day_past = today - relativedelta(months=2)
    # _date = day_past.day
    # month = day_past.month
    # ye
    # print(_date)
    # print(type(_date))

    if date_now < DATE_EXPORT_ATLD:
        to_day = today - relativedelta(months=1)
        to_month = to_day.month
        to_year = to_day.year
        # to_date = 16
        #
        # from_day = today - relativedelta(months=2)
        # from_year = from_day.year
        # from_month = from_day.month
        # from_date = 17

    else:

        to_month = today.month
        to_year = today.year
        # to_date = 16
        #
        # from_day = today - relativedelta(months=1)
        # from_year = from_day.year
        # from_month = from_day.month
        # from_date = 17

    str_date_input = "{}-{}-{}".format(to_year, to_month, DATE_EXPORT_ATLD)
    # str_past_date_input = "{}-{}-{}".format(from_year, from_month, 17)

    next_day = convert_str_date_db_to_date(str_date_input)
    next_day_1 = next_day + timedelta(days=45)
    str_next_day = next_day_1.strftime("%Y-%m-%d")
    # print(next_day_1)
    # print(type(next_day_1))
    # print(str_date_input)
    # print(str_next_day)

    # return str_date_input, str_past_date_input
    return str_next_day

def get_interval_list_train_safe_card_for_new_employyee():
    # today = datetime.now().date()



    today = get_current_datetime()


    date_now = today.day

    if date_now < DATE_EXPORT_ATLD:
        to_day = today - relativedelta(months=1)
        to_month = to_day.month
        to_year = to_day.year
        str_to_date = "{}-{}-{}".format(to_year, to_month, DATE_EXPORT_ATLD)

        from_day = today - relativedelta(months=2)
        from_month = from_day.month
        from_year = from_day.year
        str_from_date = "{}-{}-{}".format(from_year, from_month, DATE_EXPORT_ATLD + 1)

    else:

        to_month = today.month
        to_year = today.year
        str_to_date = "{}-{}-{}".format(to_year, to_month, DATE_EXPORT_ATLD)

        from_day = today - relativedelta(months=1)
        from_month = from_day.month
        from_year = from_day.year
        str_from_date = "{}-{}-{}".format(from_year, from_month, DATE_EXPORT_ATLD + 1)



    return str_from_date, str_to_date


# def get_interval_list_train_safe_card():
#     # today = datetime.now().date()
#
#
#
#     today = get_current_datetime()
#
#
#     date_now = today.day
#     # day_past = today - relativedelta(months=2)
#     # _date = day_past.day
#     # month = day_past.month
#     # ye
#     # print(_date)
#     # print(type(_date))
#
#     if date_now < 16:
#         to_day = today - relativedelta(months=1)
#         to_month = to_day.month
#         to_year = to_day.year
#         to_date = 16
#
#         from_day = today - relativedelta(months=2)
#         from_year = from_day.year
#         from_month = from_day.month
#         from_date = 17
#
#     else:
#
#         to_month = today.month
#         to_year = today.year
#         to_date = 16
#
#         from_day = today - relativedelta(months=1)
#         from_year = from_day.year
#         from_month = from_day.month
#         from_date = 17
#
#     str_date_input = "{}-{}-{}".format(to_year, to_month, 16)
#     str_past_date_input = "{}-{}-{}".format(from_year, from_month, 17)
#
#     next_day = convert_str_date_db_to_date(str_date_input)
#     next_day_1 = next_day.date() + timedelta(days=45)
#
#     # return str_date_input, str_past_date_input
#     return str_date_input, str_past_date_input

def convert_date_db_to_str_date_export(_date):
    str_date = ""
    try:
        str_date = _date.strftime('%d/%m/%Y')
    except Exception as ex:
        print("convert_date_db_to_str_date_db >> Error/Loi: {}".format(ex))
    return str_date

def get_child_depart_permission_from_token(data_token, type_screen):
    list_child_depart = []
    try:
        branch_user = data_token.get("branch")
        permission = data_token.get("permissions", {})
        all = permission.get("ALL", {})
        if len(all) > 0:
            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                              , port=project_settings.REDIS_PORT_CENTRALIZED
                                              , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                              , decode_responses=True, charset="utf-8")

            allDepartsWithLevelsStr_ = redisInstance.get("allDepartsWithLevels")
            allDepartsWithLevelsStr = eval(allDepartsWithLevelsStr_)
            allBranches = allDepartsWithLevelsStr.get("allDeparts")

            all_pnc = allBranches.get("ALLPNC", {})
            for k, v in all_pnc.items():
                list_child_depart.extend(v)

            all_tin = allBranches.get("ALLTIN", {})
            for k, v in all_tin.items():
                list_child_depart.extend(v)

            # list_parent_depart = []
            #
            # list_pnc = allBranches.get("PNC", [])
            # if len(list_pnc) > 0:
            #     list_parent_depart.extend(list_pnc)
            #
            # all_depart = allDepartsWithLevelsStr.get("allDeparts")
            # all_pnc = all_depart.get("ALLPNC", {})
            # for k in
            #
            # list_parent_depart = []
            # list_tin = allBranches.get("TIN", [])
            # if len(list_tin) > 0:
            #     list_parent_depart.extend(list_tin)


        else:
            all_tin = permission.get("ALLTIN", {})
            if len(all_tin) > 0:
                redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                                  , port=project_settings.REDIS_PORT_CENTRALIZED
                                                  , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                                  password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                                  , decode_responses=True, charset="utf-8")

                allDepartsWithLevelsStr_ = redisInstance.get("allDepartsWithLevels")
                allDepartsWithLevelsStr = eval(allDepartsWithLevelsStr_)
                allBranches = allDepartsWithLevelsStr.get("allBranches")
                list_tin = allBranches.get("TIN", [])
                if len(list_tin) > 0:
                    list_child_depart.extend(list_tin)
            else:
                all_pnc = permission.get("ALLPNC", {})
                if len(all_pnc) > 0:
                    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                                      , decode_responses=True, charset="utf-8")

                    allDepartsWithLevelsStr_ = redisInstance.get("allDepartsWithLevels")
                    allDepartsWithLevelsStr = eval(allDepartsWithLevelsStr_)
                    allBranches = allDepartsWithLevelsStr.get("allBranches")
                    list_pnc = allBranches.get("PNC", [])
                    if len(list_pnc) > 0:
                        list_child_depart.extend(list_pnc)

                else:
                    rights = {}
                    if type_screen == "train":
                        rights = permission.get("XEM_DANH_SACH_DAO_TAO", {})
                    if type_screen == "history_card":
                        rights = permission.get("XEM_DANH_SACH_LICH_SU_TT_THE", {})
                    if type_screen == "state_card":
                        rights = permission.get("XEM_DANH_SACH_TT_THE_HIEN_TAI", {})

                    if len(rights) > 0:
                        child_depart_rights = rights.get("child_depart_rights", {})
                        if len(child_depart_rights) > 0:
                            for v, k in child_depart_rights.items():
                                if len(k) > 0:
                                    list_child_depart.extend(k)
                        else:
                            branch_rights = rights.get("branch_rights", {})
                            branch_ = data_token.get("branch", [])
                            if branch_ == "PNC":
                                list_child_depart = get_all_child_depart_in_PNC()
                            else:
                                list_child_depart = get_all_child_depart_in_TIN()




    except Exception as ex:
        print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(),
                                                 "get_child_depart_permission_from_token", ex))

    return list_child_depart


def get_feature_role_atld_from_data_token(data_token, fname=""):
    role = ""
    try:
        feature = data_token.get("featuresRoles", {})
        role = feature.get("ATLD_HO", "")

    except Exception as ex:
        print("{} >> {} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(),
                                                       "get_feature_role_atld_from_data_token", fname, ex))
    return role


def check_role_on_api(role, screen, fname=""):
    ok = False
    try:
        if screen == "train":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH", "NHAN_SU_PHONG_PTC", "NHAN_SU_PHONG_HR"]:
                ok = True
        if screen == "history_card":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH", "NHAN_SU_PHONG_HR"]:
                ok = True
        if screen == "state_card":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH", "NHAN_SU_CHI_NHANH", "NHAN_SU_PHONG_PTC",
                        "NHAN_SU_PHONG_HR"]:
                ok = True
        if screen == "add_info":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                ok = True
        if screen == "edit_info":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                ok = True
        if screen == "import_info":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                ok = True
        if screen == "delete_info":
            if role in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                ok = True
    except Exception as ex:
        print("{} >> {} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(),
                                                       "get_feature_role_atld_from_data_token", fname, ex))
    return ok


def get_data_token(request):
    data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
    # data_token= {
    #         "clientId": "My_PT_HO",
    #         "grantId": 9,
    #         "userId": 9857,
    #         "email": "phuongnam.duyenntk@fpt.net",
    #         "fullName": "Võ Thị Thủy Tuyên",
    #         "isTinPncEmployee": 1,
    #         "branch": "PNC",
    #         "empCode": "00028396",
    #         "empContractType": "official",
    #         "childDepart": "PHR",
    #         "parentDepart": "PNCHO",
    #         "isHOEmp": 1,
    #         "jobTitle": "CB Quản lý CB 1",
    #         "empAvatarImageUrl": "",
    #         "permissions": {
    #             "QUAN_LY_THE_ATLD_SHOW": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 1,
    #                 "child_depart_rights": {},
    #                 "branch_rights": {
    #                     "TIN": [
    #                         "ALL"
    #                     ],
    #                     "PNC": [
    #                         "ALL"
    #                     ]
    #                 }
    #             },
    #             "QUAN_LY_THE_ATLD_EDIT": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 1,
    #                 "child_depart_rights": {},
    #                 "branch_rights": {
    #                     "TIN": [
    #                         "ALL"
    #                     ],
    #                     "PNC": [
    #                         "ALL"
    #                     ]
    #                 }
    #             },
    #             "QUAN_LY_THE_ATLD_IMPORT": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 0,
    #                 "child_depart_rights": None,
    #                 "branch_rights": None
    #             },
    #             "XEM_DANH_SACH_DAO_TAO": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 1,
    #                 "child_depart_rights": {},
    #                 "branch_rights": {
    #                     "TIN": [],
    #                     "PNC": [
    #                         "ALL"
    #                     ]
    #                 }
    #             },
    #             "XEM_DANH_SACH_TT_THE_HIEN_TAI": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 1,
    #                 "child_depart_rights": {},
    #                 "branch_rights": {
    #                     "TIN": [],
    #                     "PNC": [
    #                         "ALL"
    #                     ]
    #                 }
    #             },
    #             "XEM_DANH_SACH_LICH_SU_TT_THE": {
    #                 "group_code": "AN_TOAN_LAO_DONG",
    #                 "has_depart_right": 1,
    #                 "child_depart_rights": {},
    #                 "branch_rights": {
    #                     "TIN": [],
    #                     "PNC": [
    #                         "ALL"
    #                     ]
    #                 }
    #             }
    #         },
    #         "featuresRoles": {
    #             "ATLD_HO": "NHAN_SU_PHONG_HR"
    #         },
    #         "jti": "c2c69626-d8fc-4b63-a20f-2180463dc350",
    #         "userRoles": [
    #             "checkin",
    #             "tracking-tool",
    #             "games"
    #         ]
    #     }

    return data_token


def convert_sex(sex_input, fname=""):
    sex = ""
    try:

        sex_upper = sex_input.upper()
        if sex_upper in ['F', 'M']:
            if sex_upper == "F":
                sex = "Nữ"
            else:
                sex = "Nam"
        else:
            sex = sex_input

    except Exception as ex:
        print("{} >> {} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), fname, "convert_sex", ex))
    return sex


def get_all_child_depart_in_PNC():
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                      , decode_responses=True, charset="utf-8")
    # print(52000000000)

    allDepartsWithLevelsStr_ = redisInstance.get("allDepartsWithLevels")
    allDepartsWithLevelsStr = eval(allDepartsWithLevelsStr_)
    allBranches = allDepartsWithLevelsStr.get("allDeparts")
    # print(allBranches)

    all_pnc = allBranches.get("ALLPNC", {})
    # print(all_pnc)
    list_child_depart = []
    for k, v in all_pnc.items():
        list_child_depart.extend(v)
    return list_child_depart


def get_all_child_depart_in_TIN():
    redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                      , port=project_settings.REDIS_PORT_CENTRALIZED
                                      , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                      password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                      , decode_responses=True, charset="utf-8")

    allDepartsWithLevelsStr_ = redisInstance.get("allDepartsWithLevels")
    allDepartsWithLevelsStr = eval(allDepartsWithLevelsStr_)
    allBranches = allDepartsWithLevelsStr.get("allDeparts")

    all_pnc = allBranches.get("ALLTIN", {})
    list_child_depart = []
    # print(all_pnc)
    # print(allBranches)
    for k, v in all_pnc.items():
        list_child_depart.extend(v)
    return list_child_depart


def get_child_depart_with_permission(authorization, permission_code):
    try:
        get_all_child_departs_result = []

        redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                           , port=project_settings.REDIS_PORT_CENTRALIZED
                                           , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                           , decode_responses=True, charset="utf-8")
        all_departs_with_levels_str = redis_instance.get("allDepartsWithLevels")

        if all_departs_with_levels_str is None:
            all_departs_with_levels = None
        else:
            all_departs_with_levels = ast.literal_eval(all_departs_with_levels_str)

        if all_departs_with_levels:
            all_child_departs = all_departs_with_levels.get("allChildDeparts", [])

            user_token = authSessionHandler.getUserAuthSessionData(authorization)
            permissions = user_token.get("permissions")

            # xy ly lay danh sach child depart theo quyen
            if "ALL" in permissions:
                permission = permissions.get("ALL")
            else:
                permission = permissions.get(permission_code, None)
            if permission is None:
                return permission

            branch_rights = permission.get("branch_rights")
            all_child_depart_rights = permission.get("all_child_depart_rights")

            if "ALL" not in branch_rights["TIN"] and "ALL" not in branch_rights["PNC"]:
                # khong co quyen all PNC va TIN
                get_all_child_departs_result = [x["childDepart"] for x in all_child_depart_rights]
            elif "ALL" in branch_rights["TIN"] and "ALL" in branch_rights["PNC"]:
                # ALL tren TIN và ALL tren PNC
                get_all_child_departs_result = [x["childDepart"] for x in all_child_departs if
                                                x["branch"] in ["PNC", "TIN"]]
            elif "ALL" in branch_rights["TIN"] and "ALL" not in branch_rights["PNC"]:
                # ALL tren TIN, nhung khong all tren PNC
                get_all_child_departs_result = [x["childDepart"] for x in all_child_departs if
                                                x["branch"] == "TIN"] + [x["childDepart"] for x in
                                                                         all_child_depart_rights]
            else:
                # ALL tren PNC, nhung khong all tren TIN
                get_all_child_departs_result = [x["childDepart"] for x in all_child_departs if
                                                x["branch"] == "PNC"] + [x["childDepart"] for x in
                                                                         all_child_depart_rights]
    except Exception as ex:
        print(f"{datetime.now()} >> get_child_depart_with_permission >> {ex}")
        return None
    else:
        return get_all_child_departs_result


def empty(_val):
    if _val in ({}, [], None, '', 0):
        return True
    if isinstance(_val, str) and len(_val.strip()) == 0:
        return True
    return False

def check_input_toa_do(toa_do):
    ok = True
    try:
        toa_do_1 = toa_do.split(",")
        if len(toa_do_1)== 2:
            lat = float(toa_do_1[0])
            long = float(toa_do_1[1])
    except Exception as ex:
        print("=========================check_input_toa_do====================================")
        print(ex)
        print(toa_do)
        ok = False
    return ok


def convert_datetime_db_to_str_datetime_export(_date):
    # type _date: datetime, data = %Y-%m-%d
    str_date = ""
    try:
        str_date = datetime.strftime(_date, "%d/%m/%Y")
    except Exception as ex:
        print("{} >> convert_date_db_to_str_date_export : Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))
    return str_date

def convert_dict_data_db(dict_data):
    data = {}
    try:
        for k,v in dict_data.items():
            if isinstance(v, datetime):
                data.update({
                    k: convert_datetime_db_to_str_datetime_export(v)
                })
            elif isinstance(v, date):
                data.update({
                    k:convert_date_db_to_str_date_export(v)
                })
            else:
                data.update({
                    k:v
                })
    except Exception as ex:
        print("{} >> Error/loi >> {}".format(get_str_datetime_now_import_db(), ex))
    return data

def push_json_to_kafka(dict_data, fname=""):
    try:
        producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
        message_ = dict_data
        message2 = json.dumps(message_)
        message3 = message2.encode('utf-8')
        message = message3
        future = producer.send(TOPIC_KAFKA, message)
        result = future.get()
        print(result)
    except Exception as ex:
        print("{} >> push_json_to_kafka >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
        print(ex)


def get_start_date_and_end_date_of_last_month():
    # lay ngay dau tien va ngay ket thuc cua thang
    currentDateAndTime = datetime.now()


    year_now = currentDateAndTime.year
    if currentDateAndTime.month == 1:
        month_now = 12
        year_now = year_now - 1
    else:
        month_now = currentDateAndTime.month - 1

    end_month = calendar.monthrange(year_now, month_now)

    end_day = end_month[1]

    start_date = "{}-{}-{}".format(year_now, month_now, "01")
    end_date = "{}-{}-{}".format(year_now, month_now, end_day)
    return start_date, end_date