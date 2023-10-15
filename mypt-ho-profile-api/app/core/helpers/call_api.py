import json
import zlib
import requests
from app.core.helpers.global_variable import *
# from app.http.serializers.log_api_serializer import *
from ...http.serializers.api_log_serializer import APILogSerializer

def request_http(url, params=None, headers=None, get_request=False, auth=""):
    r = None
    try:
        # print(url)
        # print( ut.SELF_SIGNED_CERT_FILE2, os.path.isfile(ut.SELF_SIGNED_CERT_FILE2))
        proxies = {
            "http": None,
            "https": "proxy.hcm.fpt.vn",
        }
        if "https" in url:
            if not get_request:
                # r = requests.post(url=url, json=params, cert=(ut.CA_FILE, ut.KEY_FILE))
                r = requests.post(url=url, json=params, headers=headers, verify=False, proxies=proxies)
            else:
                # r = requests.get(url=url, json=params, verify=False)
                r = requests.get(url=url, verify=False, timeout=5, proxies=proxies)
        else:
            r = requests.post(url=url, json=params, headers=headers, auth=auth, proxies=proxies)
        print(r)

    except Exception as e:
        print(e)
        print("CALL {} >> Error {}".format(url, e))
    return r

def call_api_save_file(request, number_files, user_email, fname=""):
    url = MEDIA_URL + NAME_SERVICE_MEDIA + "upload-file-private"
    try:

        files = {}

        cnt_send = 0

        # ok_size = True
        # ok_type_file = True
        for i_file in range(int(number_files)):
            cnt = i_file + 1
            key_file = 'file_{}'.format(cnt)




            # file_obj = request.FILES[key_file]
            file_obj = request.FILES.get(key_file)
            print("====================check up hinh =========================")
            print(file_obj.content_type)

            # if file_obj.size > 5242880:
            #     ok_size = False
            #     break

            # if file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg']:
            #     ok_type_file = False
            #     break

            # name_file = file_obj.name
            # name_file_split = name_file.split(".")
            # if len(name_file_split) > 2:
            #     ok_type_file = False
            # final_file = name_file_split[-1]
            # if final_file.lower() not in ['png', 'jpg', 'jpeg', 'heic']:
            #     ok_type_file = False


            if file_obj is not None:
                cnt_send = cnt_send + 1
                files.update({
                    key_file: file_obj
                })
            # print(file_obj.content_type)
            # print(file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg', 'application/pdf'])




        data = {
            "numberFile": cnt_send,
            "userEmail": user_email,
            "folder": "an_toan_lao_dong"

        }
        if len(files) > 0:
            proxies = {
                "http": None,
                "https": "proxy.hcm.fpt.vn",
            }
            res = requests.post(url=url,  files=files, data=data, proxies=proxies)

            if res is not None:
                if res.status_code == 200:

                    result = res.json()
                    status_code = result.get('statusCode')
                    if status_code == 1:
                        data_api = result.get('data', {})
                        print("{} >> Call api :{} THANH CONG".format(fname, url))
                        print(result)
                        print(data_api)
                        return STATUS_CODE_SUCCESS, MESSAGE_API_SUCCESS, data_api
                    else:
                        print("{} >> Call api :{} >> status_code {} THAT BAI -------------------------------\n \n ".format(fname, url, status_code))
                        return STATUS_CODE_ERROR_LOGIC, MESSAGE_API_ERROR_LOGIC, {}
                else:
                    print("{} >> Call api :{} THAT BAI status code {} \n \n ".format(fname, url, res.status_code))
                    return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
            else:

                print("{} >> Call api :{} THAT BAI res is None \n \n ".format(fname, url))
                return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
        else:
            return STATUS_CODE_ERROR_SYSTEM, "Không có data", {}

    except Exception as ex:
        print("{} >> Call api :{} THAT BAI: {} \n \n ".format(fname, url, ex))
        return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}


