from app.core.helpers.global_variable import *
import requests

def call_api_save_file(request, number_files, user_email, fname=""):
    url = MEDIA_URL + NAME_SERVICE_MEDIA + "upload-file-private"
    try:

        files = {}
        cnt_send = 0

        for i_file in range(int(number_files)):
            cnt = i_file + 1
            key_file = 'file_{}'.format(cnt)

            # file_obj = request.FILES[key_file]
            file_obj = request.FILES.get(key_file)
            print("====================check up hinh =========================")

            if file_obj is not None:
                cnt_send = cnt_send + 1
                files.update({
                    key_file: file_obj
                })
            print(file_obj.content_type)
            print(file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg', 'application/pdf'])

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