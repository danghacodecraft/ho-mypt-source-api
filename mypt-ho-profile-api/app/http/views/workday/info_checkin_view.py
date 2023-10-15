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

class InfoCheckinView(ViewSet):
    def get_list_emp_from_child_depart(self, request):
        # service goi noi bo: api import thong tin khai bao diem danh
        # api tra ve danh sach emp code voi input la danh sach phong ban
        data_input = request.data
        list_child_depart = data_input.get("childDepart", [])
        status_working = data_input.get("statusWorking")
        try:
            if len(list_child_depart) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_INVALID_INPUT)

            queryset = Employee.objects.filter(child_depart__in=tuple(list_child_depart))
            if not is_null_or_empty(status_working):
                queryset = queryset.filter(status_working=status_working)
            queryset = queryset.values_list('emp_code', flat=True)
            if len(queryset) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            list_data = list(queryset)


            return response_data(data=list_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> get_list_emp_from_child_depart >> Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def get_emp_code_from_list_child_depart_and_email(self, request):
        data_input = request.data
        try:
            list_child_depart = data_input.get("childDepart", [])
            email = data_input.get("email", "")
            queryset = Employee.objects.filter(email=email, child_depart__in= tuple(list_child_depart)).values_list('emp_code', flat=True)
            if len(queryset) == 0:
                return response_data(data={},message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            list_data = list(queryset)
            return response_data(data=list_data[0], message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("{} >> {}  : Error/Loi: {} ".format(get_str_datetime_now_import_db(), "get_emp_code_from_list_child_depart_and_email", ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def get_emp_code_from_list_child_depart_and_name(self, request):
        data_input = request.data
        try:
            list_child_depart = data_input.get("childDepart", [])
            name = data_input.get("name", "")
            queryset = Employee.objects.filter(emp_name__icontains=name, child_depart__in=tuple(list_child_depart)).values_list(
                'emp_code', flat=True)
            if len(queryset) == 0:
                return response_data(data={},message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            list_data = list(queryset)
            return response_data(data=list_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> {}  : Error/Loi: {} ".format(get_str_datetime_now_import_db(),
                                                      "get_emp_code_from_list_child_depart_and_name", ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)




