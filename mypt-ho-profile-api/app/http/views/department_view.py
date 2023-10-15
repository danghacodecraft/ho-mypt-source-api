import copy
import os

import numpy as np
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.viewsets import ViewSet

from app.http.serializers.map_department_serializer import *
from ..models.features_roles_emails import FeaturesRolesEmails
from ..models.hr import *
from ..models.user_profile import UserProfile
from ..validations.department_validate import DepartmentValidate
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers import helper, my_datetime
from ...core.helpers.global_variable import *
from ...core.helpers.response import *


class DepartmentView(ViewSet):
    def update_department(self, request):
        try:
            data = request.data
            # update PNC
            if "departments" not in data:
                return response_data(status=5, message="departments là bắt buộc!")
            if not isinstance(data["departments"], list):
                return response_data(status=5, message="departments phải là một list!")
            if not data["departments"]:
                return response_data(status=5, message="departments không được phép rỗng!")

            # update child_depart1 to chi_nhanh
            department_branch_tin = Department.objects.all() \
                .values("child_depart1", "child_depart")
            for depart in department_branch_tin:
                Department.objects.filter(child_depart=depart["child_depart"]) \
                    .update(chi_nhanh=depart["child_depart1"])

            department_list = data["departments"]
            for depart in department_list:
                child_depart = depart["child_depart"]

                department = Department.objects.filter(child_depart=child_depart).first()
                if department:
                    department.branch = depart["branch"]
                    department.chi_nhanh = depart["chi_nhanh"]
                    department.parent_depart = depart["parent_depart"]
                    department.child_depart = depart["child_depart"]
                    department.child_depart1 = depart["chi_nhanh"]
                    department.save()
                else:
                    Department.objects.create(
                        branch=depart["branch"],
                        chi_nhanh=depart["chi_nhanh"],
                        parent_depart=depart["parent_depart"],
                        child_depart=depart["child_depart"],
                        child_depart1=depart["chi_nhanh"]
                    )
            return response_data(message="Cập nhật department table thành công.")
        except Exception as ex:
            print(f"===ERROR: {ex} =====")

    # API goi noi bo lay all child depart tu parent depart
    def get_child_departs_from_parent_depart(self, request):
        data = request.data.copy()
        if "parentDepart" not in data:
            return response_data(status=5, message="parentDepart là bắt buộc")

        try:
            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")
            all_departs_with_levels_str = redis_instance.get("allDepartsWithLevels")
            if all_departs_with_levels_str:
                all_departs_with_levels = ast.literal_eval(all_departs_with_levels_str)
                all_departs = all_departs_with_levels["allDeparts"]
                all_branches = all_departs_with_levels["allBranches"]

                parent_depart_search = data["parentDepart"]
                child_departs = []
                if parent_depart_search in ["ALLPNC", "ALLTIN"]:
                    # loc theo tat ca PNC hoat tat ca TIN
                    parent_departs_name = all_departs[parent_depart_search]
                    for x in parent_departs_name.values():
                        child_departs.extend(x)
                else:
                    parent_departs_name = all_branches["PNC"] + all_branches["TIN"]
                    # kiem tra co trong PNC | TIN hay khong
                    if parent_depart_search not in parent_departs_name:
                        return response_data(status=5, message="Parent depart không tồn tại!")

                    if parent_depart_search.startswith("TIN"):
                        child_departs = all_departs["ALLTIN"][parent_depart_search]
                    else:
                        child_departs = all_departs["ALLPNC"][parent_depart_search]

                child_departs_str = ",".join(child_departs)
                return response_data(data=child_departs_str)
            return response_data(data="")
        except Exception as ex:
            print(f"{datetime.now()} >> get_child_departs_from_parent_depart >> {ex}")
            return response_data(status=4, message="Lỗi hệ thống!")

    def get_order_child_depart(self, department_list, parent_orders, child_depart_orders):
        for idx, x in enumerate(department_list):
            x["id"] = idx

        department_result_list = []
        used_id = []
        for parent_order in parent_orders:
            # sap xep theo parent_depart
            department_by_parent = [x for x in department_list if x["parent_depart"].find(parent_order) != -1]
            used_id.extend([x["id"] for x in department_by_parent])

            department_by_child_depart = []
            used_child_depart_id = []
            for child_depart_order in child_depart_orders:
                a = [x for x in department_by_parent if x["child_depart"].find(child_depart_order) != -1]
                used_child_depart_id.extend([x['id'] for x in a])
                department_by_child_depart.extend(a)
            department_by_child_depart.extend([x for x in department_by_parent if x['id'] not in used_child_depart_id])

            # Xy ly sap xep theo child depart
            department_result_list.extend(department_by_child_depart)
        department_result_list.extend([x for x in department_list if x['id'] not in used_id])

        return department_result_list

    def update_order_department(self, request):
        try:
            data = request.data
            if "typeDepartment" not in data:
                return response_data(status=5, message="typeDepartment là bắt buộc (DEPARTMENT, DEPARTMENT_FILTER)")
            type_department = data["typeDepartment"]
            if type_department not in ["DEPARTMENT", "DEPARTMENT_FILTER"]:
                return response_data(status=5,
                                     message="typeDepartment không hợp lệ => Hợp lệ là: DEPARTMENT, DEPARTMENT_FILTER")

            if type_department == "DEPARTMENT":
                department_pnc = Department.objects.exclude(child_depart__in=["ALL", "ALLTIN", "ALLPNC"]).filter(
                    branch="PNC") \
                    .values("branch", "parent_depart", "child_depart")
                department_tin = Department.objects.exclude(child_depart__in=["ALL", "ALLTIN", "ALLPNC"]).filter(
                    branch="TIN") \
                    .values("branch", "parent_depart", "child_depart")

                parent_orders = ["HO", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "INF", "CS", "PHiFPT", "FPRO",
                                 "CAM"]
                child_depart_orders = ["USR", "BIL", "INF"]
                if "parent_orders" in data and isinstance(data["parent_orders"], list) and data["parent_orders"]:
                    parent_orders = data["parent_orders"]
                if "child_depart_orders" in data and isinstance(data["child_depart_orders"], list) and data[
                    "child_depart_orders"]:
                    child_depart_orders = data["child_depart_orders"]

                department_pnc_list = list(department_pnc)
                department_tin_list = list(department_tin)

                department_pnc_result = self.get_order_child_depart(department_list=department_pnc_list,
                                                                    parent_orders=parent_orders,
                                                                    child_depart_orders=child_depart_orders)
                department_tin_result = self.get_order_child_depart(department_list=department_tin_list,
                                                                    parent_orders=parent_orders,
                                                                    child_depart_orders=child_depart_orders)

                result = department_pnc_result.copy()
                result.extend(department_tin_result)

                all_child_depart = [x['child_depart'] for x in result]
                for idx, child_depart in enumerate(all_child_depart):
                    Department.objects.filter(child_depart=child_depart).update(order=(idx + 1))

                return response_data()
            else:
                department_pnc = DepartmentFilter.objects.exclude(child_depart__in=["ALL", "ALLTIN", "ALLPNC"]).filter(
                    branch="PNC") \
                    .values("branch", "parent_depart", "child_depart")
                department_tin = DepartmentFilter.objects.exclude(child_depart__in=["ALL", "ALLTIN", "ALLPNC"]).filter(
                    branch="TIN") \
                    .values("branch", "parent_depart", "child_depart")

                parent_orders = ["HO", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "INF", "CS", "PHiFPT", "FPRO",
                                 "CAM"]
                child_depart_orders = ["USR", "BIL", "INF"]
                if "parent_orders" in data and isinstance(data["parent_orders"], list) and data["parent_orders"]:
                    parent_orders = data["parent_orders"]
                if "child_depart_orders" in data and isinstance(data["child_depart_orders"], list) and data[
                    "child_depart_orders"]:
                    child_depart_orders = data["child_depart_orders"]

                department_pnc_list = list(department_pnc)
                department_tin_list = list(department_tin)

                department_pnc_result = self.get_order_child_depart(department_list=department_pnc_list,
                                                                    parent_orders=parent_orders,
                                                                    child_depart_orders=child_depart_orders)
                department_tin_result = self.get_order_child_depart(department_list=department_tin_list,
                                                                    parent_orders=parent_orders,
                                                                    child_depart_orders=child_depart_orders)

                result = department_pnc_result.copy()
                result.extend(department_tin_result)

                all_child_depart = [x['child_depart'] for x in result]
                for idx, child_depart in enumerate(all_child_depart):
                    DepartmentFilter.objects.filter(child_depart=child_depart).update(order=(idx + 1))

                return response_data()
        except Exception as ex:
            print(f"{datetime.now} >> update_order_department >> {ex}")
            return response_data(status=4, message=f"Đã có lỗi: {ex}")

    # api import thông tin department

    def api_import_map_department(self, request):
        try:
            data_input = request.data
            # data_input = {"data": }
            data = data_input.get("data", [])
            if len(data) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)

            # import
            serializer = MapDepartmentSerializer(data=data, many=True)
            if not serializer.is_valid():
                return response_data(data=serializer.errors, status=STATUS_CODE_INVALID_INPUT,
                                     message=MESSAGE_API_FAILED)
            serializer.save()
            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

        except Exception as ex:
            print("{} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    def api_get_info_branch(self, request):
        fname = "api_get_info_branch"
        data_input = request.data
        # data_input = {
        # "parentDepart": "Vùng 1",
        # "branch": "PSG01"
        # }

        parent_depart = data_input.get("parentDepart", '')
        try:
            # queryset = MapDepartment.object.filter(parent_depart=parent_depart)
            queryset = MapDepartment.object.all()
            serializer = MapDepartmentSerializer(queryset, many=True)
            list_data = serializer.data
            print(list_data)
            return response_data(data=list_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("{} >> Error/Loi: {}".format(fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    # ===============================================

    def check_chi_nhanh(self, request):
        # xoa no di
        data_input = request.data
        chi_nhanh_new = data_input.get('data')
        try:
            queryset = MapDepartment.objects.all().values_list('branch', flat=True)
            list_data = list(queryset)
            list_output = []

            for i in chi_nhanh_new:
                if i not in list_data:
                    list_output.append(i)

            return response_data(data=list_output, status=STATUS_CODE_SUCCESS, message=MESSAGE_API_SUCCESS)

        except Exception as ex:
            print("check_chi_nhanh >> {}".format(ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    def api_update_email_manager(self, request):
        # khong duoc xoa
        data_input = request.data
        data_array = data_input.get("data")
        try:
            for i in data_array:
                child_depart = i['child_depart']
                manager = i['manager']
                Department.objects.filter(child_depart=child_depart).update(tech_manager_email=manager)
            return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("api_update_email_manager >> Error/loi: {}".format(ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)

    # api cập nhật chi_nhanh, parent_depart, child_depart, lấy thông tin từ file xlsx
    def update_or_create_department(self, request):
        try:
            result_update = []
            result_create = []
            result_fail = []
            getDataExcel = request.FILES['file_xlsx']
            getBranch = request.data.get('branch')

            dataExcel = pd.read_excel(getDataExcel, dtype={'Mã nhân viên': str})

            # fill những ô trống thành null
            dataExcel = dataExcel.replace(np.NaN, None)

            # Thay đổi tên các key cần đổi tên
            dataExcel = dataExcel.rename(columns={'Mã nhân viên': 'empCode', 'Họ và tên': 'fullName',
                                                  'Email': 'email', 'Chi nhánh': 'chiNhanh', 'Vùng': 'parentDepart',
                                                  'Bộ phận': 'childDepart', 'Bộ phận cũ': 'oldChildDepart'})
            data = dataExcel.to_dict(orient='records')

            # cho vào transaction để tránh thao tác sai dữ liệu
            with transaction.atomic():
                for obj in data:
                    obj['branch'] = getBranch
                    # dùng update_or_create()
                    validate = DepartmentValidate(data=obj)
                    if not validate.is_valid():
                        result_fail.append(obj)
                        print(validate.errors)
                        continue
                    data, created = Department.objects.update_or_create(child_depart=obj['childDepart'],
                                                                        defaults={
                                                                            'parent_depart': obj.get('parentDepart',
                                                                                                     ''),
                                                                            'chi_nhanh': obj.get('chiNhanh', ''),
                                                                            'branch': getBranch,
                                                                            'date_last_updated': get_str_datetime_now_import_db()})
                    data1, created1 = DepartmentFilter.objects.update_or_create(child_depart=obj['childDepart'],
                                                                                defaults={
                                                                                    'parent_depart': obj.get(
                                                                                        'parentDepart',
                                                                                        ''),
                                                                                    'chi_nhanh': obj.get('chiNhanh',
                                                                                                         ''),
                                                                                    'branch': getBranch,
                                                                                    'date_last_updated': get_str_datetime_now_import_db()})
                    if created:
                        result_create.append(obj)
                    else:
                        result_update.append(obj)
                count_create = len(result_create)
                count_update = len(result_update)
                count_fail = len(result_fail)
                result = {
                    'lenList': count_update + count_create,
                    'countCreate': count_create,
                    'countUpdate': count_update,
                    'countFail': count_fail,
                    'create': result_create,
                    'update': result_update,
                    'fail': result_fail
                }
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_or_create_department.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(result)

    # api update email dành cho những nhân sự đã sinh ra user_id từ email mới của nhân sự
    def update_employees_info_with_permissions_and_fea_roles(self, request):
        try:
            request_data = request.data
            result_fail = []
            result_success = []
            result_add_app_per_success = []
            result_add_app_per_fail = []
            result_add_ho_per_success = []
            result_add_ho_per_fail = []
            base_env = project_settings.APP_ENVIRONMENT

            # cho vào transaction để tránh thao tác sai dữ liệu
            with transaction.atomic():
                for data in request_data:
                    email_old = data['emailOld']

                    try:
                        # lấy thông tin nhân sự hiện tại
                        queryset = Employee.objects.filter(emp_code=data['empCode'])

                        # kiểm tra dòng user id profile
                        user_profile_new = UserProfile.objects.filter(email=data['emailNew'])
                        if not user_profile_new:
                            if queryset:
                                user_new = UserProfile.objects.create(email=data['emailNew'], user_id=data['userId'],
                                                                      full_name=data['fullName'],
                                                                      created_at=my_datetime.get_datetime_now(),
                                                                      birthday=queryset[0].birthday,
                                                                      sex=queryset[0].sex,
                                                                      mobile_phone=queryset[0].mobile_phone,
                                                                      place_of_birth=queryset[0].place_of_birth,
                                                                      nationality=queryset[0].nationality,
                                                                      marital_status=queryset[0].marital_status,
                                                                      avatar_img=queryset[0].avatar_img)
                                user_new.save()
                            else:
                                user_new = UserProfile.objects.create(email=data['emailNew'], user_id=data['userId'],
                                                                      full_name=data['fullName'],
                                                                      created_at=my_datetime.get_datetime_now(), )
                                user_new.save()

                        # cập nhật thông tin mới cho nhân sự
                        Employee.objects.filter(emp_code=data['empCode']).update(email=data['emailNew'])

                        fea_roles_dict = {fr.feature_code: fr.role_code for fr in
                                          FeaturesRolesEmails.objects.filter(email=email_old)}

                        data_input_api_ho = {
                            'emailsWithChildDepart': [{
                                'email': data['emailNew'],
                                'childDepart': data['childDepart']
                            }],
                            'emailLimit': 1,
                            'permissions': data['hoPerOld'],
                            'feaRoles': fea_roles_dict
                        }

                        data_input_api_app = {
                            'email': data['emailNew'],
                            'permissions': list(map(lambda code: {
                                'permissionsCode': code,
                                'childDeparts': data['childDepart']
                            }, data['appPerOld']))
                        }
                        if data['hoPerOld']:
                            response_ho = helper.call_api(
                                host=SERVICE_CONFIG['HO-AUTH'][base_env],
                                func=SERVICE_CONFIG['HO-AUTH']['add_ho_pers_and_fea_roles_for_emails']['func'],
                                method=SERVICE_CONFIG['HO-AUTH']['add_ho_pers_and_fea_roles_for_emails']['method'],
                                data=data_input_api_ho
                            )
                            if json.loads(response_ho)['statusCode'] == 1:
                                result_add_ho_per_success.append(data)
                            else:
                                result_add_ho_per_fail.append(data)

                        if data['appPerOld']:
                            response_app = helper.call_api(
                                host=SERVICE_CONFIG['HO-AUTH'][base_env],
                                func=SERVICE_CONFIG['HO-AUTH']['add_user_permissions_by_email_mypt']['func'],
                                method=SERVICE_CONFIG['HO-AUTH']['add_user_permissions_by_email_mypt']['method'],
                                data=data_input_api_app
                            )
                            if json.loads(response_app)['statusCode'] == 1:
                                result_add_app_per_success.append(data)
                            else:
                                result_add_app_per_fail.append(data)

                        result_success.append(data)
                    except ObjectDoesNotExist:
                        result_fail.append(data)
                        continue
                result = {
                    'fail': result_fail,
                    'succes': result_success,
                    'add_app_success': result_add_app_per_success,
                    'add_app_fail': result_add_app_per_fail,
                    'add_ho_success': result_add_ho_per_success,
                    'add_ho_fail': result_add_ho_per_fail
                }
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(),
                                                        self.update_employee_info_with_permissions_and_fea_roles.__name__, ex))
            return response_data(None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return response_data(result)

    def get_parent_depart_from_branch(self, request):
        try:
            data = request.data
            if 'branch' not in data:
                return response_data(data={'list_data': []})

            branch = data['branch']
            list_data = Department.objects.filter(branch=branch).values_list('parent_depart', flat=True).distinct()
            return response_data(data={'list_data': list_data})

        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_parent_depart_from_branch.__name__, ex))
            return response_data(data={'list_data': []})
