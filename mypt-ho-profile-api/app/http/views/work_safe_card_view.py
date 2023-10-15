from ...core.helpers.response import *
from ..paginations.custom_pagination import *
from rest_framework.viewsets import ViewSet
from ...configs.excel_table import *
from ...core.helpers import auth_session_handler as authSessionHandler, call_api_save_file, call_api_info_ocr
from app.http.serializers.hr_serializer import *
from app.http.serializers.info_modify_history_serializer import *
from app.http.serializers.ocr_work_safe_serializer import *
from app.core.helpers.utils import *
from django.db.models import Q

class SafecardView(ViewSet):

    def info_list_train(self, request):
        fname = "info_list_train"
        data_input = request.data
        parent_depart = data_input.get('parentDepart', [])
        child_depart = data_input.get("childDepart", [])

        try:
            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")


            role = get_feature_role_atld_from_data_token(data_token, fname=fname)

            ok_role = check_role_on_api(role,screen="train", fname=fname)
            if not ok_role:
                return  response_data(data={}, message="Bạn không có quyền thực hiện tính năng này", status=STATUS_CODE_INVALID_INPUT)

            queryset_emp_code = Employee.objects.filter(status_working=1).values_list('emp_code', flat=True)
            list_queryset_emp_code = list(queryset_emp_code)

            queryset = SafeCard.objects.filter(child_depart__in=tuple(list_right_child_depart),
                                               emp_code__in=tuple(list_queryset_emp_code))

            if len(child_depart) > 0:
                queryset = queryset.filter(child_depart__in=tuple(child_depart))

            if len(parent_depart) > 0:
                queryset = queryset.filter(parent_depart__in=tuple(parent_depart))


            count = queryset.count()
            # paginator = StandardPagination()
            paginator = StandardPagination()
            if "perPage" in data_input and isinstance(data_input["perPage"], int):
                paginator.page_size = data_input["perPage"]
            result = paginator.paginate_queryset(queryset, request)
            serializer = SafeCardSerializer(result, many=True)
            list_data = serializer.data

            if len(list_data) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            list_emp_code_result = []
            for j in list_data:
                list_emp_code_result.append(j['empCode'])
            dict_col = DICT_CONVERT_TRAIN

            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                'numberRow': count,
                "data": list_data,
                "dictCol": dict_col
            }
            return response_data(data=data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("===============view_detail_info_work_safe_card===========")
            print("{} >> {}".format(get_str_datetime_now_import_db(), data_input))
            print(ex)
            print(data_input)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)


    def info_state_work_safe_card_for_manager(self, request):

        fname = "info_state_work_safe_card_for_manager"

        # tinh trang the hien tai

        # man hinh quan ly the atld
        data_input = request.data
        state_card = data_input.get("stateCard", [])
        emp_code_input = data_input.get("empCode", "")
        try:

            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="state_card", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)




            queryset_emp_code = Employee.objects.filter(status_working=1).values_list('emp_code', flat=True)

            if queryset_emp_code == 0:
                return response_data(data={}, message="Không tìm thấy nhân viên trên phòng ban mà bạn đang quản lý", status=STATUS_CODE_INVALID_INPUT)
            
            list_emp_code = list(queryset_emp_code)

            queryset = SafeCard.objects.filter(emp_code__in=tuple(list_emp_code), child_depart__in=tuple(list_right_child_depart))
            if len(state_card) > 0:
                queryset = queryset.filter(tinh_trang_the_chung_chi__in=tuple(state_card))

            if not is_null_or_empty(emp_code_input) :
                if len(emp_code_input) != 8:
                    return response_data(data={}, message="Vui lòng nhập đúng định dạng cho mã nhân viên",status=STATUS_CODE_INVALID_INPUT)
                else:
                    queryset = queryset.filter(emp_code=emp_code_input)

            queryset = queryset.filter(active=1)
            queryset = queryset.order_by('-ngay_cap_the_ATLD')

            paginator = StandardPagination()
            if "perPage" in data_input and isinstance(data_input["perPage"], int):
                paginator.page_size = data_input["perPage"]

            count = queryset.count()
            # paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = SafeCardSerializer(result, many=True)
            list_data = serializer.data

            # list_data_new = []
            if len(list_data) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            list_emp_code_result = []
            for j in list_data:
                list_emp_code_result.append(j['empCode'])


            dict_col = DICT_KEY_LIST_SAFE_CARD['manager']
            if role not in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                dict_col = DICT_KEY_LIST_SAFE_CARD['hr']


            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                "data": list_data,
                'numberRow': count,
                "dictCol": dict_col
                # 'newsList': serializer.data
            }
            return response_data(data=data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("===============info_state_work_safe_card===========")
            print("{} >> {}".format(get_str_datetime_now_import_db(), data_input))
            print(ex)
            print(data_input)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)

    def info_histories_state_work_safe_card_for_manager(self, request):
        fname = "info_histories_state_work_safe_card_for_manager"

        # man hinh quan ly the atld
        data_input = request.data
        # _type = data_input.get("type")
        state_card = data_input.get("stateCard", [])
        emp_code_input = data_input.get("empCode", "")

        try:
            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="history_card", fname=fname)

            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            queryset_emp_code = Employee.objects.all().values_list('emp_code',flat=True)

            if queryset_emp_code == 0:
                return response_data(data={}, message="Không tìm thấy nhân viên trên phòng ban mà bạn đang quản lý",
                                     status=STATUS_CODE_INVALID_INPUT)

            list_emp_code = list(queryset_emp_code)

            queryset = SafeCard.objects.filter(emp_code__in=tuple(list_emp_code), child_depart__in=tuple(list_right_child_depart))
            if len(state_card) > 0:
                queryset = queryset.filter(tinh_trang_the_chung_chi__in=tuple(state_card))


            if not is_null_or_empty(emp_code_input):
                if len(emp_code_input) != 8:
                    return response_data(data={}, message="Vui lòng nhập đúng định dạng cho mã nhân viên",
                                         status=STATUS_CODE_INVALID_INPUT)
                else:
                    queryset = queryset.filter(emp_code=emp_code_input)
            queryset = queryset.order_by('-ngay_cap_the_ATLD')

            paginator = StandardPagination()
            if "perPage" in data_input and isinstance(data_input["perPage"], int):
                paginator.page_size = data_input["perPage"]

            count = queryset.count()
            # paginator = StandardPagination()
            result = paginator.paginate_queryset(queryset, request)
            serializer = SafeCardSerializer(result, many=True)
            list_data = serializer.data

            if len(list_data) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            dict_col = DICT_KEY_LIST_SAFE_CARD['manager']
            if role not in ["TRUONG_PHO_PHONG_HR", "NHAN_SU_DUOC_CHI_DINH"]:
                dict_col = DICT_KEY_LIST_SAFE_CARD['hr']

            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                "data": list_data,
                'numberRow': count,
                "dictCol": dict_col
                # 'newsList': serializer.data
            }
            return response_data(data=data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            # print("===============info_state_work_safe_card===========")
            # print("{} >> {}".format(get_str_datetime_now_import_db(), data_input))
            # print(ex)
            # print(data_input)
            print("{} >> info_state_work_safe_card >> Error/Loi: {} >> input {}".format(get_str_datetime_now_import_db(), ex, data_input))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)

    def export_list_train(self, request):
        fname = "export_list_train"
        data_input = request.data
        # _type = data_input.get("type")
        parent_depart_input = data_input.get('parentDepart', [])
        child_depart_input = data_input.get("childDepart", [])
        time_log = get_str_datetime_now_import_db()
        try:

            data_export = []
            list_process = []

            # lay danh sach emp_code nam trong vung phan quyen
            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            queryset_emp_code = Employee.objects.filter(status_working=1,
                                                        child_depart__in=tuple(list_right_child_depart)).values_list(
                'emp_code', flat=True)
            list_emp_code = list(queryset_emp_code)
            tuple_emp_code = tuple(list_emp_code)

            dict_department = DepartmentSerializer.get_all_info_for_child_depart(fname=fname, time_log=time_log)
            dict_type_card = TypeGroupTrainingWorkSafeSerializer.get_all_info_for_job_title(fname="")

            start_date, end_date = get_interval_list_train_safe_card_for_new_employyee()


            list_process, data_export = self.list_train_for_new_emp(start_date=start_date, end_date=end_date,
                                                                    child_depart_input=child_depart_input,
                                                                    tuple_list_emp_code=tuple_emp_code,
                                                                    list_process=list_process,
                                                                    data_export=data_export,
                                                                    dict_department=dict_department,
                                                                    dict_type_card=dict_type_card, fname=fname)


            list_process, data_export = self.list_train_when_change_job_title(start_date=start_date, end_date=end_date,
                                                                              child_depart_input=child_depart_input,
                                                                              tuple_list_emp_code=tuple_emp_code,
                                                                              list_process=list_process,
                                                                              data_export=data_export,
                                                                              dict_department=dict_department,
                                                                              dict_type_card=dict_type_card, fname=fname)


            list_process, data_export = self.list_train_from_atld(parent_depart=parent_depart_input,
                                                                  child_depart=child_depart_input,
                                                                  tuple_list_emp_code=tuple_emp_code,
                                                                  list_process=list_process,
                                                                  data_export=data_export, fname=fname)



            return response_data(data={"sheet1": data_export}, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)

        except Exception as ex:
            print("{} >> {} >> Error/loi: {}".format(time_log, fname, ex))
            return response_data(data=str(ex), status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)

    def list_train_from_atld(self, parent_depart, child_depart, tuple_list_emp_code, list_process, data_export, fname):
        queryset = SafeCard.objects.filter(emp_code__in=tuple_list_emp_code)

        if len(parent_depart) > 0:
            queryset = queryset.filter(parent_depart__in=tuple(parent_depart))

        if len(child_depart) > 0:
            queryset = queryset.filter(child_depart__in=tuple(child_depart))

        str_date_input = get_interval_list_train_safe_card()
        queryset = queryset.filter(ngay_het_han_ATLD__lte=str_date_input)
        queryset = queryset.filter(active=1)

        serializer = SafeCardSerializer(queryset, many=True)
        list_data_output = serializer.data

        # xu ly danh sach dao tao trong bang tool_atld_tb
        if len(list_data_output) > 0:
            for i in list_data_output:
                if (i['empCode']) not in list_process:
                    list_process.append(i['empCode'])
                    dict_tmp = {}

                    for k, v in DICT_CONVERT_TRAIN.items():
                        dict_tmp[v] = i.get(k, '')

                    dict_tmp['Giới tính'] = convert_sex(i.get('sex'), fname)

                    data_export.append(dict_tmp)
        return list_process, data_export

    def list_train_when_change_job_title(self, start_date, end_date, child_depart_input, tuple_list_emp_code, list_process, data_export,dict_department, dict_type_card, fname):
        qr_modify = InformationModifyHistory.objects.filter(key_name='job_title', created_at__gte=start_date,
                                                            created_at__lte=end_date).values_list('emp_code',
                                                                                                  flat=True)
        list_emp_code_modify = list(qr_modify)
        qr2 = Employee.objects.filter(emp_code__in=tuple(list_emp_code_modify))
        qr2 = qr2.filter(emp_code__in=tuple_list_emp_code)
        if len(child_depart_input) > 0 :
            qr2 = qr2.filter(child_depart__in=tuple(child_depart_input))
        qr2 = qr2.values('emp_code', 'email', 'emp_name','child_depart', 'job_title', 'date_join_company',
                         'sex', 'birthday', 'cmnd')

        list_process, data_export = self.get_data_list_train(qr=qr2, list_process=list_process, data_export=data_export, dict_department=dict_department, dict_type_card=dict_type_card)

        return list_process, data_export

    def list_train_for_new_emp(self, start_date, end_date, child_depart_input, tuple_list_emp_code, list_process, data_export, dict_department, dict_type_card, fname):

        qr_new = Employee.objects.filter(emp_code__in=tuple_list_emp_code, date_join_company__gte=start_date,
                                                            date_join_company__lte=end_date)
        if len(child_depart_input) > 0:
            qr_new = qr_new.filter(child_depart__in=tuple(child_depart_input))
        qr_new = qr_new.values('emp_code', 'email', 'emp_name','child_depart', 'job_title', 'date_join_company',
                         'sex', 'birthday', 'cmnd')

        list_process, data_export = self.get_data_list_train(qr=qr_new, list_process=list_process, data_export=data_export,
                                                             dict_department=dict_department,
                                                             dict_type_card=dict_type_card)
        return list_process, data_export

    def get_data_list_train(self, qr, list_process, data_export, dict_department, dict_type_card):

        if len(qr) > 0:
            for i in qr:
                emp_code = i['emp_code']
                child_depart = i['child_depart']
                dict_detail_child_depart = dict_department.get(child_depart, {})
                agency = dict_detail_child_depart.get('agency', '')
                parent_depart = dict_detail_child_depart.get('parent_depart', '')
                date_join_company = i['date_join_company']
                if date_join_company is None:
                    str_date_join_company = ""
                else:
                    str_date_join_company = convert_date_db_to_str_date_export(date_join_company)

                ngay_sinh = i['birthday']
                if ngay_sinh is None:
                    str_ngay_sinh = ""
                else:
                    str_ngay_sinh = convert_date_db_to_str_date_export(ngay_sinh)

                job_title = i['job_title']
                dict_type_card = dict_type_card.get(job_title, {})
                type_card = dict_type_card.get('type_card', '')
                group_train = dict_type_card.get('train_group', '')
                if emp_code not in list_process:
                    list_process.append(emp_code)
                    dict_tmp = {
                        "Vùng": parent_depart,
                        "Đơn vị": agency,
                        "Bộ phận": child_depart,
                        "Mã NV": emp_code,
                        "Họ và tên": i['emp_name'],
                        "Vị trí công việc": job_title,
                        "Ngày vào công ty": str_date_join_company,
                        "Giới tính":convert_sex(i["sex"], ""),
                        "Ngày sinh": str_ngay_sinh,
                        "CMND/CCCD": i["cmnd"],
                        "Nhóm đào tạo": group_train,
                        "Đối tượng cấp thẻ/Chứng nhận": type_card
                    }
                    data_export.append(dict_tmp)

        return list_process, data_export





    def export_state_card_for_manager(self, request):
     # man hinh quan ly
        fname = "export_state_card"

        data_input = request.data
        # _type = data_input.get("type")
        state_card = data_input.get("stateCard", [])
        emp_code_input = data_input.get("empCode", "")

        try:
            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="state_card", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            # queryset_emp_code = Employee.objects.filter(child_depart__in=tuple(list_right_child_depart),
            #                                             status_working=1).values()

            queryset_emp_code = Employee.objects.filter( status_working=1).values_list('emp_code', flat=True)

            if queryset_emp_code == 0:
                return response_data(data={}, message="Không tìm thấy nhân viên trên phòng ban mà bạn đang quản lý",
                                     status=STATUS_CODE_INVALID_INPUT)
            # list_emp_code = []
            # for i_code in queryset_emp_code:
            #     list_emp_code.append(i_code['emp_code'])

            list_emp_code = list(queryset_emp_code)

            queryset = SafeCard.objects.filter(child_depart__in=tuple(list_right_child_depart),emp_code__in=tuple(list_emp_code))
            if len(state_card) > 0:
                queryset = queryset.filter(tinh_trang_the_chung_chi__in=tuple(state_card))

            if not is_null_or_empty(emp_code_input):
                if len(emp_code_input) != 8:
                    return response_data(data={}, message="Vui lòng nhập đúng định dạng cho mã nhân viên",
                                         status=STATUS_CODE_INVALID_INPUT)
                else:
                    queryset = queryset.filter(emp_code=emp_code_input)

            queryset = queryset.filter(active=1)
            # query_emp_code_result = queryset.values_list('emp_code', flat=True)
            # dict_info_list_emp_code = EmployeeSerializer.get_info_present_atld(query_emp_code_result)
            queryset = queryset.order_by('-ngay_cap_the_ATLD')
            serializer = SafeCardSerializer(queryset, many=True)
            list_data = serializer.data
            if len(list_data) > 0:
                list_data_output = []
                for i in list_data:
                    # emp_info = i['emp_info']
                    # emp_info = dict_info_list_emp_code.get(i['empCode'], {})
                    child_depart = i.get('childDepart', '')

                    # parent_depart, chi_nhanh = DepartmentSerializer.get_parent_depart_from_child_depart(child_depart=child_depart)
                    # dict_info_child_depart = DepartmentSerializer.get_parent_depart_from_child_depart(
                    #     child_depart=[child_depart])
                    # info_parent_depart = dict_info_child_depart.get(child_depart, {})
                    parent_depart = i['parentDepart']
                    chi_nhanh = i['agency']

                    i['parentDepart'] = parent_depart
                    dict_tmp = {}
                    dict_tmp['Vùng'] = parent_depart
                    dict_tmp['Đơn vị'] = chi_nhanh
                    dict_tmp['Bộ phận'] = child_depart
                    dict_tmp['Mã NV'] = i['empCode']
                    dict_tmp['Tên nhân viên'] = i.get('name', '')
                    dict_tmp['Vị trí công việc'] = i.get('jobTitle', '')
                    if role in ['NHAN_SU_DUOC_CHI_DINH', 'TRUONG_PHO_PHONG_HR']:
                        dict_tmp['Ngày vào công ty'] = i.get('dateJoinCompany', '')
                        dict_tmp['Giới tính'] = convert_sex(i.get('sex', ''), fname)
                        dict_tmp['Ngày sinh'] = i.get('birthday', '')
                        dict_tmp['CMND/CCCD'] = i.get('cmnd', '')
                    dict_tmp['Nhóm đào tạo'] = i['trainingGroup']
                    dict_tmp['Ngày bắt đầu đào tạo'] = i['trainingStartDate']
                    dict_tmp['Ngày cấp thẻ ATLĐ'] = i['dateCertificate']
                    dict_tmp['Ngày hết hạn ATLĐ'] = i['expirationDate']
                    dict_tmp['Số thẻ'] = i['numberCard']
                    dict_tmp['Tình trạng thẻ/Chứng nhận'] = i['statusCertificate']
                    dict_tmp['Cấp thẻ/Chứng nhận'] = i['certificate']
                    dict_tmp['Tên file hình ảnh/chứng nhận'] = i['pictureCertificate']
                    list_data_output.append(dict_tmp)

                return response_data(data={"sheet1": list_data_output}, status=STATUS_CODE_SUCCESS,
                                     message=MESSAGE_API_SUCCESS)




            else:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
        except Exception as ex:
            # print("==============={}===========".format(fname))
            # print("{} >> {}".format(get_str_datetime_now_import_db(), data_input))
            # print(ex)
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)


    def export_histories_state_card_for_manager(self, request):
     # man hinh quan ly
        fname = "export_state_card"

        data_input = request.data
        state_card = data_input.get("stateCard", [])
        emp_code_input = data_input.get("empCode", "")

        try:
            data_token = get_data_token(request)
            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="history_card", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            # queryset_emp_code = Employee.objects.filter(child_depart__in=tuple(list_right_child_depart),
            #                                             status_working=1).values()

            queryset_emp_code = Employee.objects.all().values_list('emp_code', flat=True)

            if queryset_emp_code == 0:
                return response_data(data={}, message="Không tìm thấy nhân viên trên phòng ban mà bạn đang quản lý",
                                     status=STATUS_CODE_INVALID_INPUT)
            # list_emp_code = []
            # for i_code in queryset_emp_code:
            #     list_emp_code.append(i_code['emp_code'])
            list_emp_code = list(queryset_emp_code)

            queryset = SafeCard.objects.filter(emp_code__in=tuple(list_emp_code), child_depart__in=tuple(list_right_child_depart))
            if len(state_card) > 0:
                queryset = queryset.filter(tinh_trang_the_chung_chi__in=tuple(state_card))

            if not is_null_or_empty(emp_code_input):
                if len(emp_code_input) != 8:
                    return response_data(data={}, message="Vui lòng nhập đúng định dạng cho mã nhân viên",
                                         status=STATUS_CODE_INVALID_INPUT)
                else:
                    queryset = queryset.filter(emp_code=emp_code_input)

            # queryset = queryset.filter(active=1)
            # queryset_emp_code_result = queryset.values_list('emp_code', flat=True)
            # dict_info_list_emp_code = EmployeeSerializer.get_info_present_atld(queryset_emp_code_result)
            queryset = queryset.order_by('-ngay_cap_the_ATLD')
            serializer = SafeCardSerializer(queryset, many=True)
            list_data = serializer.data
            if len(list_data) > 0:
                list_data_output = []
                for i in list_data:
                    child_depart = i.get('childDepart', '')
                    parent_depart = i['parentDepart']
                    chi_nhanh = i['agency']

                    dict_tmp = {}
                    dict_tmp['Vùng'] = parent_depart
                    dict_tmp['Đơn vị'] = chi_nhanh
                    dict_tmp['Bộ phận'] = child_depart
                    dict_tmp['Mã NV'] = i['empCode']
                    dict_tmp['Tên nhân viên'] = i.get('name', '')
                    dict_tmp['Vị trí công việc'] = i.get('jobTitle', '')
                    if role in ['NHAN_SU_DUOC_CHI_DINH', 'TRUONG_PHO_PHONG_HR']:
                        dict_tmp['Ngày vào công ty'] = i.get('dateJoinCompany', '')
                        dict_tmp['Giới tính'] = convert_sex(i.get('sex', ''), fname)
                        dict_tmp['Ngày sinh'] = i.get('birthday', '')
                        dict_tmp['CMND/CCCD'] = i.get('cmnd', '')
                    dict_tmp['Nhóm đào tạo'] = i['trainingGroup']
                    dict_tmp['Ngày bắt đầu đào tạo'] = i['trainingStartDate']
                    dict_tmp['Ngày cấp thẻ ATLĐ'] = i['dateCertificate']
                    dict_tmp['Ngày hết hạn ATLĐ'] = i['expirationDate']
                    dict_tmp['Số thẻ'] = i['numberCard']
                    dict_tmp['Tình trạng thẻ/Chứng nhận'] = i['statusCertificate']
                    dict_tmp['Cấp thẻ/Chứng nhận'] = i['certificate']
                    dict_tmp['Tên file hình ảnh/chứng nhận'] = i['pictureCertificate']

                    list_data_output.append(dict_tmp)

                return response_data(data={"sheet1": list_data_output}, status=STATUS_CODE_SUCCESS,
                                     message=MESSAGE_API_SUCCESS)




            else:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)





    def add_info_safe_card(self, request):
        fname = "add_info_safe_card"
        # data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        data_token = get_data_token(request)
        user_email = data_token.get("email")
        data = request.data
        # print("--->", type(dict(request.POST)))
        # print("--->", dict(request.POST))
        _type = data.get("type", "")
        # type = ocr neu la thong tin tu ocr




        try:
            # validate = AddSafeCardValidate(data=data)
            # if not validate.is_valid():
            #     return response_data(status=5, message=validate.errors)

            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="add_info", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            list_right_child_depart = get_child_depart_permission_from_token(data_token, "train")




            validate_emp_code = EmpCodeSafeCardValidate(data=data)
            if not validate_emp_code.is_valid():
                return response_data(status=5, message=list(validate_emp_code.errors.values())[0][0])

            if _type != "ocr":
                validate_ngay_cap_the = DateCertificateSafeCardValidate(data=data)
                if not validate_ngay_cap_the.is_valid():
                    return response_data(status=5, message=list(validate_ngay_cap_the.errors.values())[0][0])

                validate_ngay_het_han = ExpirationDateSafeCardValidate(data=data)
                if not validate_ngay_het_han.is_valid():
                    return response_data(status=5, message=list(validate_ngay_het_han.errors.values())[0][0])

                validate_ngay_start_train = TrainingStartDateSafeCardValidate(data=data)
                if not validate_ngay_start_train.is_valid():
                    return response_data(status=5, message=list(validate_ngay_start_train.errors.values())[0][0])

                validate_ngay_end_train = TrainingEndDateSafeCardValidate(data=data)
                if not validate_ngay_end_train.is_valid():
                    return response_data(status=5, message=list(validate_ngay_end_train.errors.values())[0][0])

            # if is_null_or_empty(data['numberCard']):
            #     return response_data(status=5, message="Số thẻ không được để trống")

            if not Employee.objects.filter(emp_code=data['empCode'], child_depart__in=tuple(list_right_child_depart)).exists():
                return response_data(status=5, message="Thông tin nhân viên không tồn tại trên hệ thống.")

            emp_code = data['empCode']

            dict_emp = EmployeeSerializer.get_info_present_atld([emp_code])
            dict_info_emp = dict_emp.get(emp_code, {})
            job_title = dict_info_emp.get('jobTitle')
            number_card = data['numberCard']
            ngay_cung_cap_the = data['dateCertificate']
            ngay_het_han = data['expirationDate']
            ngay_bat_dau_dao_tao = data['trainingStartDate']
            ngay_ket_thuc_dao_tao = data['trainingEndDate']




            number_file = data.get("numberFile", 0)
            data_save = {}
            data_save['empCode'] = emp_code
            data_save['numberCard'] = number_card
            data_save['dateCertificate'] = ngay_cung_cap_the
            data_save['expirationDate'] = ngay_het_han
            data_save['trainingStartDate'] = ngay_bat_dau_dao_tao
            data_save['trainingEndDate'] = ngay_ket_thuc_dao_tao
            if _type == "ocr":
                data_save['pictureCertificate'] = data.get('pictureCertificate', '')

            if len(dict_info_emp) > 0 :
                data_save.update(dict_info_emp)
                data_save['dateJoinCompany'] = convert_str_date_input_date_db(data_save['dateJoinCompany'])
                data_save['birthday']= convert_str_date_input_date_db(data_save['birthday'])
            else:
                return response_data(data={}, message="Không tìm thấy thông tin nhân viên", status=STATUS_CODE_INVALID_INPUT)

            if _type != "ocr":
                if SafeCard.objects.filter(emp_code=emp_code, number_card=number_card,
                                           ngay_cap_the_ATLD=convert_str_date_input_date_db(ngay_cung_cap_the),
                                           ngay_het_han_ATLD=convert_str_date_input_date_db(ngay_het_han),
                                           ngay_bat_dau_dao_tao=convert_str_date_input_date_db(ngay_bat_dau_dao_tao),
                                           ngay_ket_thuc_dao_tao=convert_str_date_input_date_db(ngay_ket_thuc_dao_tao)).exists():
                    return response_datas(data={}, message="Thông tin thẻ đã tồn tại trên hệ thống", status=STATUS_CODE_INVALID_INPUT)
            else:
                if SafeCard.objects.filter(emp_code=emp_code, number_card=number_card,
                                           ngay_cap_the_ATLD=ngay_cung_cap_the,
                                           ngay_het_han_ATLD=ngay_het_han,
                                           ngay_bat_dau_dao_tao=ngay_bat_dau_dao_tao,
                                           ngay_ket_thuc_dao_tao=ngay_ket_thuc_dao_tao).exists():
                    return response_datas(data={}, message="Thông tin thẻ đã tồn tại trên hệ thống", status=STATUS_CODE_INVALID_INPUT)



            if int(number_file) > 0:
                status_code, msg_code, data_code = call_api_save_file(request, number_file, user_email, "")
                if status_code == 1:
                    list_img = data_code.get('linkFile', [])
                    str_img = ''
                    if len(list_img) > 0:
                        str_img = list_img[0]
                        str_img = str_img.replace("download-file", "view-file")
                    # str_img = ""
                    # for item in list_img:
                    #     if str_img == "":
                    #         str_img = item
                    #     else:
                    #         str_img += ";" + item
                    data_save['pictureCertificate'] = str_img
                    # data.pictureCertificate = str_img
                    # print("---------------------UP HINH THANH CONG--------------------")
                    # print(list_img)
                else:
                    # print("---------------------UP HINH --------------------")
                    # print(msg_code)
                    return response_data(data={}, message="Không thể up hình", status=status_code)
            train_group, type_card = TypeGroupTrainingWorkSafeSerializer.get_info_from_job_title(job_title)


            if not is_null_or_empty(train_group):
                data_save['trainingGroup'] = train_group
            if not is_null_or_empty(type_card):
                data_save['certificate'] = type_card

            data_save['createdBy'] = user_email
            data_save['createdAt'] = get_str_datetime_now_import_db()
            data_save['jobTitle'] = job_title

            # if SafeCard.objects.filter(emp_code=data['empCode'],
            #                                      ngay_cap_the_ATLD=convert_str_date_input_date_db(data['dateCertificate']),ngay_het_han_ATLD=convert_str_date_input_date_db(data['expirationDate']), ngay_bat_dau_dao_tao=convert_str_date_input_date_db(data['trainingStartDate']), ngay_ket_thuc_dao_tao=convert_str_date_input_date_db(data['trainingEndDate']), number_card=data['numberCard']).exists():
            #     return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message="Thông tin thẻ đã tồn tại trên hệ thống")


            data_save['statusCertificate'] = SafeCardSerializer.get_status_card_from_expire_date(data_save['expirationDate'], fname= fname)

            # data.createdBy = user_email
            # data.createdAt = get_str_datetime_now_import_db()

            serializer = SafeCardSerializer(data=data_save)
            # print(data_save)
            if not serializer.is_valid():
                return response_data(status=5, message=serializer.errors)
            if not serializer.save():
                return response_data(message="Vui lòng kiểm tra thông tin thẻ An toàn lao động", status=STATUS_CODE_ERROR_LOGIC, data={})

            if _type == "ocr":
                try:
                    self.update_delete_info_ocr(id=data['id'])
                except Exception as ex1:
                    print(data)
                    print("get id Data: {}".format(ex1))
            if _type != "ocr":
                SafeCardSerializer.auto_update_active_from_emp_code_and_date_provide_card(data['empCode'],convert_str_date_input_date_db(data['dateCertificate']))
            else:
                SafeCardSerializer.auto_update_active_from_emp_code_and_date_provide_card(data['empCode'],
                                                                                              data['dateCertificate'])
            return response_data(message="Thêm thẻ ATLĐ thành công", status=1,data={})
        except Exception as ex:
            print("===============add_info_safe_card===========")
            print("{} >> {}".format(get_str_datetime_now_import_db(), data))
            print(ex)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_ERROR_LOGIC)

    def edit_info_safe_card(self, request):
        fname = "edit_info_safe_card"
        # data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        data_token = get_data_token(request)
        user_email = data_token.get("email", "")
        # user_email = "phuongnam.duuyenntk@fpt.net"
        data = request.data



        try:

            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="edit_info", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)


            validate = idValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            queryset = SafeCard.objects.filter(atld_id=data["id"]).first()
            serializer = SafeCardSerializer(queryset, many=True)

            queryset_data = SafeCard.objects.filter(atld_id=data["id"])
            serializer_data = SafeCardSerializer(queryset_data, many=True)
            list_data_init = serializer_data.data
            emp_code = ""
            if len(list_data_init) > 0:
                emp_code = list_data_init[0]['empCode']




            if not SafeCard.objects.filter(atld_id=data["id"]).exists():
                return response_data(status=5, message="Id chưa tồn tại. Không thể sửa")

            ngay_cap_the = data['dateCertificate']
            ngay_het_han = data['expirationDate']
            ngay_bat_dau_dao_tao = data['trainingStartDate']
            ngay_ket_thuc_dao_tao = data['trainingEndDate']
            so_the = data.get('numberCard')


            if is_null_or_empty(so_the):
                if SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the,
                                           ngay_het_han_ATLD=ngay_het_han,
                                           ngay_bat_dau_dao_tao=ngay_bat_dau_dao_tao,
                                           ngay_ket_thuc_dao_tao=ngay_ket_thuc_dao_tao, number_card__isnull=True).exclude(atld_id=data["id"]).exists():
                    return response_data(data={}, message="Dữ liệu chỉnh sữa trùng với dữ liệu đã có")

                if SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the,
                                           ngay_het_han_ATLD=ngay_het_han,
                                           ngay_bat_dau_dao_tao=ngay_bat_dau_dao_tao,
                                           ngay_ket_thuc_dao_tao=ngay_ket_thuc_dao_tao, number_card='').exclude(atld_id=data["id"]).exists():
                    return response_data(data={}, message="Dữ liệu chỉnh sữa trùng với dữ liệu đã có")
            else:
                if SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the,
                                           ngay_het_han_ATLD=ngay_het_han,
                                           ngay_bat_dau_dao_tao=ngay_bat_dau_dao_tao,
                                           ngay_ket_thuc_dao_tao=ngay_ket_thuc_dao_tao, number_card=so_the).exclude(atld_id=data["id"]).exists():
                    return response_data(data={}, message="Dữ liệu chỉnh sữa trùng với dữ liệu đã có")






            list_data_key = data.keys()
            data_save = {}
            # data_save['trainingGroup'] = data['trainingGroup']
            for item in list_data_key:
                # if data[item] != "" and data[item] != "edit":
                if data[item] != "edit":
                    data_save[item] = data[item]

            number_file = data.get("numberFile", 0)

            if int(number_file) > 0:
                status_code, msg_code, data_code = call_api_save_file(request, number_file, user_email, "")
                if status_code == 1:
                    list_img = data_code.get('linkFile', [])
                    str_img = ""
                    if len(list_img) > 0:
                        str_img = list_img[0]
                        str_img = str_img.replace("download-file", "view-file")
                    # str_img = ""
                    # for item in list_img:
                    #     if str_img == "":
                    #         str_img = item
                    #     else:
                    #         str_img += ";" + item
                    data_save['pictureCertificate'] = str_img
                    # print("---------------------UP HINH THANH CONG--------------------")
                    # print(list_img)
                else:
                    # print("---------------------UP HINH --------------------")
                    # print(msg_code)
                    return response_data(data={}, message="Không thể up hình", status=status_code)


            if data.get('statusCertificate') == "Chưa cấp":
                data_save['statusCertificate'] = "Chưa cấp"
            else:
                if not is_null_or_empty(data_save['expirationDate']):
                    data_save['statusCertificate'] = SafeCardSerializer.get_status_card_from_expire_date(
                        data_save['expirationDate'])
            data_save['updateTime'] = get_str_datetime_now_import_db()
            data_save['updateBy'] = user_email
            serializer = SafeCardSerializer(queryset, data=data_save)
            if not serializer.is_valid():
                # return response_data(status=5, message=serializer.errors)
                print(" {} >> {} >> {} >> Error/Loi :{}".format(user_email, get_str_datetime_now_import_db(), fname, serializer.errors))
                return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message="Điều chỉnh thẻ an toàn lao động thất bại")
            if not serializer.save():
                print(" {} >> {} >> {} >> Error/Loi :{}".format(user_email, get_str_datetime_now_import_db(), fname,
                                                                "Không sửa được"))
                return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message="Điều chỉnh thẻ an toàn lao động thất bại")

            SafeCardSerializer.auto_update_active_from_emp_code_and_date_provide_card(emp_code,
                                                                                          data_save['dateCertificate'])
            return response_data(message="Điều chỉnh thông tin thẻ An toàn lao động thành công.", data={}, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("===============edit_info_safe_card===========")
            print("{} edit_info_safe_card >> {} >> Error>> {}".format(get_str_datetime_now_import_db(), data, ex))
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message="Điều chỉnh thẻ an toàn lao động thất bại")





    def check_input_import_info_safe_card(self, request):
        fname = "check_input_import_info_safe_card"

        # data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        data_token = get_data_token(request)

        data = request.data


        data_array = data.get("array",[])
        try:

            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")

            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="add_info", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)




            # type =1 la check theo truong hop 1 va type = 2 la check theo truong hop 2
            if "array" not in data or data_array == []:
                return response_data(status=4, message="Không có dữ liệu import")

            if len(data_array) > 500:
                return response_data(status=4, message="Dữ liệu import quá lớn")


            query_emp = Employee.objects.filter(child_depart__in=tuple(list_right_child_depart)).values_list('emp_code', flat=True)
            list_data_exist = self.list_data_exist(list_right_child_depart)
            list_train_available = SafeCardSerializer.list_train_available(fname=fname)
            query_emp_not_working = Employee.objects.filter(child_depart__in=tuple(list_right_child_depart), status_working=0).values_list('emp_code', flat=True)




            errors = []
            save_flag = True
            list_data_process = []
            for idx_, item in enumerate(data_array):


                    idx = idx_ + 1
                    # item_keys = list(item.keys())






                    ma_nv = item.get("Mã nhân viên")
                    number_card = item.get("Số thẻ")
                    date_provide_card = item.get("Ngày cấp thẻ ATLĐ")
                    date_expire_card = item.get("Ngày hết hạn ATLĐ")
                    date_start_train = item.get("Ngày bắt đầu đào tạo")
                    date_end_train = item.get("Ngày kết thúc đào tạo")
                    if is_null_or_empty(ma_nv):
                        errors.append(f"Dòng ({idx + 1}) vui lòng điền mã nhân viên")
                        save_flag = False
                        # continue

                    # if is_null_or_empty(number_card):
                    #     errors.append(f"Dòng ({idx + 1}) vui lòng điền số thẻ")
                    #     save_flag = False
                    #     continue

                    if is_null_or_empty(date_provide_card):
                        errors.append(f"Dòng ({idx + 1}) vui lòng điền ngày cấp thẻ ATLĐ")
                        save_flag = False
                        # continue

                    if is_null_or_empty(date_expire_card):
                        errors.append(f"Dòng ({idx + 1}) vui lòng điền ngày hết hạn ATLĐ")
                        save_flag = False
                        # continue

                    if is_null_or_empty(date_start_train):
                        errors.append(f"Dòng ({idx + 1}) vui lòng điền ngày bắt đầu đào tạo")
                        save_flag = False
                        # continue

                    if is_null_or_empty(date_end_train):
                        errors.append(f"Dòng ({idx + 1}) vui lòng điền ngày kết thúc đào tạo")
                        save_flag = False
                        # continue






                    # if not SafeCardSerializer.check_emp_code_in_list_train(ma_nv):
                    if ma_nv not in list_train_available:
                        errors.append(f"Dòng ({idx + 1}) nhân viên không có trong danh sách đào tạo")

                    # if Employee.objects.filter(emp_code=ma_nv, status_working=0).exists():
                    if ma_nv in query_emp_not_working:
                        errors.append(f"Dòng ({idx + 1}) thông tin nhân viên đã nghỉ việc")

                    if not len(ma_nv) == 8:
                        errors.append(f"Dòng ({idx + 1})  mã nhân viên không đúng định dạng. Vui lòng nhập 8 ký tự số")
                        save_flag = False
                        # continue

                    check_provide_card = check_input_str_format_date(date_provide_card)
                    if not check_provide_card:
                        errors.append(f"Dòng ({idx + 1}) ngày cấp thẻ không đúng định dạng. Vui lòng nhập đúng định dạng dd/mm/yyyy")
                        save_flag = False
                        # continue

                    check_expire_card = check_input_str_format_date(date_expire_card)
                    if not check_expire_card:
                        errors.append(f"Dòng ({idx + 1}) ngày hết hạn thẻ không đúng định dạng. Vui lòng nhập đúng định dạng dd/mm/yyyy")
                        save_flag = False
                        # continue

                    check_start_train = check_input_str_format_date(date_start_train)
                    if not check_start_train:
                        errors.append(f"Dòng ({idx + 1}) ngày bắt đầu đào tạo không đúng định dạng. Vui lòng nhập đúng định dạng dd/mm/yyyy")
                        save_flag = False
                        # continue

                    check_end_train = check_input_str_format_date(date_end_train)
                    if not check_end_train:
                        errors.append(f"Dòng ({idx + 1}) ngày kết thúc đào tạo không đúng định dạng. Vui lòng nhập đúng định dạng dd/mm/yyyy")
                        save_flag = False
                        # continue

                    # if not Employee.objects.filter(emp_code=ma_nv, child_depart__in=tuple(list_right_child_depart)).exists():
                    if ma_nv not in query_emp:
                        errors.append(
                            f"Dòng ({idx + 1}) thông tin nhân viên không tồn tại trên hệ thống.")
                        save_flag = False
                        # continue



                    if check_expire_card and check_provide_card and check_start_train and check_end_train:

                        if is_null_or_empty(number_card):

                            if (ma_nv, date_provide_card, date_expire_card, date_start_train, date_end_train,'') in list_data_exist:
                                errors.append(f"Dòng ({idx + 1}) dữ liệu bị trùng lập")
                                save_flag = False

                            if (ma_nv, date_provide_card, date_expire_card, date_start_train, date_end_train,None) in list_data_exist:
                                errors.append(f"Dòng ({idx + 1}) dữ liệu bị trùng lập")
                                save_flag = False

                        else:
                            if (ma_nv, date_provide_card, date_expire_card, date_start_train, date_end_train,number_card) in list_data_exist:
                                errors.append(f"Dòng ({idx + 1}) dữ liệu bị trùng lập")
                                save_flag = False


                    if item not in list_data_process:
                        list_data_process.append(item)
                    else:
                        errors.append(f"Dòng ({idx + 1}) dữ liệu bị trùng lập")
                        save_flag = False
                        # continue













                    # if 'Mã NV' not in item_keys or 'Số thẻ' not in item_keys or 'Ngày cấp thẻ ATLĐ' not in item_keys\
                    #         or 'Ngày hết hạn ATLĐ' not in item_keys or 'Ngày kết thúc đào tạo ' not in item_keys :
                    #     errors.append(f"Dòng ({idx+1}) vui lòng điền đủ thông tin")


            if errors:
                return response_data(status=0, message=errors, data={"save_flag": save_flag})
            return response_data(status=1, message="", data={"save_flag": save_flag})
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(get_str_datetime_now_import_db(), "check_input_import_info_safe_card", ex ))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)



    def check_input_import_info_safe_card_from_api(self,**kwargs):
        data = kwargs.pop("data", {})
        data_array = data.get("array", [])
        list_right_child_depart = kwargs.get("list_right_child_depart", [])
        list_data_exist = kwargs.pop('list_data_exist', [])
        _type = 2
        ok = True
        des_error = ""
        try:
            # type =1 la check theo truong hop 1 va type = 2 la check theo truong hop 2
            if "array" not in data or data_array == []:
                return response_data(status=4, message="Không có dữ liệu import")

            if len(data_array) >= 500:
                return response_data(status=4, message="Dữ liệu import quá lớn")

            query_emp = Employee.objects.filter(child_depart__in=tuple(list_right_child_depart)).values_list('emp_code',
                                                                                                             flat=True)

            # errors = []
            save_flag = True
            list_data_process = []
            for idx_, item in enumerate(data_array):

                idx = idx_ + 1
                item_keys = list(item.keys())

                ma_nv = item.get("Mã nhân viên")
                number_card = item.get("Số thẻ")
                date_provide_card = item.get("Ngày cấp thẻ ATLĐ")
                date_expire_card = item.get("Ngày hết hạn ATLĐ")
                date_start_train = item.get("Ngày bắt đầu đào tạo")
                date_end_train = item.get("Ngày kết thúc đào tạo")
                if is_null_or_empty(ma_nv):
                    ok = False
                    des_error = "Thiếu mã nhân viên"
                    break

                # if is_null_or_empty(number_card):
                #     ok = False
                #     break

                if is_null_or_empty(date_provide_card):
                    ok = False
                    des_error = "Thiếu ngày cấp thẻ"
                    break

                if is_null_or_empty(date_expire_card):
                    ok = False
                    des_error = "Thiếu ngày hết hạn"
                    break

                if is_null_or_empty(date_start_train):
                    ok = False
                    des_error = "Thiếu ngày bắt đầu đào tạo"
                    break

                if is_null_or_empty(date_end_train):
                    ok = False
                    des_error = "Thiếu ngày kết thúc đào tạo"
                    break

                if not len(ma_nv) == 8:
                    ok = False
                    des_error = "Mã nhân viên không phù hợp"
                    break

                if not check_input_str_format_date(date_provide_card):
                    ok = False
                    des_error = "Ngày cấp thẻ không phù hợp"
                    break

                if not check_input_str_format_date(date_expire_card):
                    ok = False
                    des_error = "Ngày hết hạn không phù hợp"
                    break

                if not check_input_str_format_date(date_start_train):
                    ok = False
                    des_error = "Ngày bắt đầu đào tạo không phù hợp"
                    break

                if not check_input_str_format_date(date_end_train):
                    ok = False
                    des_error = "Ngày kết thúc đào tạo không phù hợp"
                    break

                # if not is_null_or_empty(number_card):
                if is_null_or_empty(number_card):

                    if (ma_nv, date_provide_card,date_expire_card,date_start_train,date_end_train, '') in list_data_exist:
                        des_error = "Nhân viên đã tồn tại trên hệ thống"
                        ok = False
                        break

                else:
                    if (ma_nv, date_provide_card,date_expire_card,date_start_train,date_end_train, number_card) in list_data_exist:
                        des_error = "Nhân viên đã tồn tại trên hệ thống"
                        ok = False
                        break


                # if SafeCard.objects.filter(emp_code=ma_nv, number_card=number_card,
                #                            ngay_cap_the_ATLD=convert_str_date_input_date_db(date_provide_card),
                #                            ngay_het_han_ATLD=convert_str_date_input_date_db(date_expire_card),
                #                            ngay_bat_dau_dao_tao=convert_str_date_input_date_db(date_start_train),
                #                            ngay_ket_thuc_dao_tao=convert_str_date_input_date_db(
                #                                date_end_train)).exists():
                #     ok = False
                #     des_error = "Dữ liệu đã tồn tại"
                #     break
                #
                # if number_card is None:
                #     if SafeCard.objects.filter(emp_code=ma_nv,number_card="",
                #                                ngay_cap_the_ATLD=convert_str_date_input_date_db(date_provide_card),
                #                                ngay_het_han_ATLD=convert_str_date_input_date_db(date_expire_card),
                #                                ngay_bat_dau_dao_tao=convert_str_date_input_date_db(date_start_train),
                #                                ngay_ket_thuc_dao_tao=convert_str_date_input_date_db(
                #                                    date_end_train), ).exists():
                #         ok = False
                #         des_error = "Dữ liệu đã tồn tại"
                #         break

                # if not Employee.objects.filter(emp_code=ma_nv,
                #                                child_depart__in=tuple(list_right_child_depart)).exists():

                if ma_nv not in query_emp:
                    ok = False
                    des_error = "Nhân viên không tồn tại"
                    break

                if item not in list_data_process:
                    list_data_process.append(item)
                else:
                    ok = False
                    break

        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), "check_input_import_info_safe_card_from_api", ex))
            ok = False
        return ok, des_error

    def delete_info_from_id(self, request):
        fname = "delete_info_from_id"
        data = request.data
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        user_email = data_token.get("email", "")
        _type = data.get("type", "")



        try:
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="delete_info", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)



            data["Id"] = data["id"]
            # if "action" in data and data["action"] == "delete":
            validate = IdValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)

            if _type != "ocr":
                queryset = SafeCard.objects.filter(atld_id=data["Id"])
                serializer = SafeCardSerializer(queryset, many=True)


                if not SafeCard.objects.filter(atld_id=data["Id"]).exists():

                    return response_data(status=5, message="Id chưa tồn tại. Không thể xoá")

                data_id = serializer.data
                info_card = str(data_id[0])
                self.insert_info_log_delete_work_safe_card(info_card, data["Id"], user_email)
                queryset.delete()
            else:
                queryset = OcrWorkSafe.objects.filter(atld_id=data['id'])
                # serializer = OcrWorkSafeSerializer(queryset, many=True)
                if not queryset.exists():
                    return response_data(data={}, message="ID chưa tồn tại", status=STATUS_CODE_INVALID_INPUT)
                queryset.delete()

            return response_data(message="Xóa thẻ ATLĐ thành công", status=STATUS_CODE_SUCCESS, data={})
        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), "delete_info_from_id", ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def cron_auto_update_status_card(self, request):
        fname = "cron_auto_update_status_card"
        try:
            list_id_sap_het_han = []
            list_id_het_han = []

            today = datetime.now().date()
            day_45 = today + timedelta(days=45)
            queryset = SafeCard.objects.exclude(
                tinh_trang_the_chung_chi__in=["Hết Hạn", "Chưa Cấp"]
            )
            for data in queryset:
                id_card = data.atld_id
                ngay_het_han = data.ngay_het_han_ATLD
                if ngay_het_han is not None:
                    if ngay_het_han <= today:
                        list_id_het_han.append(id_card)
                    elif ngay_het_han > today:
                        if ngay_het_han <= day_45:
                            list_id_sap_het_han.append(id_card)

            if len(list_id_sap_het_han) > 0:
                SafeCard.objects.filter(atld_id__in=tuple(list_id_sap_het_han)).update(tinh_trang_the_chung_chi="Sắp hết hạn")

            if len(list_id_het_han):
                SafeCard.objects.filter(atld_id__in=tuple(list_id_het_han)).update(
                    tinh_trang_the_chung_chi="Hết hạn")
            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def cron_auto_update_status_card_ocr(self, request):
        fname = "cron_auto_update_status_card"
        try:
            list_id_sap_het_han = []
            list_id_het_han = []

            today = datetime.now().date()
            day_45 = today + timedelta(days=45)
            queryset = OcrWorkSafe.objects.exclude(
                tinh_trang_the_chung_chi__in=["Hết Hạn", "Chưa Cấp"]
            )
            for data in queryset:
                id_card = data.atld_id
                ngay_het_han = data.ngay_het_han_ATLD
                if ngay_het_han is not None:
                    if ngay_het_han <= today:
                        list_id_het_han.append(id_card)
                    elif ngay_het_han > today:
                        if ngay_het_han <= day_45:
                            list_id_sap_het_han.append(id_card)

            if len(list_id_sap_het_han) > 0:
                OcrWorkSafe.objects.filter(atld_id__in=tuple(list_id_sap_het_han)).update(tinh_trang_the_chung_chi="Sắp hết hạn")

            if len(list_id_het_han):
                OcrWorkSafe.objects.filter(atld_id__in=tuple(list_id_het_han)).update(
                    tinh_trang_the_chung_chi="Hết hạn")
            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)





    def auto_update_active(self, request):
        data_input = request.data
        parent_depart = data_input.get("parentDepart")
        _type = data_input.get("type", 1)
        try:
            
            if _type == 1:

                list_parent_depart = ['PNCV5', 'PNCV6', 'PNCV7', 'PNCV4']
                list_emp_process = []


                queryset_card = SafeCard.objects.exclude(parent_depart__in=tuple(list_parent_depart))
                for card in queryset_card:
                    ngay_cap_the = card.ngay_cap_the_ATLD
                    emp_code = card.emp_code
                    if emp_code not in list_emp_process:
                        list_emp_process.append(emp_code)

                        SafeCardSerializer.auto_update_active_from_emp_code_and_date_provide_card(emp_code,ngay_cap_the)

                return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
            else:
                list_emp_process = []

                queryset_card = SafeCard.objects.all()
                for card in queryset_card:
                    ngay_cap_the = card.ngay_cap_the_ATLD
                    emp_code = card.emp_code
                    if emp_code not in list_emp_process:
                        list_emp_process.append(emp_code)
                        SafeCardSerializer.auto_update_active_from_emp_code_and_date_provide_card(emp_code, ngay_cap_the)

                return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), "auto_update_active", ex))
            return response_data(data=str(ex), message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    # sua lai code
    def import_info_safe_card_v2(self, request):
        fname = "import_info_safe_card"
        data_token = get_data_token(request)
        user_email = data_token.get("email")

        data = request.data
        _type = data.get("type")
        try:
            role = get_feature_role_atld_from_data_token(data_token, fname=fname)
            ok_role = check_role_on_api(role, screen="import_info", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token, type_screen="train")
            list_data_exist = self.list_data_exist(list_right_child_depart)
            ok_import, des_err = self.check_input_import_info_safe_card_from_api(data=data,
                                                                        list_right_child_depart=list_right_child_depart, list_data_exist=list_data_exist)

            if not ok_import:
                return response_data(data=des_err, message="Lỗi dữ liệu vui lòng kiểm tra lại",
                                     status=STATUS_CODE_ERROR_LOGIC)

            if "array" not in data or data["array"] == []:
                return response_data(status=4, message="Không có dữ liệu import", data={})

            list_data_save = []
            list_emp_import = []
            data_array = data['array']
            for k in data_array:
                emp_code_tmp = k.get('Mã nhân viên', '')
                if not is_null_or_empty(emp_code_tmp):
                    list_emp_import.append(emp_code_tmp)

            dict_emp_import = EmployeeSerializer.get_info_present_atld(list_emp_import)
            for item in data_array:
                data_dict = self.import_vi_to_en_safe_card_v2(EN=SAFE_CARD_INPUT, data=item, user_email=user_email, _type=_type, dict_emp_import=dict_emp_import)
                list_data_save.append(data_dict)

            serializer_create = SafeCardSerializer(data=list_data_save, many=True)
            if not serializer_create.is_valid():
                return response_data(data=serializer_create.errors, status=STATUS_CODE_INVALID_INPUT, message=MESSAGE_API_FAILED)
            serializer_create.save()




            list_active_1 = []
            list_active_0 = []
            for i_item in data['array']:
                lst_0, lst_1 = SafeCardSerializer.get_list_id_update_active(i_item['Mã nhân viên'],convert_str_date_input_date_db(i_item['Ngày cấp thẻ ATLĐ']))
                list_active_1.extend(lst_1)
                list_active_0.extend(lst_0)

            if len(list_active_0) > 0:
                SafeCard.objects.filter(atld_id__in=tuple(list_active_0)).update(active=0)

            if len(list_active_1) > 0:
                SafeCard.objects.filter(atld_id__in=tuple(list_active_1)).update(active=1)

            return response_data(message="Thêm thẻ ATLĐ thành công", status=1, data={})
        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def import_vi_to_en_safe_card_v2(self, **kwargs):
        EN = kwargs.pop('EN', None)
        data = kwargs.pop('data', None)
        dict_emp_import = kwargs.pop('dict_emp_import', {})
        user_email = kwargs.pop("user_email", "")
        _type = kwargs.pop("_type", "")
        data_list = list(data.keys())
        data_dict = {}
        if EN is not None and data is not None:
            key_list = list(EN.keys())
            value_list = list(EN.values())
            data_list = set(value_list) & set(data_list)
            data_dict = {}
            try:
                for item in data_list:
                    if item in value_list:
                        index = value_list.index(item)
                        data_dict[key_list[index]] = data[item]

                data_dict["createdAt"] = datetime.now()
                data_dict['createdBy'] = user_email
                if _type == "ocr":
                    data_dict['pictureCertificate'] = data.get('Tên file hình ảnh/chứng nhận', '')

                ma_nv = data_dict.get('empCode')
                dict_detail_emp = dict_emp_import.get(ma_nv, {})
                if len(dict_detail_emp) > 0:
                    data_dict.update(dict_detail_emp)

                job_title = dict_detail_emp.get('jobTitle', '')
                train_group, type_card= TypeGroupTrainingWorkSafeSerializer.get_info_from_job_title(job_title)

                if _type == "ocr":
                    train_group_2 = ""
                    try:
                        train_group_2 = data['Nhóm đào tạo']
                    except Exception as ex:
                        print("loi khong co key >> Error/Loi: {}".format(ex))

                    if train_group_2 != "":
                        train_group = train_group_2
                data_dict['trainingGroup'] = train_group
                data_dict['certificate'] = type_card
                data_dict['statusCertificate'] = SafeCardSerializer.get_status_card_from_expire_date(data_dict['expirationDate'])
                data_dict['active'] = 1

            except Exception as ex:
                print("import_vi_to_en_safe_card_v2 >> {} ".format(ex))
                return {}

        return data_dict


    def update_info_for_ocr(self, **kwargs):
        ok = False
        nhom_dao_tao = kwargs.pop("nhom_dao_tao")
        data_dict = kwargs.pop("data_dict", {})
        user_email = kwargs.pop("user_email", '')
        try:

            ok = True
            qr = OcrWorkSafe.objects.filter(emp_code=data_dict['empCode'], nhom_dao_tao=data_dict['trainingGroup'],
                                       ngay_cap_the_ATLD=convert_str_date_input_date_db(data_dict['dateCertificate']),
                                       ngay_het_han_ATLD=convert_str_date_input_date_db(data_dict['expirationDate']),
                                       ngay_bat_dau_dao_tao=convert_str_date_input_date_db(
                                           data_dict['trainingStartDate']),
                                       ngay_ket_thuc_dao_tao=convert_str_date_input_date_db(
                                           data_dict['trainingEndDate']), created_by=user_email)
            if not is_null_or_empty(nhom_dao_tao):
                qr = qr.filter(nhom_dao_tao=nhom_dao_tao)




            qr = qr.update(confirm=1)

            ok = True

        except Exception as ex:
            print("{} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), "update_info_for_ocr", ex))
        return  ok

    def update_delete_info_ocr(self, **kwargs):
        id_data = kwargs.pop("id")
        ok = False
        try:
            OcrWorkSafe.objects.filter(atld_id= id_data).update(confirm=2)

            if not OcrWorkSafe.objects.filter(atld_id=id_data).exists():
                print("{} >> id khong ton tai trong bang log ocr: {}".format(get_str_datetime_now_import_db(), id_data))

                return ok
            queryset = OcrWorkSafe.objects.filter(atld_id=id_data)
            queryset.delete()

        except Exception as ex:
            print("{} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), "update_delete_info_ocr", ex))
        return ok



    def api_check_img_from_ocr(self, request):
        fname = "api_check_img_from_ocr"
        # data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        data_token = get_data_token(request)
        user_email = data_token.get("email")
        data = request.data
        try:
            number_file = data.get("numberFile", 0)
            _type = data.get("type", "")

            if int(number_file) > 0:
                status_code, msg_code, data_code = call_api_save_file(request, number_file, user_email, "")
                if status_code == 1:
                    list_img = data_code.get('linkFile', []) # sua cho nay
                    str_img = ''
                    if len(list_img) > 0:
                        # str_img = list_img[0]
                        list_img_new = []
                        for k in list_img:
                            # str_img = str_img.replace("download-file", "view-file")
                            str_img = k.replace("download-file", "view-file")
                            str_img = str_img.replace(PUBLIC_URL, MEDIA_URL)
                            list_img_new.append(str_img)



                        #todo Call api check img hoac api lay thong tin
                        params = {
                                "pdf_urls": list_img_new,
                                "type": "ATLD"
                        }
                        result, status_call = call_api_info_ocr(params, get_str_datetime_now_import_db())
                        if status_call == 1:
                            status_code_ocr = result.get("statusCode", 2)
                            data_api = result.get("data", [])

                            if status_code_ocr != 1:
                                return response_data(data={}, message="Có lỗi trong quá trình xử lý ocr", status=STATUS_CODE_ERROR_LOGIC)

                            if len(data_api) == 0:
                                return response_data(data={}, message="Không tìm thấy thông tin từ ocr", status=STATUS_CODE_ERROR_LOGIC)

                            list_right_child_depart = get_child_depart_permission_from_token(data_token=data_token,
                                                                                             type_screen="train")
                            list_data_exist = self.list_data_exist(list_right_child_depart)
                            list_train_available = SafeCardSerializer.list_train_available(fname=fname)
                            query_emp_not_working = Employee.objects.filter(
                                child_depart__in=tuple(list_right_child_depart), status_working=0).values_list(
                                'emp_code', flat=True)

                            query_emp = Employee.objects.filter(
                                child_depart__in=tuple(list_right_child_depart)).values_list('emp_code',
                                                                                             flat=True)

                            dict_info_emp_code = EmployeeSerializer.get_info_present_atld(query_emp)


                            list_data_pass = []
                            list_data_faild = []


                            list_data_process = []
                            list_item = []
                            for i_data in data_api:
                                data_url = i_data.get("data", {})
                                status_url = i_data.get("statusCode", 2)
                                str_url = i_data.get("pdf_url", "")
                                str_url = str_url.replace(MEDIA_URL, PUBLIC_URL)


                                if status_url != 1:
                                    data_url = {
                                        "empCode": "",
                                        "numberCard": "",
                                        "jobTitle": "",
                                        "trainingGroup": "",
                                        "trainingStartDate": "",
                                        "trainingEndDate": "",
                                        "dateCertificate": "",
                                        "expirationDate": ""
                                    }

                                dict_check = self.check_data_from_ocr(data=data_url, pdf_url=str_url,
                                                                      statusCode=status_url, query_emp=query_emp,
                                                                      query_emp_not_working=query_emp_not_working,
                                                                      list_data_process=list_data_process, user_email=user_email,
                                                                      list_data_exist=list_data_exist,
                                                                      list_train_available=list_train_available)


                                str_err = dict_check.get("errors", "")
                                save_flag = dict_check.get("save_flag", 2)
                                list_data_process = dict_check.get("list_data_process", [])
                                item_process = dict_check.get("item", {})
                                if len(item_process) > 0 :
                                    list_item.append(item_process)

                                # list_data_process.extend(list_data_process_after)

                                data_dict = {
                                    "Mã nhân viên": "",
                                    "Họ tên": "",
                                    "Số thẻ": "",
                                    "Vị trí công việc": "",
                                    "Nhóm đào tạo": "",
                                    "Ngày bắt đầu đào tạo": "",
                                    "Ngày kết thúc đào tạo": "",
                                    "Ngày cấp thẻ ATLĐ": "",
                                    "Ngày hết hạn ATLĐ": "",
                                    "Tên file hình ảnh/chứng nhận": str_url,
                                    "statusUrl": status_url,
                                    "Nội dung": "Ocr không nhận dạng",
                                    "saveFlag": save_flag

                                }


                                # status_url thong tin tu ocr tra ve, save_flag check thong tin du lieu


                                if status_url == 1 :
                                    data_list = list(data_url.keys())
                                    key_list = list(WORK_SAFE_IMPORT.keys())
                                    value_list = list(WORK_SAFE_IMPORT.values())
                                    # data_list = set(value_list) & set(data_list)
                                    data_dict = {}

                                    emp_code_rs = data_url['empCode']
                                    data_dict.update({"Họ tên": ''})
                                    if not is_null_or_empty(emp_code_rs):
                                        emp_name = dict_info_emp_code.get(emp_code_rs, {}).get("name", '')
                                        data_dict.update({"Họ tên": emp_name})


                                    for item2 in data_list:
                                        if item2 in key_list:
                                            index = key_list.index(item2)

                                            data_dict[value_list[index]] = data_url.pop(item2, None)

                                    data_dict.update({
                                        "Tên file hình ảnh/chứng nhận": str_url.replace(MEDIA_URL, PUBLIC_URL)
                                    })




                                    data_dict.update({
                                        # "url" : str_url,
                                        "statusUrl": status_url,
                                        "saveFlag": save_flag,
                                        "Nội dung": str_err
                                    })




                                    if save_flag == 1:
                                        list_data_pass.append(data_dict)
                                    else:
                                        list_data_faild.append(data_dict)

                                else:
                                    list_data_faild.append(data_dict)

                            dict_output = {
                                "listPass": list_data_pass,
                                "listFail": list_data_faild
                            }

                            self.insert_info_ocr(data=list_item)

                            return response_data(data=dict_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

                        elif status_call == 2:
                            return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
                        elif status_call == 503:
                            return response_data(data={}, message="Không thể call ocr", status=STATUS_CODE_ERROR_LOGIC)
                        else:
                            return response_data(data={}, message="Có lỗi trong quá trình call ocr", status=STATUS_CODE_ERROR_LOGIC)

                        # return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
                    else:
                        return response_data(data={}, message="Có lỗi trong quá trình upfile", status=STATUS_CODE_ERROR_LOGIC)


                    # str_img = ""
                    # for item in list_img:
                    #     if str_img == "":
                    #         str_img = item
                    #     else:
                    #         str_img += ";" + item
                    # data_save['pictureCertificate'] = str_img
                    # data.pictureCertificate = str_img
                    # print("---------------------UP HINH THANH CONG--------------------")
                    # print(list_img)
                else:
                    # print("---------------------UP HINH --------------------")
                    # print(msg_code)
                    return response_data(data={}, message="Không thể up hình", status=status_code)
        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), fname, ex))

            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def check_data_from_ocr(self, **kwargs):

        item = kwargs.pop("data", {})
        link_url = kwargs.pop("pdf_url", "")
        status_link = kwargs.pop("statusCode", 2)
        query_emp_not_working = kwargs.pop("query_emp_not_working", [])
        query_emp = kwargs.pop("query_emp", [])
        list_data_process_init = kwargs.pop("list_data_process", [])
        user_email = kwargs.pop("user_email", '')
        list_data_exist = kwargs.pop('list_data_exist', [])
        list_train_available = kwargs.pop('list_train_available', [])
        save_flag = 1

        #save_flag = 2 (loi, cho import), save_flag = 1 (ko loi), save_flag = 0 (loi nghiem trong)

        # list_data_process = []
        errors = []

        try:
            if status_link == 1:
                ma_nv = item.get("empCode")
                number_card = item.get("numberCard")
                date_provide_card = item.get("dateCertificate")
                date_expire_card = item.get("expirationDate")
                date_start_train = item.get("trainingStartDate")
                date_end_train = item.get("trainingEndDate")
                nhom_dao_tao = item.get("trainingGroup")
                if is_null_or_empty(ma_nv):
                    errors.append("Mã nhân viên bị trống")
                    save_flag = 0
                    # continue

                if is_null_or_empty(date_provide_card):
                    errors.append("Ngày cấp thẻ ATLĐ bị trống")
                    save_flag = 0
                    # continue

                if is_null_or_empty(date_expire_card):
                    errors.append("Ngày cấp thẻ ATLĐ bị trống")
                    save_flag = 0
                    # continue

                if is_null_or_empty(date_start_train):
                    errors.append("Ngày cấp thẻ ATLĐ bị trống")
                    save_flag = 0
                    # continue

                if is_null_or_empty(date_end_train):
                    errors.append("Ngày cấp thẻ ATLĐ bị trống")
                    save_flag = 0
                    # continue

                if not is_null_or_empty(ma_nv):
                    # if not SafeCardSerializer.check_emp_code_in_list_train(ma_nv):
                    if ma_nv not in list_train_available:
                        errors.append("Nhân viên không có trong danh sách đào tạo")
                        if save_flag == 1:
                            save_flag = 2

                    if not len(ma_nv) == 8:
                        errors.append("Mã nhân viên không đúng định dạng")
                        save_flag = 0
                        # continue

                # if Employee.objects.filter(emp_code=ma_nv, status_working=0).exists():
                    if ma_nv in query_emp_not_working:
                        errors.append("Thông tin nhân viên đã nghỉ việc")
                        if save_flag == 1:
                            save_flag = 2

                    # if not Employee.objects.filter(emp_code=ma_nv, child_depart__in=tuple(list_right_child_depart)).exists():
                    if ma_nv not in query_emp:
                        errors.append(
                            "Thông tin nhân viên không tồn tại trên hệ thống.")
                        save_flag = 0
                        # continue
                else:
                    job_title = EmployeeSerializer.get_job_title_from_emp_code(
                        emp_code=ma_nv)
                    item.update({
                        'jobTitle': job_title
                    })




                check_provide_card = check_input_str_format_date(date_provide_card)
                if not check_provide_card:
                    errors.append(
                        "Ngày cấp thẻ không đúng định dạng")
                    save_flag = 0
                    # continue

                check_expire_card = check_input_str_format_date(date_expire_card)
                if not check_expire_card:
                    errors.append(
                        "Ngày hết hạn thẻ không đúng định dạng")
                    save_flag = 0
                    # continue
                else:
                    item['statusCertificate'] = SafeCardSerializer.get_status_card_from_expire_date(
                        item['expirationDate'])

                check_start_train = check_input_str_format_date(date_start_train)
                if not check_start_train:
                    errors.append(
                        "Ngày bắt đầu đào tạo không đúng định dạng")
                    save_flag = 0
                    # continue

                check_end_train = check_input_str_format_date(date_end_train)
                if not check_end_train:
                    errors.append(
                        "Ngày kết thúc đào tạo không đúng định dạng")
                    save_flag = 0
                    # continue



                item.update({
                    "certificate": ""
                })

                if not is_null_or_empty(ma_nv):
                    job_title = EmployeeSerializer.get_job_title_from_emp_code(emp_code=ma_nv)
                    train_group_fr_db, type_card = TypeGroupTrainingWorkSafeSerializer.get_info_from_job_title(job_title)
                    item.update({"certificate": type_card})

                    if train_group_fr_db != nhom_dao_tao:
                        if not is_null_or_empty(nhom_dao_tao):
                            if nhom_dao_tao.title() not in GROUP_TRAIN_WORK_SAFE:
                                save_flag = 0
                                errors.append("Nhân viên có nhóm đào tạo không đúng")

                if check_expire_card and check_provide_card and check_start_train and check_end_train and not is_null_or_empty(ma_nv):

                    if is_null_or_empty(number_card):

                        if (ma_nv, date_provide_card,date_expire_card,date_start_train,date_end_train, '') in list_data_exist:
                            errors.append("Nhân viên đã tồn tại trên hệ thống")
                            save_flag = 0

                    else:
                        if (ma_nv, date_provide_card,date_expire_card,date_start_train,date_end_train, number_card) in list_data_exist:
                            errors.append("Nhân viên đã tồn tại trên hệ thống")
                            save_flag = 0

                if item not in list_data_process_init:
                    list_data_process_init.append(item)
                else:
                    errors.append("Dữ liệu bị trùng lập")
                    save_flag = 0
            else:
                errors = ['OCR không thể nhận dạng']
                save_flag = 0


            item.update({
                "statusFile": status_link,
                "createdBy": user_email,
                "createdAt": get_str_datetime_now_import_db(),
                "pictureCertificate": link_url,
                "confirm": 0
            })

        except Exception as ex:
            errors = ['Không thể check thông tin']
            save_flag = 2
            print("{} >> check_data_from_ocr >> Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))

        if len(errors) == 0 and save_flag == 1:
            errors = ["Thông tin đã đạt yêu cầu"]


        dict_output = {
            "errors": "<br/>".join(errors),
            "save_flag": save_flag,
            "list_data_process": list_data_process_init,
            "item": item.copy()
        }

        return dict_output


    def insert_info_ocr(self, **kwargs):
        id_data = 0
        data = kwargs.pop("data")
        try:
            data_save = []
            for i in data:
                for k , v in i.items():
                    if is_null_or_empty(v):
                        i[k] = None

                data_save.append(i)

            serializer = OcrWorkSafeSerializer(data=data_save, many=True)
            if not serializer.is_valid():
                print(data_save)
                print(serializer.errors)
                return "k"
            if not serializer.save():
                print(data_save)
                print("insert_info_ocr >> " + "Không thể kiểm save")
                return "j"

        except Exception as ex:
            print("{} >> insert_info_ocr >> Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))
        return id_data

    def api_get_info_error_data(self, request):

        data_token = get_data_token(request)
        user_email = data_token.get("email")

        fname = "api_get_info_error_data"
        data_input = request.data
        parent_depart = data_input.get('parentDepart', [])
        child_depart = data_input.get("childDepart", [])
        emp_code_input = data_input.get("empCode", "")
        state_card = data_input.get("cardStatus", "")

        from_date = data_input.get("fromDate")
        to_date = data_input.get("toDate")
        try:

            role = get_feature_role_atld_from_data_token(data_token, fname=fname)

            ok_role = check_role_on_api(role, screen="train", fname=fname)
            if not ok_role:
                return response_data(data={}, message="Bạn không có quyền thực hiện tính năng này",
                                     status=STATUS_CODE_INVALID_INPUT)

            queryset = OcrWorkSafe.objects.filter(created_by=user_email)
            if not is_null_or_empty(emp_code_input):
                queryset = queryset.filter(emp_code=emp_code_input)

            if not is_null_or_empty(state_card):
                queryset = queryset.filter(tinh_trang_the_chung_chi=state_card)

            if not is_null_or_empty(from_date) and not is_null_or_empty(to_date):
                from_date_db = convert_str_date_input_date_db(from_date)
                to_date_db = convert_str_date_input_date_db(to_date)
                from_date_db = from_date_db + " 00:00:00"
                to_date_db = to_date_db + " 23:59:59"
                queryset = queryset.filter(created_time__range=[from_date_db, to_date_db])


            queryset = queryset.exclude(confirm__in=(1,2)).order_by('-created_time')

            count = queryset.count()
            # paginator = StandardPagination()
            paginator = StandardPagination()
            if "perPage" in data_input and isinstance(data_input["perPage"], int):
                paginator.page_size = data_input["perPage"]
            result = paginator.paginate_queryset(queryset, request)
            serializer = OcrWorkSafeSerializer(result, many=True)
            list_data = serializer.data

            # print(queryset.query)

            if len(list_data) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            list_emp_code_result = []
            for j in list_data:
                list_emp_code_result.append(j['empCode'])

            dict_info_list_emp_code = EmployeeSerializer.get_info_present_atld(list_emp_code_result)

            for i in list_data:
                emp_code = i['empCode']
                value = dict_info_list_emp_code.get(emp_code, {})
                if len(value) == 0:
                    i.update({
                        "childDepart": None,
                        "dateJoinCompany": None,
                        "name": None,
                        "sex": None,
                        "birthday": None,
                        "cmnd": None,
                        "statusWorking": None,
                        "dateQuitJob": None,
                        "jobTitle": None,

                    })
                else:
                    i.update(value)

                child_depart = i['childDepart']

                dict_info_child_depart = DepartmentSerializer.get_parent_depart_from_child_depart(
                    child_depart=[child_depart])
                parent_depart = dict_info_child_depart.get(child_depart, {})
                i['parentDepart'] = parent_depart.get('parentDepart', '')
                i['branch'] = parent_depart.get('department', '')
                i['sex'] = convert_sex(i['sex'], fname)

            dict_col = {
                "parentDepart": "Vùng",
                "branch": "Đơn vị",
                "childDepart": "Bộ phận",
                "empCode": "Mã NV",
                "name": "Họ và tên",
                "jobTitle": "Vị trí công việc",
                "dateJoinCompany": "Ngày vào công ty",
                "sex": "Giới tính",
                "birthday": "Ngày sinh",
                "cmnd": "CMND/CCCD",
                "trainingGroup": "Nhóm đào tạo",
                "certificate": "Đối tượng cấp thẻ/Chứng nhận",
                "pictureCertificate": "Tên file hình ảnh/chứng nhận"

            }


            data = {
                'numberPage': count // StandardPagination.page_size + 1,
                'numberRow': count,
                "data": list_data,
                "dictCol": dict_col
                # 'newsList': serializer.data
            }
            return response_data(data=data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)



        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data="", message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    def insert_info_log_delete_work_safe_card(self, info_card, card_id, user_email):
        ok = True
        try:
            data_delete = {}
            data_delete['card_id'] = card_id
            data_delete['infoCard'] = str(info_card)
            data_delete['updateBy'] = user_email
            data_delete['updateAt'] = get_str_datetime_now_import_db()
            serializer = HistoriesDeleteCardSerializer(data=data_delete)
            if not serializer.is_valid():
                ok = False
                print(serializer.errors)
                return ok
            if not serializer.save():
                print("import lich su khong thanh cong")
                ok = False

                return ok
            ok = True

        except Exception as ex:
            ok = False
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(),
                                                     "insert_info_log_delete_work_safe_card", ex))
        return ok


    def auto_update_status_card_v2(self, request):
        # dung de updat nhung cot con trong
        fname = "auto_update_status_card"
        try:
            list_id_sap_het_han = []
            list_id_het_han = []
            list_id_con_han = []
            list_chua_cap = []

            today = datetime.now().date()
            day_45 = today + timedelta(days=45)
            
            queryset = SafeCard.objects.filter(Q(tinh_trang_the_chung_chi='') | Q(tinh_trang_the_chung_chi__isnull=True))
            for data in queryset:
                id_card = data.atld_id
                ngay_het_han = data.ngay_het_han_ATLD
                ngay_cap_the = data.ngay_cap_the_ATLD
                tinh_trang_the_chung_chi = data.tinh_trang_the_chung_chi
                if is_null_or_empty(tinh_trang_the_chung_chi):
                    if ngay_het_han is not None:
                        if ngay_het_han <= today:
                            list_id_het_han.append(id_card)
                        elif ngay_het_han > today:
                            if ngay_het_han > day_45:
                                list_id_con_han.append(id_card)

                            if ngay_het_han <= day_45:
                                list_id_sap_het_han.append(id_card)
                    else:

                        if is_null_or_empty(ngay_cap_the):
                            list_chua_cap.append(id_card)





            if len(list_id_sap_het_han) > 0:
                SafeCard.objects.filter(atld_id__in=tuple(list_id_sap_het_han)).update(tinh_trang_the_chung_chi="Sắp hết hạn")
                self.insert_info_log_delete_work_safe_card(list_id_sap_het_han, 77777, "update_sap_het_han")

            if len(list_id_con_han) > 0 :
                SafeCard.objects.filter(atld_id__in=tuple(list_id_con_han)).update(
                    tinh_trang_the_chung_chi="Còn hạn")
                self.insert_info_log_delete_work_safe_card(list_id_con_han, 111111, "update_con_han")

            if len(list_id_het_han):
                SafeCard.objects.filter(atld_id__in=tuple(list_id_het_han)).update(
                    tinh_trang_the_chung_chi="Hết hạn")
                self.insert_info_log_delete_work_safe_card(list_id_het_han, 88888, "update_con_han")


            if len(list_chua_cap) > 0 :
                SafeCard.objects.filter(atld_id__in=tuple(list_chua_cap)).update(
                    tinh_trang_the_chung_chi="Chưa cấp")
                self.insert_info_log_delete_work_safe_card(list_chua_cap, 9999, "update_chua_cap")



            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> {} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def api_auto_update_info_safe_card(self, request):

        # dung de quet tam nhung thong tin bị sot
        fname = "api_auto_update_info_safe_card"
        try:
            qr_emp = Employee.objects.all().values('emp_code', 'job_title')
            qr_type_card = TypeGroupTrainingWorkSafe.objects.all().values('job_title', 'train_group', 'type_card')
            dict_type_card = {}
            dict_emp = {}
            for i in qr_type_card:
                dict_type_card.update({
                    i['job_title'] : {
                        "train_group": i['train_group'],
                        "type_card": i['type_card']
                    }
                })

            list_success = []
            list_failed = []

            for k in qr_emp:
                emp_code = k['emp_code']
                job_title = k['job_title']
                dict_tmp_type = dict_type_card.get(job_title, {})
                train_group = dict_tmp_type.get('train_group', '')
                type_card = dict_tmp_type.get('type_card', '')

                if is_null_or_empty(train_group) or is_null_or_empty(type_card) :
                    list_failed.append(emp_code)
                else:
                    list_success.append(emp_code)
                dict_emp.update({
                    emp_code: {
                        "train_group": train_group,
                        "type_card": type_card
                    }
                })



            self.insert_info_log_delete_work_safe_card(list_success, 22222, "emp_code_ok")
            self.insert_info_log_delete_work_safe_card(list_failed, 33333, "emp_code_not_ok")


            qr_card = SafeCard.objects.filter(Q(nhom_dao_tao="") | Q(nhom_dao_tao__isnull=True)).values()

            # Q(x=1) | Q(y=2)
            list_card_1 = list(qr_card)
            list_id_card = []

            if len(list_card_1) > 0 :
                for j in list_card_1:
                    emp_code_rs = j['emp_code']
                    id_card = j['atld_id']

                    train_group_ = dict_emp.get(emp_code_rs, {})
                    train_group = train_group_.get("train_group")
                    if not is_null_or_empty(train_group):

                        SafeCard.objects.filter(atld_id=id_card).update(nhom_dao_tao=train_group)
                        list_id_card.append(id_card)

            self.insert_info_log_delete_work_safe_card(list_id_card, 4444, "list_nhom_dao_tao")

            qr_card_2 = SafeCard.objects.filter(Q(cap_the_chung_chi="") | Q(cap_the_chung_chi__isnull=True)).values("emp_code",
                                                                                                        "atld_id")

            list_card_2 = list(qr_card_2)
            list_id_card = []

            if len(list_card_2) > 0 :
                for l in list_card_2:
                    emp_code_rs = l['emp_code']
                    id_card = l['atld_id']
                    type_card_ = dict_emp.get(emp_code_rs, {})
                    type_card = type_card_.get('type_card')
                    SafeCard.objects.filter(atld_id=id_card).update(cap_the_chung_chi=type_card)
                    list_id_card.append(id_card)

            self.insert_info_log_delete_work_safe_card(list_id_card, 4444, "list_loai_the")

            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)







        except Exception as ex:
            print("{} >> {} >> Error/loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def api_update_info_emp(self, request):
        fname = "api_update_info_emp"
        try:
            qr = SafeCard.objects.filter(emp_name="").values('emp_code', 'atld_id')

            qr2 = SafeCard.objects.filter(emp_name="").values_list('emp_code', flat=True)

            list_emp = list(qr2)

            dict_emp = EmployeeSerializer.get_info_present_atld(list_emp)

            for i in qr:
                emp_code = i['emp_code']
                id_card = i['atld_id']
                dict_info = dict_emp.get(emp_code, {})
                job_title = dict_info.get('jobTitle', '')
                emp_name = dict_info.get('name', '')
                ngay_sinh = dict_info.get('birthday')
                str_import_ngay_sinh = None
                if not is_null_or_empty(ngay_sinh):
                    str_import_ngay_sinh = convert_str_date_input_date_db(ngay_sinh)
                date_join_company = dict_info.get('dateJoinCompany')
                str_date_join = None
                if not is_null_or_empty(date_join_company):
                    str_date_join = convert_str_date_input_date_db(date_join_company)

                parent_depart = dict_info.get('parentDepart', '')
                agency = dict_info.get('agency', '')
                sex = dict_info.get('sex', '')
                date_quit = dict_info.get('dateQuitJob')
                str_date_quit = None
                if not is_null_or_empty(date_quit):
                    str_date_quit = convert_str_date_input_date_db(date_quit)

                cmnd = dict_info.get('cmnd')
                child_depart = dict_info.get('childDepart', '')

                SafeCard.objects.filter(atld_id=id_card).update(sex=sex,cmnd=cmnd, date_join_company=str_date_join,
                                                                date_quit_job=str_date_quit,agency=agency,
                                                                parent_depart=parent_depart,birthday=str_import_ngay_sinh,
                                                                emp_name=emp_name, job_title=job_title,child_depart=child_depart)

                return response_data(data="", message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)





        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def list_data_exist(self, list_child_depart_right):
        # list_child_depart_right = ['PCMUUSR']
        list_data = []
        try:
            qr_emp_code = Employee.objects.filter(child_depart__in=tuple(list_child_depart_right)).values_list('emp_code', flat=True)
            list_code = list(qr_emp_code)
            qr_card = SafeCard.objects.filter(emp_code__in=tuple(list_code)).values('emp_code', 'ngay_cap_the_ATLD',
                                                                                    'ngay_het_han_ATLD', 'ngay_bat_dau_dao_tao',
                                                                                    'ngay_ket_thuc_dao_tao', 'number_card')
            for i in qr_card:
                # list_data.append(convert_dict_data_db(i))
                tmp = convert_dict_data_db(i)
                number_card = tmp['number_card']
                if not is_null_or_empty(number_card):
                    t_data = (tmp['emp_code'], tmp['ngay_cap_the_ATLD'], tmp['ngay_het_han_ATLD'],
                              tmp['ngay_bat_dau_dao_tao'], tmp['ngay_ket_thuc_dao_tao'], tmp['number_card'])
                else:
                    t_data = (tmp['emp_code'], tmp['ngay_cap_the_ATLD'], tmp['ngay_het_han_ATLD'],
                              tmp['ngay_bat_dau_dao_tao'], tmp['ngay_ket_thuc_dao_tao'], '')

                list_data.append(t_data)
        except Exception as ex:
            print("{} >> list_data_exist >> Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))
        return list_data





































