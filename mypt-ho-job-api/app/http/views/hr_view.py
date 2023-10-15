import collections
import datetime

from rest_framework.viewsets import ViewSet
from app.core.helpers.response import response_data
from app.http.serializers.hr_serializer import *
from ..paginations.custom_pagination import StandardPagination
from ..paginations.working_schedule_pagination import WorkingSchedulePagination
from ...configs.excel_table import (
    SALARY_FOREIGN_EN, SALARY_HACH_TOAN_OUTPUT
)
from ...configs.import_salary import *
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers import auth_session_handler as authSessionHandler
from ...core.helpers.helper import call_api
from django.conf import settings as project_settings
from django.db import transaction
import json
from decouple import config

class HrView(ViewSet):
    def get_show_working_schedule(self, request):
        data = request.data
        serializer = MonthYearSearchValidate(data=data)

        if not serializer.is_valid():
            return response_data(status=0, message=serializer.errors)
        thang = serializer.validated_data['month']
        nam = serializer.validated_data['year']
        branch = serializer.validated_data['branch']

        list_vung = self.get_list_parent_depart_from_branch(branch=branch)

        thang_nam = f"T{thang}.{nam}" if thang > 9 else f"T0{thang}.{nam}"

        lst_working_schedule = WorkingSchedule.objects.filter(thang=thang, thang_nam=thang_nam,
                                                              vung__in=list_vung).order_by("ho_va_ten")
        page_size = 10
        params = request.query_params
        if 'page_size' in params:
            page_size = params['page_size']
        paginator = WorkingSchedulePagination()
        paginator.page_size = page_size
        result_page = paginator.paginate_queryset(lst_working_schedule, request)
        serializer = WorkingScheduleSerializer(result_page, many=True)

        return paginator.get_paginated_response(data=serializer.data)

    def post_import_working_schedule(self, request):
        data = request.data
        current_date = datetime.now()

        # luôn import tháng T-1
        target_month = current_date.month - 1 if current_date.month != 1 else 12
        target_year = current_date.year if target_month != 12 else current_date.year - 1
        target_month_year = f'T{target_month}.{target_year}' if target_month > 9 else f'T0{target_month}.{target_year}'

        try:
            form_lct = ['vung', 'chi_nhanh', 'phong_ban', 'MNV', 'ho_va_ten',
                        'vi_tri', 'account', 'tu_ngay', 'den_ngay', 'ghi_chu1', 'ghi_chu2']
            form_lct_required = ['vung', 'chi_nhanh', 'phong_ban', 'MNV', 'ho_va_ten',
                                 'vi_tri', 'tu_ngay', 'den_ngay']
            inp_field = set(data['list_schedule'][0].keys())

            for rq in form_lct_required:
                if rq not in inp_field:
                    return response_data(status=0, message="Form import Công tác chưa đúng. Vui lòng kiểm tra lại")

            if not inp_field.issubset(form_lct):
                return response_data(status=0, message="Form import Công tác chưa đúng. Vui lòng kiểm tra lại")
        except Exception as ex:
            print(ex)
            return response_data(status=0, message={"errors_format": ["Không có dữ liệu import"]})

        serializer_search = BranchSearchValidate(data=data)
        if not serializer_search.is_valid():
            return response_data(status=0, message={"errors_format": [serializer_search.errors]})
        inp_branch = serializer_search.validated_data['branch']

        # Không cần truyền lên tháng nữa
        # inp_month = serializer_search.validated_data['month']
        # inp_year = serializer_search.validated_data['year']

        list_schedule = data['list_schedule']
        lst_duplicate = []
        errors_duplicate = []
        errors_format = []

        # bước 1: kiểm tra lỗi
        for idx, item in enumerate(list_schedule):
            item['thang'] = target_month
            item['thang_nam'] = target_month_year
            serializer = WorkingScheduleSerializer(data=item)

            if not serializer.is_valid():
                for error_item in serializer:
                    if error_item.errors:
                        errors_format.append(f"Dòng số {idx + 2}: " + error_item.errors[0])
            else:
                item_d = {
                    "MNV": serializer.validated_data['MNV'],
                    "tu_ngay":   serializer.validated_data['tu_ngay'],
                    "den_ngay": serializer.validated_data['den_ngay'],
                }
                if item_d in lst_duplicate:
                    dup_idx = lst_duplicate.index(item_d)
                    errors_duplicate.append(f"Dòng số {idx + 2} bị trùng với dòng số {dup_idx + 2}")

                lst_duplicate.append(item_d)

            serializer = FromDateToDateSerializer(data=item)

            if not serializer.is_valid():
                if 'non_field_errors' in serializer.errors:
                    errors_format.append((f"Dòng số {idx + 2}: " + serializer.errors['non_field_errors'][0]))

        if errors_format or errors_duplicate:
            return response_data(status=0, message={
                "errors_format": errors_format, "errors_duplicate": errors_duplicate})

        # bước 2: lưu data
        if len(list_schedule) > 0:
            for item in list_schedule:
                schedule_info_dict = OrderedDict(dict.fromkeys([f" {i}" for i in range(1, 32)], 0))
                serializer_date = FromDateToDateSerializer(data=item)
                # đã kiểm tra data ở trên nên bước này pass
                if not serializer_date.is_valid():
                    pass
                from_date = serializer_date.validated_data['tu_ngay']
                to_date = serializer_date.validated_data['den_ngay']
                serializer_detail = WorkingScheduleSerializer(data=item)
                if not serializer_detail.is_valid():
                    pass
                date_range = self.get_date_range(from_date=from_date, to_date=to_date)
                for item_date in date_range:
                    if target_year == item_date.year and target_month == item_date.month:
                        schedule_info_dict[f' {item_date.day}'] = 1

                item['schedule_info'] = json.dumps(schedule_info_dict)

            serializer = WorkingScheduleSerializer(data=list_schedule, many=True)
            if not serializer.is_valid():
                return response_data(status=0, message="Không import được lịch công tác")

            try:
                with transaction.atomic():
                    # Xóa DB tháng cũ
                    list_vung = self.get_list_parent_depart_from_branch(branch=inp_branch)

                    WorkingSchedule.objects.filter(
                        thang=target_month, thang_nam=target_month_year, vung__in=list_vung).delete()
                    instances = [WorkingSchedule(**save_data) for save_data in serializer.validated_data]
                    WorkingSchedule.objects.bulk_create(instances)
            except Exception as ex:
                print(ex)
                return response_data(status=0, message='Không import được lịch công tác')
        else:
            return response_data(status=0, message="Không có dòng dữ liệu nào")

        # Đẩy lịch công tác lên powerbi
        try:
            lst_working_schedule = WorkingSchedule.objects.filter(thang=target_month, thang_nam=target_month_year,
                                                                  vung__in=list_vung).order_by("ho_va_ten")

            serializer = WorkingScheduleToBISerializer(lst_working_schedule, many=True)

            data_bi = serializer.data

            data_auth = helper.call_api(
                host=SERVICE_CONFIG["POWER-BI"][config('APP_ENV')],
                func=SERVICE_CONFIG["POWER-BI"]["login"]['func'],
                method=SERVICE_CONFIG["POWER-BI"]["login"]['method'],
                data=SERVICE_CONFIG["POWER-BI"]["user"]
            )
            data_auth = json.loads(data_auth)
            call_api(
                host=SERVICE_CONFIG["POWER-BI"][config('APP_ENV')],
                func=SERVICE_CONFIG["POWER-BI"]["cong_tac"]["func"],
                method=SERVICE_CONFIG["POWER-BI"]["cong_tac"]["method"],
                headers={
                    'Authorization': 'Bearer ' + str(data_auth["data"]["access_token"]),
                    'Content-Type': 'application/json'
                },
                data={'data': data_bi}
            )

        except Exception as ex:
            print('Lỗi đẩy lịch công tác qua power bi', ex)

        return response_data(status=1, message="Import lịch công tác thành công")

    def get_export_working_schedule(self, request):
        data = request.data

        serializer = MonthYearSearchValidate(data=data)

        if not serializer.is_valid():
            return response_data(status=0, message=serializer.errors)
        thang = serializer.validated_data['month']
        nam = serializer.validated_data['year']
        branch = serializer.validated_data['branch']

        thang_nam = f"T{thang}.{nam}" if thang > 9 else f"T0{thang}.{nam}"

        list_vung = self.get_list_parent_depart_from_branch(branch=branch)

        lst_working_schedule = WorkingSchedule.objects.filter(thang=thang, thang_nam=thang_nam,
                                                              vung__in=list_vung).order_by("ho_va_ten")

        serializer = ExportWorkingScheduleSerializer(lst_working_schedule, many=True)

        list_data = serializer.data
        dict_keys = {}
        if list_data:
            for key_item in list_data[0]:
                dict_keys.update({key_item: key_item.strip()})

        return response_data(data={"dict_keys": dict_keys, "list_data": list_data})

    def get_date_range(self, from_date, to_date):
        delta = to_date - from_date  # as timedelta
        days = [from_date + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_year_from_month_year(self, month_year):
        return int(month_year[-4:])

    def get_month_from_month_year(self, month_year):
        return int(month_year[1:3])

    def get_list_parent_depart_from_branch(self, branch):
        app_env = project_settings.APP_ENVIRONMENT
        list_vung = call_api(
            host=SERVICE_CONFIG["HO-PROFILE"][app_env],
            func=SERVICE_CONFIG["HO-PROFILE"]["get-parent-depart-from-branch"]["func"],
            method=SERVICE_CONFIG["HO-PROFILE"]["get-parent-depart-from-branch"]["method"],
            data={'branch': branch}
        )

        try:
            list_vung = json.loads(list_vung)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_export_working_schedule.__name__, ex))
            list_vung = None

        list_vung = list_vung['data']['list_data'] if list_vung else []

        return list_vung

    def list_info_in_block(self, request, field="code"):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return None
        # data = self.emp_by_child_depart(data=data, fields=[field])

        app_env = project_settings.APP_ENVIRONMENT

        data = call_api(
            host=SERVICE_CONFIG["HO-PROFILE"][app_env],
            func=SERVICE_CONFIG["HO-PROFILE"]["emp-code-by-child-depart"]["func"],
            method=SERVICE_CONFIG["HO-PROFILE"]["emp-code-by-child-depart"]["method"],
            data=data
        )

        try:
            data = json.loads(data)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_export_working_schedule.__name__, ex))
            data = []

        arr = []
        for item in data:
            arr.append(item[field])
        while None in arr:
            arr.remove(None)
        return arr

    def timeQuerySalary(self, monthStart, monthEnd, year):
        try:
            arr = []
            monthStart = int(monthStart)
            monthEnd = int(monthEnd)
            while monthStart <= monthEnd:
                if str(monthStart) in ["10", "11", "12"]:
                    arr.append(str(monthStart) + "-" + year)
                else:
                    arr.append("0" + str(monthStart) + "-" + year)
                monthStart += 1
            return arr
        except:
            return []

    def merge_foreign_en(self, data=None, foreign=None):
        # try:
        if data is None or data == []:
            return []
        if foreign is None:
            return []
        for item in data:
            list_foreign = foreign.keys()
            for value in list_foreign:
                list_key = foreign[value].keys()
                for key in list_key:
                    item[key] = item.pop(value)[0].pop(key, "")
        return data

    def merge_foreign(self, data=None, foreign=None):
        try:
            if data is None or data == []:
                return []
            if foreign is None:
                return []
            keys = foreign.keys()
            for index, item in enumerate(data):
                new_item = {}
                for key in keys:
                    new_item[foreign[key]] = item[key]
                data[index] = new_item
            return data
        except:
            return []

    def check_accounting_salary(self, data_array, salary_month):
        EN = SALARY_HACH_TOAN
        key_list = list(EN.keys())
        value_list = list(EN.values())

        errors = {"format_error": {"quantity": 0, "error_message": []},
                  "data_duplicate_error": {"quantity": 0, "error_message": []}}
        salaries = []

        if len(data_array) > MAX_ROW:
            return {"status": False, "data": "Số dòng dữ liệu đã vượt quá 500 dòng!"}
        for idx, data in enumerate(data_array):
            data_list = list(data.keys())
            data_list = set(data_list)
            data_dict = {}

            if not len(data) == len(EN):
                return {"status": False, "data": "Không đủ số cột!"}
            try:
                for item in data_list:
                    index = value_list.index(item)
                    data_dict[key_list[index]] = data.pop(item, None)
                data_dict["updateTime"] = str(datetime.now())
            except:
                return {"status": False, "data": "Lỗi định dạng tiêu đề!"}

            serializer = AccountingSalarySerializer(data=data_dict,
                                                    context={"salary_month": salary_month})
            if not serializer.is_valid():
                errors_data = serializer.errors
                error_str = ""
                count_flag = True
                for idx_key, key_field in enumerate(errors_data):
                    if errors_data[key_field]["type"] == "FORMAT":
                        if count_flag:
                            errors["format_error"]["quantity"] += 1
                            count_flag = False
                        error_str += errors_data[key_field]["err_msg"]
                        if idx_key < len(errors_data) - 1:
                            error_str += ", "
                errors["format_error"]["error_message"].append(f"Dòng {idx + 1}: {error_str.capitalize()}")
            salaries.append(data_dict)

        # kiem tra trung email va month
        email_and_month_str_list = [f"{x['email']}-{x['month']}" for x in salaries]
        email_and_month_str_duplicates = [k for k, v in collections.Counter(email_and_month_str_list).items() if v > 1]

        errors["data_duplicate_error"]["quantity"] = len(email_and_month_str_duplicates)
        for data_duplicate in email_and_month_str_duplicates:
            indexes_duplicate = [i for i, d in enumerate(email_and_month_str_list) if d == data_duplicate]
            error_str = ""
            for i, index_duplicate in enumerate(indexes_duplicate):
                error_str += f"dòng {index_duplicate + 1}"
                if i < len(indexes_duplicate) - 1:
                    error_str += ", "
            errors["data_duplicate_error"]["error_message"].append(error_str)

        if errors["format_error"]["quantity"] > 0 \
                or errors["data_duplicate_error"]["quantity"] > 0:
            return {"status": False, "data": errors}
        return {"status": True, "data": salaries}

    def update_or_save_salary(self, data, type_salary, update_by):
        salaryHachToan = AccountingSalary.objects.filter(email=data["email"], month=data["month"]).first()
        if salaryHachToan is not None:
            salaryHachToanSerializer = AccountingSalarySerializer(salaryHachToan, data=data,
                                                                  context={"email": update_by})
        else:
            salaryHachToanSerializer = AccountingSalarySerializer(data=data,
                                                                  context={"email": update_by})

        data_save = {
            "salaryDH": SalaryDhSerializer(data=data),
            "salaryINDO": SalaryIndoSerializer(data=data),
            "salaryABCD": SalaryABCDSerializer(data=data),
            "salaryTF": SalaryTFSerializer(data=data),
            "salaryTKBT": SalaryTKBTSerializer(data=data),
            "salaryThuCuoc": SalaryFeeSerializer(data=data),
            "salaryFTI": SalaryFTISerializer(data=data),
            "salaryKeyINDO": SalaryKeyIndoSerializer(data=data),
            "salaryTNOS": SalaryTnOsSerializer(data=data),
            "salarySOPNC": SalarySoSerializer(data=data),
            "salaryTestTB": SalaryTestSerializer(data=data),
            "salaryDHTIN": SalaryDhTinSerializer(data=data),
            "salaryTFTIN": SalaryTfTinSerializer(data=data),
            "salaryTKBTTIN": SalaryTkbtTinSerializer(data=data),
            "salaryINF": SalaryInfSerializer(data=data),
            "salaryHachToan": salaryHachToanSerializer
        }
        if not data_save[type_salary].is_valid():
            return False
        data_save[type_salary].save()
        return True

    def salary(self, request):
        paginator = StandardPagination()
        paginator.page_size = 10000
        data = request.data
        if len(str(data["monthStart"])) == 1:
            data["monthStart"] = "0" + str(data["monthStart"])
        else:
            data["monthStart"] = str(data["monthStart"])

        if len(str(data["monthEnd"])) == 1:
            data["monthEnd"] = "0" + str(data["monthEnd"])
        else:
            data["monthEnd"] = str(data["monthEnd"])
        data["year"] = str(data["year"])

        validate = SalaryValidate(data=data)
        if not validate.is_valid():
            return response_data(message=list(validate.errors.values())[0][0], status=5)

        validate = EmpInDepartmentValidate(data=data)
        if not validate.is_valid():
            return response_data(message=list(validate.errors.values())[0][0], status=5)

        validate = SalaryTypeValidate(data=data)
        if not validate.is_valid():
            return response_data(message=list(validate.errors.values())[0][0], status=5)

        if "code" in data and data["code"] and data["code"] != "":
            validate = EmpCodeValidate(data=data)
            if not validate.is_valid():
                return response_data(message=list(validate.errors.values())[0][0], status=5)
            code = data['code'].replace(" ", "")

            # email = self.email_from_emp_code(code=code, field="email")
            app_env = project_settings.APP_ENVIRONMENT

            email = call_api(
                host=SERVICE_CONFIG["HO-PROFILE"][app_env],
                func=SERVICE_CONFIG["HO-PROFILE"]["email-from-emp-code"]["func"],
                method=SERVICE_CONFIG["HO-PROFILE"]["email-from-emp-code"]["method"],
                data=code
            )

            try:
                email = json.dumps(email)
            except Exception as ex:
                print("{} >> {} >> Error/Loi: >> {} -> call email-from-emp-code".format(
                    datetime.now(), self.salary.__name__, ex))
                email = None

            list_email = [email]
        elif "email" in data and data["email"]:
            for email in data["email"]:
                if not helper.is_email(email):
                    return response_data(status=5, message="Email không hợp lệ!")
            list_email = data["email"]
        elif "name" in data and data["name"]:
            # list_email = self.email_list_from_emp_name(data["name"])

            app_env = project_settings.APP_ENVIRONMENT
            list_email = call_api(
                host=SERVICE_CONFIG["HO-PROFILE"][app_env],
                func=SERVICE_CONFIG["HO-PROFILE"]["email-list-from-emp-name"]["func"],
                method=SERVICE_CONFIG["HO-PROFILE"]["email-list-from-emp-name"]["method"],
                data=data["name"]
            )

            try:
                list_email = json.dumps(list_email)
            except Exception as ex:
                print("{} >> {} >> Error/Loi: >> {} -> call email-list-from-emp-name".format(
                    datetime.now(), self.salary.__name__, ex))
                list_email = []

        else:
            # list_email = self.list_info_in_block(request=request, field="email")

            app_env = project_settings.APP_ENVIRONMENT
            list_email = call_api(
                host=SERVICE_CONFIG["HO-PROFILE"][app_env],
                func=SERVICE_CONFIG["HO-PROFILE"]["emp-code-by-child-depart"]["func"],
                method=SERVICE_CONFIG["HO-PROFILE"]["emp-code-by-child-depart"]["method"],
                data=request
            )

            try:
                list_email = json.dumps(list_email)
            except Exception as ex:
                print("{} >> {} >> Error/Loi: >> {} -> call emp-code-by-child-depart".format(
                    datetime.now(), self.salary.__name__, ex))
                list_email = []

        list_month = self.timeQuerySalary(monthStart=data["monthStart"], monthEnd=data["monthEnd"], year=data["year"])

        if "show" in data and data["show"] == "EN":
            if data["salaryType"] == "hach_toan":
                queryset = AccountingSalary.objects.filter(month__in=list_month, email__in=list_email)
                result = paginator.paginate_queryset(queryset, request)
                serializer = AccountingSalarySerializer(result, many=True)
                return response_data(serializer.data)
            if data["salaryType"] == "cong_thuc":
                queryset = HistorySalaryType.objects.filter(email__in=list_email, month__in=list_month)
                serializer = HistorySalaryTypeSerializer(queryset, many=True)
                result = self.merge_foreign_en(data=serializer.data, foreign=SALARY_FOREIGN_EN)
                return response_data(result)

        if data["salaryType"] == "hach_toan":
            queryset = AccountingSalary.objects.filter(month__in=list_month, email__in=list_email)
            serializer = AccountingSalarySerializer(queryset, many=True)
            result = self.merge_foreign(data=serializer.data, foreign=SALARY_HACH_TOAN_OUTPUT)
            return response_data(result)

        return response_data(status=4, message="No data return")

    def import_salary(self, request):
        data = request.data.copy()
        salary_month = data.get("salaryMonth", None)

        if salary_month is None:
            return response_data(status=4, message="Thiếu tháng import lương!")
        elif not helper.check_data_with_re("^(1[0-2]|0[1-9])-[0-9]{4}$", salary_month):
            return response_data(status=4, message="Ngày import không hợp lệ!")

        if "array" not in data or data["array"] == []:
            return response_data(status=4, message="Không có dữ liệu import!")

        # kiem tra dinh dang va du lieu
        result = self.check_accounting_salary(data["array"], salary_month)
        if not result["status"]:
            return response_data(message=result["data"], status=4)

        # lay email user hien tai
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        email = data_token.get("email", None)

        for salary_data in result["data"]:
            if not self.update_or_save_salary(data=salary_data,
                                              type_salary="salaryHachToan",
                                              update_by=email):
                return response_data(status=4, message="Đã có lỗi trong quá trình import!")
        return response_data(message="Import lương hạch toán thành công.", status=1)