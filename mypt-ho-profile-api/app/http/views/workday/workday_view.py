from ...validations.hr_validate import *
from ....core.helpers.response import *
from ....core.helpers.helper import *
from ....core.helpers.global_variable import *
from ...models.hr import *
from ...serializers.hr_serializer import *
from ...paginations.custom_pagination import *
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
from ....configs.excel_table import *
from datetime import datetime
from django.db.models import Q

class WorkdayView(ViewSet):
    def info_emp_fr_branch(self, request):
        fname = "info_emp_fr_branch"
        # service gọi noi bo
        data_input = request.data
        branch = data_input.get("branch", "")
        try:
            queryset = Department.objects.filter(branch=branch)
            s = DepartmentSerializer(queryset, many=True, emp_info=True)
            list_data = s.data
            if len(list_data) > 0:
                list_code = []
                dict_code = {}
                for i in list_data:
                    list_info_emp = i.get("emp_info", [])
                    child_depart = i.get("childDepart", "")
                    child_depart1 = i.get("childDepart1", "")
                    if len(list_info_emp) > 0 :
                        for j in list_info_emp:
                            code = j.get('code', '')
                            name = j.get('name', '')
                            list_code.append(code)
                            dict_code.update({
                                code: {
                                    "name": name,
                                    "childDepart": child_depart,
                                    "childDepart1": child_depart1,


                                }
                            })
                if len(list_code) > 0:
                    data_output = {
                        "listCode": list_code,
                        "dictCode": dict_code
                    }
                    return response_data(data=data_output, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)
                else:
                    return response_data(data={}, status=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA)

            else:
                return response_data(data={}, status=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA)

        except Exception as ex:
            print("{}-------------".format(fname))
            print(data_input)
            print(ex)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)

    def api_detail_emp_for_workday(self, request):
        fname = 'api_detail_emp_for_workday'
        time_log = get_str_datetime_now_import_db()
        try:
            # qr = Employee.objects.filter(status_working=1).values('emp_code', 'emp_name', 'email', 'job_title',
            #                                                       'date_join_company', 'date_quit_job', 'child_depart')
            start_month, end_month = get_start_date_and_end_date_of_last_month()

            qr = Employee.objects.filter(Q(date_quit_job__isnull=True)|Q(date_quit_job__gte=start_month)).values('emp_code', 'emp_name', 'email', 'job_title',
                                                                  'date_join_company', 'date_quit_job', 'child_depart')

            if len(qr) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            dict_data = {}
            for i in qr:
                date_join_company = i['date_join_company']
                str_date_join_company = None
                if date_join_company is not None:
                    str_date_join_company = convert_date_db_to_str_date_export(date_join_company)
                date_quit_job = i['date_quit_job']
                str_date_quit_job = None
                if date_quit_job is not None:
                    str_date_quit_job = convert_date_db_to_str_date_export(date_quit_job)
                job_title = i['job_title']
                emp_code = i['emp_code']
                emp_name = i['emp_name']
                emp_email = i['email']
                level_3 = i['child_depart']

                dict_data.update({
                    emp_code:{
                        'name': emp_name,
                        'email': emp_email,
                        "job_postion": job_title,
                        "date_join": str_date_join_company,
                        "date_leaving": str_date_quit_job,
                        "level_3": level_3
                    }
                })
            return response_data(data=dict_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)


        except Exception as ex:
            print("{} >> {} Error/Loi: {} ".format(time_log, fname, ex))
            return response_data(data={}, message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)


    def api_detail_emp_for_leave_application(self, request):
        fname = 'api_detail_emp_for_workday'
        time_log = get_str_datetime_now_import_db()
        try:
            start_month, end_month = get_start_date_and_end_date_of_last_month()
            qr = Employee.objects.filter(Q(date_quit_job__isnull=True)|Q(date_quit_job__gte=start_month)).values('emp_code', 'emp_name', 'email',  'child_depart')

            if len(qr) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


            qr_department = Department.objects.all().values('child_depart', 'chi_nhanh', 'branch', 'parent_depart', 'dien_giai')
            dict_department = {}
            for j in qr_department:
                child_depart = j['child_depart']
                chi_nhanh = j['chi_nhanh']
                branch = j['branch']
                parent_depart = j['parent_depart']
                dien_giai = j['dien_giai']
                dict_department.update({
                    child_depart: {
                        "level_2": parent_depart,
                        "level_3": chi_nhanh,
                        "level_1": branch,
                        'level_5': dien_giai
                    }
                })

            dict_data = {}
            for i in qr:


                emp_code = i['emp_code']
                emp_name = i['emp_name']
                emp_email = i['email']
                child_depart = i['child_depart']
                dict_department_detail = dict_department.get(child_depart, {})
                dict_tmp = {}
                if len(dict_department_detail) > 0:
                    dict_tmp = dict_department_detail.copy()
                else:
                    dict_tmp.update({
                        "level_2": None,
                        "level_3": None,
                        "level_1": None,
                        'level_5': None

                    })
                dict_tmp.update({
                    'level_4': child_depart
                })
                dict_tmp.update({
                    'name': emp_name,
                    'email': emp_email,
                })
                dict_data.update({
                    emp_code: dict_tmp
                })





                # dict_data.update({
                #     emp_code:{
                #         'name': emp_name,
                #         'email': emp_email,
                #         'level_4': child_depart,
                #     }
                # })
            return response_data(data=dict_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)


        except Exception as ex:
            print("{} >> {} Error/Loi: {} ".format(time_log, fname, ex))
            return response_data(data="{} >> {} Error/Loi: {} ".format(time_log, fname, ex), message=MESSAGE_API_FAILED, status=STATUS_CODE_ERROR_LOGIC)



    def check_status_from_emp_code(self, request):
        # api kiem tra emp code hợp lệ
        data_input = request.data
        emp_code = data_input.get("emp_code")
        try:
            if is_null_or_empty(emp_code):
                return response_data(data={}, message="Không tìm thấy mã nhân viên", status=STATUS_CODE_INVALID_INPUT)

            # if Employee.objects.filter(emp_code=emp_code, status_working=1).exists():
            #     return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
            #
            # else:
            #     return response_data(data={}, message="Mã nhân viên không tồn tại trên hệ thống vui lòng kiểm tra ", status=STATUS_CODE_NO_DATA)

            data_info = Employee.objects.filter(emp_code=emp_code).values()
            if len(data_info) == 0:
                return response_data(data={}, message="Mã nhân viên không tồn tại trên hệ thống", status=STATUS_CODE_NO_DATA)

            state = data_info[0]['status_working']
            if state == 1:
                return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

            else:
                return response_data(data={}, message="Vui lòng kiểm tra trạng thái làm việc của nhân viên", status=STATUS_CODE_NO_DATA)



        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), "check_emp_code", ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    def get_list_emp_code(self, request):
        try:
            # queryset = Employee.objects.filter(status_working=1).values('emp_code') // lay data cot emp_code
            queryset = Employee.objects.filter(status_working=1).values('emp_code')
            if len(queryset) == 0:
                return response_data(data=[], message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            list_data = []
            for i in queryset:
                list_data.append(i['emp_code'])



            return response_data(data=list_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), "get_list_emp_code", ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)