def call_api_info_ocr(params,time_now):
    msg = "NOTOK"
    url = URL_INFO_OCR
    result = {}
    status_call = 0
    try:

        # url = "https://apis-stag.fpt.vn/mypt-notification-api/v1/" + "send-noti"

        res = request_http(url=url, params=params)
        if res is not None:
            # print(res.status_code)
            # msg = "OK"
            # print("call_call_api_info_ocr {} - THANH CÔNG : res is not none \n \n".format(url))
            if res.status_code == 200:
                result = res.json()
                status_call = 1

                print("{} >> call_call_api_info_ocr  >> THANH CONG".format(time_now, url))
                # LogApiSerializer.save_log_api(data_input=params, data_ouput=result, fname=url, time_log=time_now, ip="")
                log = APILogSerializer(
                    data={
                        "url": url,
                        "method": "POST",
                        "data": str(params),
                        "params": params,
                        "headers": "",
                        "result": result
                    }
                )

                if log.is_valid():
                    log.save()



            else:
                status_call = 2
                print("{} >> call_call_api_info_ocr  >> THAT BAI >> status code : {}".format(time_now, url, res.status_code))
                # LogApiSerializer.save_log_api(data_input=params, data_ouput=res.status_code, fname=url, time_log=time_now, ip="")
        else:
            status_call = 503
            print("{} >> call_call_api_info_ocr >> {} >> THAT BAI : res is none ".format(time_now, url))
            # LogApiSerializer.save_log_api(data_input=params, data_ouput=res, fname=url, time_log=time_now,
            #                               ip="")
    except Exception as e:
        print("{} >> call_call_api_info_ocr >> {} >> THAT BAI VI LOI: {} \n \n".format(time_now, url, e))
        # LogApiSerializer.save_log_api(data_input=params, data_ouput=e, fname=url, time_log=time_now,
        #                               ip="")
    return result, status_call

def call_api_get_emp_on_block(list_block, time_now, fname=""):
    dict_data = {}
    url = HO_CHECKIN_URL + NAME_SERVIE_HO_CHECKIN + "get-emp-on-block"
    try:
        print(list_block)

        params = {
            "listBlock": list_block
        }

        res = request_http(url=url, params=params)
        if res is not None:
            # print(res.status_code)
            # msg = "OK"
            # print("call_call_api_info_ocr {} - THANH CÔNG : res is not none \n \n".format(url))
            if res.status_code == 200:
                result = res.json()
                status_code = result.get("statusCode")
                if status_code == 1:
                    dict_data = result.get("data", {})





            else:
                status_call = 2
                print("{} >> call_api_get_emp_on_block  >> THAT BAI >> status code : {}".format(time_now, url,
                                                                                             res.status_code))
        else:
            status_call = 503
            print("{} >> call_api_get_emp_on_block >> {} >> THAT BAI : res is none ".format(time_now, url))

    except Exception as ex:
        print("{} >> {} >> Error/Loi: {}".format(url, time_now,  ex))
    return dict_data

def call_api_count_block_according_to_agency(time_now, fname=""):
    dict_data = {}
    url = HO_CHECKIN_URL + NAME_SERVIE_HO_CHECKIN + "count-block-according-to-agency"
    try:
        # print(list_block)
        #
        # params = {
        #     "listBlock": list_block
        # }

        res = request_http(url=url)
        if res is not None:
            # print(res.status_code)
            # msg = "OK"
            # print("call_call_api_info_ocr {} - THANH CÔNG : res is not none \n \n".format(url))
            if res.status_code == 200:
                result = res.json()
                dict_data = result.get("data", {})
                # status_code = result.get("statusCode")

                # if status_code == 1:
                #     dict_data = result.get("data", {})

            else:
                status_call = 2
                print("{} >> call_api_count_block_according_to_agency  >> THAT BAI >> status code : {}".format(time_now, url,
                                                                                             res.status_code))
        else:
            status_call = 503
            print("{} >> call_api_count_block_according_to_agency >> {} >> THAT BAI : res is none ".format(time_now, url))

    except Exception as ex:
        print("{} >> {} >> Error/Loi: {}".format(url, time_now,  ex))
    return dict_data


def call_api_info_block_from_emp_code(list_code, time_now, fname=""):
    dict_data = {}
    url = HO_CHECKIN_URL + NAME_SERVIE_HO_CHECKIN + "info-block-from-emp-code"
    try:

        params = {
            "listEmpCode": list_code
        }

        res = request_http(url=url, params=params)
        if res is not None:
            # print(res.status_code)
            # msg = "OK"
            # print("call_call_api_info_ocr {} - THANH CÔNG : res is not none \n \n".format(url))
            if res.status_code == 200:
                result = res.json()
                status_code = result.get("statusCode")
                if status_code == 1:
                    dict_data = result.get("data", {})





            else:
                status_call = 2
                print("{} >> call_api_get_emp_on_block  >> THAT BAI >> status code : {}".format(time_now, url,
                                                                                             res.status_code))
        else:
            status_call = 503
            print("{} >> call_api_get_emp_on_block >> {} >> THAT BAI : res is none ".format(time_now, url))

    except Exception as ex:
        print("{} >> {} >> Error/Loi: {}".format(url, time_now,  ex))
    return dict_data

def call_api(method, url, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None):
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            data=json.dumps(data),
            timeout=timeout
        )
        log = APILogSerializer(
            data={
                "url": url,
                "method": method.lower(),
                "data": data,
                "params": params,
                "headers": headers,
                "result": response.json()
            }
        )

        if log.is_valid():
            log.save()
        return response
    except Exception as e:
        return str(e)


