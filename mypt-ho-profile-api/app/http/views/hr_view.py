from app.http.models.info_modify_history import InformationModifyHistory
from ...core.helpers.response import *
from ...core.helpers.global_variable import *
from ...core.helpers.helper import *
from ..models.hr import *
from ..models.contract import ContractType, Contract
from ..serializers.hr_serializer import *
from ..paginations.custom_pagination import *
import redis
import ast
from rest_framework.viewsets import ViewSet
from ...configs.excel_table import *
from datetime import datetime
from ..threading.handle_permission import *
from ...core.helpers import auth_session_handler as authSessionHandler


class HrView(ViewSet):
    pagination_class = CustomPagination()

    def get_contract_type_from_redis(self):
        redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                           port=project_settings.REDIS_PORT_CENTRALIZED,
                                           db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                           decode_responses=True,
                                           charset="utf-8")
        contracts_type_str = redis_instance.get("contractsType")
        if contracts_type_str is None:
            contracts_type = None
        else:
            contracts_type = ast.literal_eval(contracts_type_str)

        if contracts_type is None:
            # luu contracts type vao redis
            contracts_type = list(ContractType.objects.values_list('contract_type', flat=True))
            redis_instance.set("contractsType", str(contracts_type))

        return contracts_type

    def get_contracts_type(self, request):
        return response_data(data=self.get_contract_type_from_redis())

    def delete_contracts_type_from_redis(self, request):
        redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                           port=project_settings.REDIS_PORT_CENTRALIZED,
                                           db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                           decode_responses=True,
                                           charset="utf-8")
        contracts_type_str = redis_instance.get("contractsType")
        try:
            if contracts_type_str is not None:
                redis_instance.delete("contractsType")
        except Exception as ex:
            print(f"delete_contracts_type_from_redis function -> Error: {ex}")
            return response_data(status=4, message="Đã có lỗi!")
        else:
            return response_data()

    def add_employee(self, request):
        return response_data()

    def edit_employee(self, request):
        data = request.data
        try:
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            validate = EmpCodeValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=list(validate.errors.values())[0][0])

            if not Employee.objects.filter(email=data["email"]).exists():
                return response_data(status=5, message="Email chưa tồn tại. Không thể sửa")

            if "code" in data \
                    and Employee.objects.exclude(email=data["email"]).filter(emp_code=data["code"]).exists():
                return response_data(status=5, message="Trùng mã nhân viên, không cho phép sửa!")

            list_data_key = data.keys()
            data_save = {}
            for item in list_data_key:
                if item in ['contractBegin', 'contractEnd', 'dateJoinCompany', 'birthday']:
                    if not is_null_or_empty(data[item]):
                        data_save[item] = data[item]
                    else:
                        data_save[item] = None
                elif item in ['dateQuitJob']:
                    if not is_null_or_empty(data[item]):
                        # cap nhat status working = 0
                        data_save[item] = data[item]
                        data_save["statusWorking"] = 0
                    else:
                        # cap nhat status working = 1
                        data_save[item] = None
                        data_save["statusWorking"] = 1
                else:
                    if data[item] != "" and item != "dateQuitJob":
                        data_save[item] = data[item]
            data_save["updateBy"] = user_token.get("email", "")

            queryset = Employee.objects.filter(emp_code=data["code"]).first()
            # serializer = EmployeeSerializer(queryset, data=data_save,
            #                                 contracts_type=self.get_contract_type_from_redis())
            serializer = EmployeeSerializer(queryset, data=data_save)
            if not serializer.is_valid():
                return response_data(status=5, message=list(serializer.errors.values())[0][0])
            if not serializer.save():
                return response_data(status=5, message="Không sửa được")
            return response_data(message="Sửa thành công")
        except Exception as ex:
            print(f'{datetime.now()} >> "edit_employee" >> {ex}')
            return response_data(status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED, data="")

    def list_name_from_code(self, request):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])
        data = self.emp_by_child_depart(data=data, fields=["email", "name", "code", "childDepart", "fullChildDepart"])
        # .filter(code__in=['00170734'])
        return response_data(data=data)

    def list_code_from_name(self, request):
        try:
            data = request.data
            if "name" in data and data["name"]:
                code_list = Employee.objects.filter(emp_name__icontains=data["name"]).values_list("emp_code", flat=True)
                return response_data(data=code_list)
        except Exception as ex:
            print(f"{datetime.now()} >> list_code_from_name >> {ex}")
            return response_data(status=4, data=[])
        return response_data(status=4, data=[])

    def name_from_code(self, request):
        data = request.data
        if "code" not in data:
            return response_data(status=5, message="Code is valid")
        try:
            queryset = Employee.objects.filter(emp_code=data['code'])
            serializer = EmployeeSerializer(queryset, many=True, fields=['name'])
            return response_data(data=serializer.data[0]['name'])
        except:
            return response_data(data="arr")

    def info_from_email(self, request):
        data = request.data.copy()
        fields = data.get('fields', None)
        if "email" in data and not empty(data["email"]):
            validate = EmpFieldsListValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=list(validate.errors.values())[0][0])
            queryset = Employee.objects.filter(email__in=data['email'])
        if "code" in data and not empty(data["code"]):
            validate = CodeFieldsListValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=list(validate.errors.values())[0][0])
            queryset = Employee.objects.filter(emp_code__in=data['code'])
        try:
            serializer = EmployeeSerializer(queryset, many=True, fields=fields)
            return response_data(data=serializer.data)
        except:
            return response_data(status=5, message="Error")

    def info_from_code_list(self, request):
        data = request.data
        fields = data.get("fields", None)

        try:
            queryset = Employee.objects.filter(emp_code__in=data["codeList"])
            if fields is not None:
                serializer = EmployeeSerializer(queryset, many=True, fields=fields)
            else:
                serializer = EmployeeSerializer(queryset, many=True)

            return response_data(data=serializer.data)
        except Exception as ex:
            print(f"{datetime.now()} >> info_from_code_list >> {ex}")
            return response_data(status=5, message="Error")

    def get_emp_info(self, request):
        email = "ainv@vienthongtin.com"
        queryset = Employee.objects.filter(email=email)
        serializer = EmployeeSerializer(queryset, many=True)
        if serializer.data:
            return response_data(data=serializer.data[0])
        return response_data(data=serializer.data)

    def get_block_info(self, request):
        queryset = Department.objects.distinct().values('branch').filter(branch__isnull=False)
        serializer = DepartmentSerializer(queryset, many=True, fields=['branch'])
        value = {}
        queryset = Department.objects.distinct().values()
        for item in serializer.data:
            key = item.pop('branch')
            queryset = Department.objects.distinct().values('parent_depart').filter(branch=key)
            serializer = DepartmentSerializer(queryset, many=True, fields=['parentDepart'])
            value[key] = {}
            for item1 in serializer.data:
                key1 = item1.pop('parentDepart')
                queryset = Department.objects.distinct().values('child_depart').filter(parent_depart=key1)
                serializer = DepartmentSerializer(queryset, many=True, fields=['childDepart'])
                value1 = []
                for item2 in serializer.data:
                    key2 = item2.pop('childDepart')
                    value1.append(key2)
                value[key][key1] = value1
        return response_data(data=value)

    def get_all_in_block(self, request):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])
        data = self.emp_by_child_depart(data=data)
        return response_data(data=data)

    def get_in_block(self, request):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])
        data = self.emp_by_child_depart(data=data, fields=["email", "name", "code"])
        arr_email = []
        arr_name = []
        arr_code = []
        for item in data:
            arr_email.append(item['email'])
            arr_name.append(item['name'])
            arr_code.append(item['code'])
        result = {
            "listEmail": arr_email,
            "listName": arr_name,
            "listCode": arr_code
        }
        return response_data(data=result)

    def emp_by_child_depart(self, data, fields=None, status_working=1):
        # try:
        department_list = InformationModifyHistory.objects.filter(new_value__in=data['childDepart']).values_list('old_value', flat=True)
        data['childDepart'] += list(set(department_list))
        if status_working:
            queryset = Employee.objects.filter(child_depart__in=data['childDepart'], status_working=status_working)
        else:
            queryset = Employee.objects.filter(child_depart__in=data['childDepart'])
        serializer = EmployeeSerializer(queryset, many=True)
        if fields is not None:
            serializer = EmployeeSerializer(queryset, many=True, fields=fields)
        return serializer.data
        # except:

    def emp_code_by_child_depart(self, data, fields='code', status_working=1):
        # try:
        if status_working:
            queryset = Employee.objects.filter(child_depart__in=data['childDepart'], status_working=status_working)
        else:
            queryset = Employee.objects.filter(child_depart__in=data['childDepart'])
        serializer = EmployeeSerializer(queryset, many=True)
        if fields is not None:
            serializer = EmployeeSerializer(queryset, many=True, fields=fields)
        return serializer.data
        # except:

    def emp_contract(self, list_code, contract):
        queryset = Employee.objects.filter(emp_code__in=list_code, contract_type__in=contract)
        serializer = EmployeeSerializer(queryset, many=True, fields=["code"])
        data = serializer.data
        arr = []
        for item in data:
            arr.append(item['code'])
        while None in arr:
            arr.remove(None)
        return arr

    def emp_status_work(self, list_code, statusWork):
        queryset = Employee.objects.filter(emp_code__in=list_code, status_working__in=statusWork)
        serializer = EmployeeSerializer(queryset, many=True, fields=["code"])
        data = serializer.data
        arr = []
        for item in data:
            arr.append(item['code'])
        while None in arr:
            arr.remove(None)
        return arr

    def list_code_in_block(self, request):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return None
        if "statusWorking" in data and data["statusWorking"] is None:
            data = self.emp_by_child_depart(data=data, fields=["code"], status_working=data["statusWorking"])
        else:
            data = self.emp_by_child_depart(data=data, fields=["code"])
        arr = []
        for item in data:
            arr.append(item['code'])
        while None in arr:
            arr.remove(None)
        return arr

    def post_emp_info(self, request):
        data = request.data
        show = data.pop("show", None)
        key_list = list(EMPLOYEE.keys())

        child_departs_right = utils.get_child_depart_with_permission(request.headers.get("Authorization"), "QUAN_LY_NHAN_VIEN_SHOW")
        if child_departs_right is None:
            return response_data(status=4, message="Lỗi hệ thống!")

        paginator = self.pagination_class
        if "code" in data or "email" in data or "name" in data:
            count = 0
            queryset = Employee.objects.filter(child_depart__in=child_departs_right)
            emp_queryset = {}
            if "code" in data and data["code"]:
                # loc theo ma nhan vien
                validate = EmpCodeValidate(data=data)
                if not validate.is_valid():
                    return response_data(status=5, message=list(validate.errors.values())[0][0])

                queryset = queryset.filter(emp_code=data["code"]).all()
                count = len(queryset)
                emp_queryset = paginator.paginate_queryset(queryset, request)
            elif "email" in data and data["email"]:
                if not helper.is_email(data['email']):
                    return response_data(status=5, message="Email không hợp lệ!")
                # loc theo email nhan vien
                queryset = queryset.filter(email=data["email"]).all()
                count = len(queryset)
                emp_queryset = paginator.paginate_queryset(queryset, request)
            elif "name" in data and data["name"]:
                # loc theo ten nhan vien
                queryset = queryset.filter(emp_name__icontains=data["name"])
                count = len(queryset)
                emp_queryset = paginator.paginate_queryset(queryset, request)

            if show is not None and show == "EN":
                serializer = EmployeeSerializer(emp_queryset, many=True, fields=key_list)
                data_response = paginator.get_paginated_response(serializer.data)
                return response_data(data={
                    "numberRow": count,
                    "data": data_response.data,
                    "dictCol": EMPLOYEE
                })
            serializer = EmployeeSerializer(queryset, many=True, VN=EMPLOYEE_EXPORT)
            return response_data(data={
                "numberRow": count,
                "data": serializer.data,
                "dictCol": EMPLOYEE_EXPORT
            })

        validate = EmpInDepartmentValidate(data=data)
        if not validate.is_valid():
            return response_data(message=list(validate.errors.values())[0][0], status=5)
        request.data["statusWorking"] = None
        list_code = self.list_code_in_block(request)
        queryset = Employee.objects.filter(emp_code__in=list_code)
        if "statusWork" in data and data["statusWork"] != [] and isinstance(data["statusWork"], list):
            queryset = queryset.filter(status_working__in=data["statusWork"])

        count = len(queryset)
        emp_queryset = paginator.paginate_queryset(queryset, request)
        if show is not None and show == "EN":
            serializer = EmployeeSerializer(emp_queryset, many=True, fields=key_list)
            data_response = paginator.get_paginated_response(serializer.data)

            return response_data({
                "numberRow": count,
                "data": data_response.data,
                "dictCol": EMPLOYEE
            })
        serializer = EmployeeSerializer(queryset, many=True, VN=EMPLOYEE_EXPORT)
        return response_data({
            "numberRow": count,
            "data": serializer.data,
            "dictCol": EMPLOYEE_EXPORT
        })

    def import_employee(self, request):
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        user_email = data_token.get("email", "")
        data = request.data
        if "array" not in data or data["array"] == []:
            return response_data(status=4, message="Không có dữ liệu import")

        if len(data["array"]) > MAX_ROW:
            return response_data(status=5, message=f"Chỉ được phép import tối đa {MAX_ROW} dòng!")
        fails = ""
        for idx, item in enumerate(data['array']):
            try:
                data_dict = self.import_vi_to_en_emp(EN=EMPLOYEE_IMPORT,
                                                     data=item,
                                                     user_email=user_email)
            except Exception as ex:
                return response_data(status=4, message="Có lỗi trong quá trình import dữ liệu!", data=str(ex))
            if not data_dict['status'] and data_dict['messages'] != "BUG":
                return response_data(message=data_dict['messages'], status=5)
            if not data_dict['status'] and data_dict['messages'] == "BUG":
                fails += "Dòng có lỗi là dòng: " + str(idx + 1) + str(data_dict['error']) + "<br>"
        if fails == "":
            return response_data(message="Import thành công", status=1)
        return response_data(message=fails, status=5)

    def import_vi_to_en_emp(self, **kwargs):
        # contracts_type = kwargs.pop('contracts_type', None)
        user_email = kwargs.pop('user_email')
        EN = kwargs.pop('EN', None)
        data = kwargs.pop('data', None)
        data_list = list(data.keys())
        if EN is not None and data is not None:
            key_list = list(EN.keys())
            value_list = list(EN.values())
            data_list = set(value_list) & set(data_list)
            data_dict = {}
            try:
                for item in data_list:
                    index = value_list.index(item)
                    data_dict[key_list[index]] = data.pop(item, None)
                data_dict["updateTime"] = datetime.now()
                data_dict["updateBy"] = user_email
            except:
                return {"status": False, "messages": "Lỗi định dạng"}

            errors = []
            if "code" not in data_dict:
                errors.append('Mã nhân viên là bắt buộc')
                return {"status": False, "messages": "BUG", "error": errors}
            if "email" not in data_dict:
                errors.append("Email nhân viên là bắt buộc")
                return {"status": False, "messages": "BUG", "error": errors}
            
            if Employee.objects.filter(emp_code=data_dict["code"], email=data_dict["email"]).exists():
                # cho update
                queryset = Employee.objects.get(emp_code=data_dict["code"])
                # serializer = EmployeeSerializer(queryset, data=data_dict,
                #                                 contracts_type=contracts_type)
                serializer = EmployeeSerializer(queryset, data=data_dict)
            elif Employee.objects.filter(emp_code=data_dict["code"]).exclude(email=data_dict["email"]).exists():
                # bao loi va khong cho update => khong cho sua email
                errors.append("Không được chỉnh sửa email")
                return {"status": False, "messages": "BUG", "error": errors}
            elif Employee.objects.exclude(emp_code=data_dict["code"]).filter(email=data_dict["email"]).exists():
                # bao loi va khong cho update => khogn cho sua emp_code
                errors.append("Không được chỉnh sửa mã nhân viên")
                return {"status": False, "messages": "BUG", "error": errors}
            else:
                # tao moi nhan vien
                # serializer = EmployeeSerializer(data=data_dict,
                #                                  contracts_type=contracts_type)
                serializer = EmployeeSerializer(data=data_dict)
            if not serializer.is_valid():
                # get error what field is not valid
                errors = []
                for error in serializer:
                    if error.errors:
                        if error.name in ["maritalStatus", "workplace", "childDepart", "contractType"]:
                            errors.append(error.errors[0].__str__())
                        else:
                            errors.append(error.name + " " + error.value)
                return {"status": False, "messages": "BUG", "error": errors}

            if not serializer.save():
                return {"status": False, "messages": "Import không thành công"}
            HandlePermission(data=serializer.data).start()
            return {"status": True, "data": data_list}
        return {"status": False, "messages": "Dữ liệu import rỗng"}

    def email_from_emp_code(self, code, field="email"):
        try:
            employee_data = Employee.objects.filter(emp_code=code).first()
            if employee_data is None:
                return None
            employee_serializer = EmployeeSerializer(employee_data, fields=[field])
            return employee_serializer.data[field]
        except Exception as ex:
            print(f"===== ERROR: {ex} ======")
            return None

    def email_list_from_emp_name(self, name):
        try:
            emp_email_list = Employee.objects.filter(emp_name__icontains=name).values_list("email", flat=True)
            return emp_email_list
        except Exception as ex:
            print(f"===== ERROR: {ex} ======")
            return []

    def list_info_in_block(self, request, field="code"):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return None
        data = self.emp_by_child_depart(data=data, fields=[field])
        arr = []
        # print (data)
        # return arr
        for item in data:
            arr.append(item[field])
        while None in arr:
            arr.remove(None)
        return arr

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

    def check_emp_rank(self, request):
        userSessionData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        userSessionData["thuHangNhanVien"] = "Hang 15 tren 369"
        return response_data({"loginUserData": userSessionData})

    # api noi bo - cap nhat status working cho nhan vien khi da co ngay nghi viec
    def update_status_working_employee(self, request):
        try:
            Employee.objects.exclude(date_quit_job__isnull=True).update(
                status_working=0)
            Employee.objects.filter(date_quit_job__isnull=True).update(status_working=1)
        except Exception as ex:
            print(f"====ERROR: {ex} ====")
            return response_data(data="Cập nhật status working không thành công.")
        return response_data(data="Cập nhật status working thành công.")

    def get_emp_code_and_name_from_email(self, request):
        try:
            data = request.data
            if 'email' not in data:
                return response_data(data=[])
            email = data['email']
            emp = Employee.objects.filter(email=email).values('emp_code', 'emp_name')
            return response_data(data=emp)
        except Exception as ex:
            print(f"====ERROR: {ex} ====> Lấy tên và mã nv từ email thất bại")
            return response_data(data=[])
