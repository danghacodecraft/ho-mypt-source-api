from app.http.models.info_modify_history import InformationModifyHistory
from ...configs.excel_table import *
from ...core.helpers.response import *
from ..serializers.hr_serializer import *
from ..paginations.custom_pagination import *
from rest_framework.viewsets import ViewSet
from datetime import datetime, timedelta
from app.core.helpers.call_api import *
from app.core.helpers.helper import convert_vi_to_en
from ...core.helpers import auth_session_handler as authSessionHandler


class PtqView(ViewSet):
    def email_is_ptq(self, request):
        cheTaiFeaRole = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))[
            "featuresRoles"].get("CHE_TAI_HO", None)
        if cheTaiFeaRole is None:
            return response_data(False)

        if cheTaiFeaRole == "NHAN_VIEN_KIEM_SOAT":
            # print("User nay la Nhan Vien Kiem Soat trong feature CHE_TAI_HO")
            return response_data(True)

        # print("User nay KHONG PHAI la Nhan Vien Kiem Soat trong feature CHE_TAI_HO")
        return response_data(False)

    def get_all_employee_email_list(self, request):
        # bên ho-company gọi
        try:
            data = Employee.objects.filter(status_working=1).values_list('email', flat=True)
            return response_data(data=data)

        except Exception as ex:
            print(f"{datetime.now()} >> get_all_employee_email_list >> {ex}")
            return []

    def get_code_in_block(self, request):
        data = request.data
        fields = data["fields"]
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=serializer.errors)
        data = self.emp_by_child_depart(data=data, fields=[fields], status=True)
        arr = []
        for item in data:
            arr.append(item[fields])
        while None in arr:
            arr.remove(None)
        return response_data(data=arr)

    def emp_by_child_depart(self, data, fields=None, status=False):
        department_list = InformationModifyHistory.objects.filter(new_value__in=data['childDepart']).values_list('old_value', flat=True)
        data['childDepart'] += list(set(department_list))
        try:
            queryset = Employee.objects.filter(child_depart__in=data['childDepart'])
            if status:
                queryset = queryset.filter(status_working=1)
            if "name" in data and data["name"] != []:
                queryset = queryset.filter(emp_name__in=data['name'])
            if fields is not None:
                serializer = EmployeeSerializer(queryset, many=True, fields=fields)
            else:
                serializer = EmployeeSerializer(queryset, many=True)
            return serializer.data
        except:
            return []

    def lst_code_emp_by_parent_depart(self, request):
        data = request.data
        child_depart = Department.objects.filter(
            parent_depart__in=data['parentDepart']).values_list('child_depart')
        query_set = Employee.objects.filter(child_depart__in=child_depart)

        serializer = EmployeeSerializer(query_set, many=True)
        if not serializer:
            return response_data(status=6, message=serializer.errors)

        data_response = [item['code'] for item in serializer.data]

        return data_response


    def list_code_in_block(self, request):
        data = request.data
        serializer = EmpInDepartmentValidate(data=data)
        if not serializer.is_valid():
            return None
        data = self.emp_by_child_depart(data=data, fields=["code"])
        arr = []
        for item in data:
            arr.append(item['code'])
        while None in arr:
            arr.remove(None)
        return arr

    def get_emp_rank(self, request):
        data = request.data
        validate = DateSearchValidate(data=data)
        if not validate.is_valid():
            return response_data(message=validate.errors, status=5)
        queryset = EmployeeRank.objects.filter(thang=data['month'], nam=data["year"])

        if ("code" in data and data["code"]) or ("emp_name" in data and data["emp_name"]) \
                or ("email" in data and data["email"]):
            if "code" in data and data["code"]:
                validate = EmpCodeValidate(data=data)
                if not validate.is_valid():
                    return response_data(message=[f'{validate.errors[err][0]}' for err in validate.errors][0], status=5)
                code = data['code'].strip()
                queryset = queryset.filter(emp_code=code)
            elif "email" in data and data["email"]:
                email = data['email'].strip()
                queryset = queryset.filter(email__iexact=email)
            elif "emp_name" in data and data["emp_name"]:
                queryset = queryset.filter(emp_name__icontains=data['emp_name'])

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            permissions = data_token['permissions']

            if 'ALL' not in permissions:
                xhnv_show = permissions['XEP_HANG_NHAN_VIEN_SHOW']
                branch_rights = xhnv_show['branch_rights']
                child_depart_rights = xhnv_show['child_depart_rights']
                tin = branch_rights['TIN']
                pnc = branch_rights['PNC']
                list_child_depart = []
                if 'ALL' not in tin and 'ALL' not in pnc:
                    all_keys = child_depart_rights.keys()
                    for key_item in all_keys:
                        list_child_depart.extend(child_depart_rights[key_item])
                else:
                    if 'ALL' in tin:
                        list_child_depart.extend(
                            Department.objects.filter(branch='TIN').values_list('child_depart', flat=True))
                    else:
                        tin_keys = child_depart_rights.keys()
                        for key_item in tin_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                    if 'ALL' in pnc:
                        list_child_depart.extend(
                            Department.objects.filter(branch='PNC').values_list('child_depart', flat=True))
                    else:
                        pnc_keys = child_depart_rights.keys()
                        for key_item in pnc_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                list_emp_code = Employee.objects.filter(child_depart__in=list_child_depart).values_list('emp_code',
                                                                                                        flat=True)
                queryset = queryset.filter(emp_code__in=list_emp_code)

            first_emp_rank = queryset.first()

            # serializer = EmployeeRankSerializerEN(queryset, many=True)

            paginator = EmployeeRankPagination()

            params = request.query_params

            if 'page_size' in params:
                paginator.page_size = params['page_size']

            result_page = paginator.paginate_queryset(queryset, request)

            serializer = EmployeeRankSerializerEN(result_page, many=True)

            dict_keys = {}
            if first_emp_rank:
                dict_keys = {
                    'id': 'Id',
                    'emp_code': 'Mã NV',
                    'emp_name': 'Họ và tên',
                    'email': 'Email',
                    'month': 'Tháng',
                    'year': 'Năm',
                    'job_level': 'Bậc',
                }
                emp_rank_info = ast.literal_eval(first_emp_rank.emp_rank_info)
                for k, v in emp_rank_info.items():
                    en_key = convert_vi_to_en(k).replace(" ", "_").lower()
                    dict_keys.update({en_key: k})

            data_response = paginator.get_paginated_response(data=serializer.data)
            data_response.update({
                'dict_keys': dict_keys,
            })

            return response_data(data=data_response)

        if 'childDepart' not in data or data['childDepart'] == []:
            validate = EmpInParentDepartmentValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            list_code = self.lst_code_emp_by_parent_depart(request)
            queryset = queryset.filter(emp_code__in=list_code)
        else:
            validate = EmpInDepartmentValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            list_code = self.list_code_in_block(request)
            queryset = queryset.filter(emp_code__in=list_code)

        first_emp_rank = queryset.first()

        paginator = EmployeeRankPagination()

        params = request.query_params

        if 'page_size' in params:
            paginator.page_size = params['page_size']

        result_page = paginator.paginate_queryset(queryset, request)

        serializer = EmployeeRankSerializerEN(result_page, many=True)

        dict_keys = {}
        if first_emp_rank:
            dict_keys = {
                'id': 'Id',
                'emp_code': 'Mã NV',
                'emp_name': 'Họ và tên',
                'email': 'Email',
                'month': 'Tháng',
                'year': 'Năm',
                'job_level': 'Bậc',
            }
            emp_rank_info = ast.literal_eval(first_emp_rank.emp_rank_info)
            for k, v in emp_rank_info.items():
                en_key = convert_vi_to_en(k).replace(" ", "_").lower()
                dict_keys.update({en_key: k})

        data_response = paginator.get_paginated_response(data=serializer.data)
        data_response.update({
            'dict_keys': dict_keys,
        })
        return response_data(status=1, data=data_response)

    def export_emp_rank(self, request):
        data = request.data
        validate = DateSearchValidate(data=data)
        if not validate.is_valid():
            return response_data(message=[f'{err}: {validate.errors[err][0]}' for err in validate.errors], status=5)
        queryset = EmployeeRank.objects.filter(thang=data['month'], nam=data["year"])

        if ("code" in data and data["code"]) or ("emp_name" in data and data["emp_name"]) \
                or ("email" in data and data["email"]):
            if "code" in data and data["code"]:
                validate = EmpCodeValidate(data=data)
                if not validate.is_valid():
                    return response_data(message=[f'{validate.errors[err][0]}' for err in validate.errors][0], status=5)
                code = data['code'].strip()
                queryset = queryset.filter(emp_code=code)
            elif "email" in data and data["email"]:
                queryset = queryset.filter(email__iexact=data['email'])
            elif "emp_name" in data and data["emp_name"]:
                queryset = queryset.filter(emp_name__icontains=data['emp_name'])

            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            permissions = data_token['permissions']

            if 'ALL' not in permissions:
                xhnv_show = permissions['XEP_HANG_NHAN_VIEN_SHOW']
                branch_rights = xhnv_show['branch_rights']
                child_depart_rights = xhnv_show['child_depart_rights']
                tin = branch_rights['TIN']
                pnc = branch_rights['PNC']
                list_child_depart = []
                if 'ALL' not in tin and 'ALL' not in pnc:
                    all_keys = child_depart_rights.keys()
                    for key_item in all_keys:
                        list_child_depart.extend(child_depart_rights[key_item])
                else:
                    if 'ALL' in tin:
                        list_child_depart.extend(
                            Department.objects.filter(branch='TIN').values_list('child_depart', flat=True))
                    else:
                        tin_keys = child_depart_rights.keys()
                        for key_item in tin_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                    if 'ALL' in pnc:
                        list_child_depart.extend(
                            Department.objects.filter(branch='PNC').values_list('child_depart', flat=True))
                    else:
                        pnc_keys = child_depart_rights.keys()
                        for key_item in pnc_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                list_emp_code = Employee.objects.filter(
                    child_depart__in=list_child_depart).values_list('emp_code', flat=True)
                queryset = queryset.filter(emp_code__in=list_emp_code)

            serializer = EmployeeRankSerializer(queryset, many=True)

            return response_data(data={'list_data': serializer.data})

        if 'childDepart' not in data or data['childDepart'] == []:
            validate = EmpInParentDepartmentValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            list_code = self.lst_code_emp_by_parent_depart(request)
            queryset = queryset.filter(emp_code__in=list_code)
        else:
            validate = EmpInDepartmentValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            list_code = self.list_code_in_block(request)
            queryset = queryset.filter(emp_code__in=list_code)

        serializer = EmployeeRankSerializer(queryset, many=True)

        return response_data({"list_data": serializer.data})

    def check_import_rank(self, request):
        data = request.data
        if "array" not in data:
            return response_data(status=4, data={'save_flag': False}, message="Không có dữ liệu import")
        errors = []
        save_flag = True

        list_field = []
        if 'listField' in data:
            list_field = data['listField']

        list_distinct_rank = []

        for idx, item in enumerate(data['array']):
            if idx == 0:
                if 'Tháng' in item and 'Năm' in item:
                    emp_code = item['Mã NV']
                    thang = item['Tháng']
                    nam = item['Năm']
                    if EmployeeRank.objects.filter(emp_code=emp_code, thang=thang, nam=nam).exists():
                        emp_fst = EmployeeRank.objects.get(emp_code=emp_code, thang=thang, nam=nam)
                        info_fst = ast.literal_eval(emp_fst.emp_rank_info)
                        info_fst_lst_key = list(info_fst.keys())
                        info_fst_lst_key.extend(['Mã NV', 'Họ và tên', 'Email', 'Tháng', 'Năm', 'Bậc'])
                        list_field.sort()

                        info_fst_lst_key.sort()
                        if list_field != info_fst_lst_key:
                            return response_data(status=0, message=[f'Các trường thông tin về dữ liệu chưa trùng khớp với dữ liệu tháng {thang}/{nam} đã được tải lên trước đó. Bạn vui lòng kiểm tra và thử lại'], data={'save_flag': False})
            item_keys = list(item.keys())

            if 'Mã NV' not in item_keys or 'Tháng' not in item_keys or 'Năm' not in item_keys\
                    or 'Email' not in item_keys or 'Họ và tên' not in item_keys or 'Bậc' not in item_keys:
                errors.append(f"Dòng ({idx+2}) vui lòng điền đủ thông tin")
                save_flag = False
                continue
            if not Employee.objects.filter(emp_code=item['Mã NV'], status_working=1).exists():
                errors.append(f"Dòng ({idx+2}) nhân viên đã nghỉ việc")
                save_flag = False
                continue
            if EmployeeRank.objects.filter(
                emp_code=item['Mã NV'], thang=item['Tháng'], nam=item['Năm']
            ).exists():
                errors.append(f'Dòng ({idx + 2}): đã có kết quả đánh giá cho nhân viên này trên hệ thống')
            if 'Mã NV' in item_keys and 'Tháng' in item_keys and 'Năm' in item_keys:
                dict_d = {'emp_code': item['Mã NV'], 'thang': item['Tháng'], 'nam': item['Năm']}
                if dict_d in list_distinct_rank:
                    dup_idx = list_distinct_rank.index(dict_d)
                    errors.append(f'Dòng ({idx+2}) bị trùng với dòng ({dup_idx+2})')
                    save_flag = False
                list_distinct_rank.append(dict_d)
        if errors:
            return response_data(status=0, message=errors, data={"save_flag": save_flag})
        return response_data(status=1)

    def import_rank(self, request):
        data = request.data

        if "array" not in data:
            return response_data(status=4, message="Không có dữ liệu import")
        list_field = []
        if 'listField' in data:
            list_field = data['listField']
        lst_rank_create = []
        for idx, item in enumerate(data['array']):
            item_keys = item.keys()
            empty_key_items = [item for item in list_field if item not in item_keys]
            if 'Mã NV' not in item_keys or 'Tháng' not in item_keys or 'Năm' not in item_keys \
                    or 'Email' not in item_keys or 'Họ và tên' not in item_keys or 'Bậc' not in item_keys:
                return response_data(message='Vui lòng điền đầy đủ thông tin: Mã NV, Họ và tên, Tháng, Năm, Email, Bậc',
                                     status=5)
            emp_code = item.pop('Mã NV')
            emp_name = item.pop('Họ và tên')
            bac_nghe = item.pop('Bậc')
            thang = item.pop('Tháng', datetime.today().month)
            nam = item.pop('Năm', datetime.today().year)
            email = item.pop('Email')
            for k in empty_key_items:
                item[k] = ""

            item_sort = {}
            for field in list_field:
                if field not in ['Mã NV', 'Họ và tên', 'Bậc', 'Tháng', 'Năm', 'Email']:
                    item_sort[field] = item[field]

            emp_rank_info = json.dumps(item_sort)
            if EmployeeRank.objects.filter(
                    emp_code=emp_code, thang=thang, nam=nam
            ).exists():
                emp_rank = EmployeeRank.objects.filter(emp_code=emp_code, thang=thang, nam=nam).first()
                update_item = {"empCode": emp_code, "empName": emp_name, "month": thang, "year": nam, "email": email,
                               "empRankInfo": emp_rank_info, "jobLevel": bac_nghe}

                update_serializer = EmployeeRankSerializer(data=update_item)
                if not update_serializer.is_valid():
                    return response_data(data=update_serializer.errors)
                emp_rank.emp_name = update_serializer.validated_data['emp_name']
                emp_rank.email = update_serializer.validated_data['email']
                emp_rank.bac_nghe = update_serializer.validated_data['bac_nghe']
                emp_rank.emp_rank_info = update_serializer.validated_data['emp_rank_info']
                emp_rank.save()

            else:
                lst_rank_create.append({
                    "empCode": emp_code, "empName": emp_name, "month": thang, "year": nam, "email": email,
                    "empRankInfo": emp_rank_info, "jobLevel": bac_nghe})

        serializer_create = EmployeeRankSerializer(data=lst_rank_create, many=True)
        if not serializer_create.is_valid():
            return response_data(data=serializer_create.errors)
        serializer_create.save()

        return response_data(message="import thành công", status=1)

    def edit_rank(self, request):
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        data = request.data
        if "edit_job_level" not in data:
            return response_data(message='phải truyền edit_job_level', status=5)

        if not data['edit_job_level']:
            return response_data(message='Dữ liệu đã chốt không chỉnh sửa được', status=5)
        validate = IdValidate(data=data)

        if not validate.is_valid():
            return response_data(message=validate.errors, status=5)
        if 'Mã NV' in data:
            data.pop('Mã NV')
        if 'Họ và tên' in data:
            data.pop('Họ và tên')
        if 'Tháng' in data:
            data.pop('Tháng')
        if 'Năm' in data:
            data.pop('Năm')
        if 'Email' in data:
            data.pop('Email')
        data.pop('Id')
        em_rank_id = validate.validated_data['Id']
        if not EmployeeRank.objects.filter(id=em_rank_id).exists():
            return response_data(status=5, message="Id chưa tồn tại. Không thể sửa")
        emp_rank = EmployeeRank.objects.filter(id=em_rank_id).first()
        data_save = {
            "id": em_rank_id
        }
        if 'Bậc' in data:
            jobLevel = data.pop('Bậc')
            data_save.update(jobLevel=jobLevel)

        data.pop('edit_job_level')
        empRankInfo = json.dumps(data)
        data_save.update({
            "empRankInfo": empRankInfo,
            "updateBy": data_token['email'],
            "updateTime": datetime.now()
        })

        serializer = EmployeeRankSerializer(emp_rank, data_save)
        if not serializer.is_valid():
            return response_data(status=5, message=serializer.errors)
        if not serializer.save():
            return response_data(status=5, message='Không sửa được')
        return response_data("Sửa thành công")

    def import_vi_to_en_rank(self, **kwargs):
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
                    data_dict[key_list[index]] = data[item]
                data["acctiveTime"] = datetime.now()
            except:
                return {"status": False, "messages": "Lỗi định dạng"}
            serializer = EmployeeRankSerializer(data=data_dict)
            if not serializer.is_valid():
                return {"status": False, "messages": serializer.errors}
            if not serializer.save():
                return {"status": False, "messages": "Import không thành công"}
            return {"status": True}
        return {"status": False, "messages": "Dữ liệu import rỗng"}

    def safe_card_info(self, request):
        try:
            updated_verifier = self.update_situation_safe_card()

            if 1 != updated_verifier.data["statusCode"]:
                return updated_verifier

            data = request.data
            show = data.pop("show", None)
            if "code" in data and data["code"] != "":
                validate = EmpCodeValidate(data=data)
                if not validate.is_valid():
                    return response_data(message=validate.errors, status=5)
                code = data['code'].replace(" ", "")
                queryset = SafeCard.objects.filter(emp_code=code)
                if show is not None and show == "EN":
                    serializer = self.safe_card_data(queryset=queryset)
                    return response_data(serializer)
                serializer = self.safe_card_data(queryset=queryset, VN=SAFE_CARD_EXPORT)
                return response_data(serializer)
            validate = EmpInDepartmentValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            list_code = self.list_code_in_block(request)
            queryset = SafeCard.objects.filter(emp_code__in=list_code)
            if "typeCard" in data and data["typeCard"] != [] and isinstance(data["typeCard"], list):
                queryset = queryset.filter(tinh_trang_the_chung_chi__in=data["typeCard"])
            if show is not None and show == "EN":
                serializer = self.safe_card_data(queryset=queryset)
                return response_data(serializer)
            serializer = self.safe_card_data(queryset=queryset, VN=SAFE_CARD_EXPORT)
            return response_data(serializer)
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))

    def safe_card_data(self, **kwargs):
        queryset = kwargs.pop('queryset', None)
        VN = kwargs.pop('VN', None)
        serializer = SafeCardSerializer(queryset, many=True, emp=True)
        data = serializer.data
        # return data
        for item in data:
            value = item.pop("emp_info")
            if value is None:
                item.update({
                    "childDepart": None,
                    "dateJoinCompany": None,
                    "name": None,
                    "sex": None,
                    "birthday": None,
                    "cmnd": None,
                    "statusWorking": None,
                    "dateQuitJob": None,
                    "jobTitle": None
                })
            else:
                item.update(value)
            if VN is not None:
                fields = []
                for key in VN:
                    fields.append(key)
                allowed = set(fields)
                existing = set(item)
                for field_name in fields:
                    item[VN[field_name]] = item.pop(field_name)
                for field_name in existing - allowed:
                    item.pop(field_name)
        return data

    def add_safe_card(self, request):
        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        user_email = data_token.get("email", "")

        data = request.data
        if "action" in data and data["action"] == "edit":
            validate = IdValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            queryset = SafeCard.objects.filter(atld_id=data["id"]).first()
            serializer = SafeCardSerializer(queryset, many=True)
            if not SafeCard.objects.filter(atld_id=data["id"]).exists():
                return response_data(status=5, message="Id chưa tồn tại. Không thể sửa")
            list_data_key = data.keys()
            data_save = {}
            for item in list_data_key:
                if data[item] != "" and data[item] != "edit":
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
                    print("---------------------UP HINH THANH CONG--------------------")
                    print(list_img)
                else:
                    print("---------------------UP HINH --------------------")
                    print(msg_code)
                    return response_data(data={}, message="Không thể up hình", status=status_code)

            serializer = SafeCardSerializer(queryset, data=data_save)
            if not serializer.is_valid():
                return response_data(status=5, message=serializer.errors)
            if not serializer.save():
                return response_data(status=5, message="Không sửa được")
            return response_data(message="Sửa thành công")
        try:
            if "action" in data and data["action"] == "delete":
                validate = IdValidate(data=data)
                if not validate.is_valid():
                    return response_data(status=5, message=validate.errors)
                queryset = SafeCard.objects.filter(atld_id=data["id"]).first()
                serializer = SafeCardSerializer(queryset, many=True)
                if not SafeCard.objects.filter(atld_id=data["id"]).exists():
                    return response_data(status=5, message="Id chưa tồn tại. Không thể xoá")
                queryset.delete()
                return response_data(message="Xoá thành công")
        except:
            return response_data(status=5, message="Xoá lỗi")

        validate = AddSafeCardValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message=validate.errors)
        if "pictureCertificate" in data and data["pictureCertificate"] == "":
            data.pop("pictureCertificate")
        data["updateTime"] = datetime.now()

        number_file = data.get("numberFile", 0)

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
                data['pictureCertificate'] = str_img
                print("---------------------UP HINH THANH CONG--------------------")
                print(list_img)
            else:
                print("---------------------UP HINH --------------------")
                print(msg_code)
                return response_data(data={}, message="Không thể up hình", status=status_code)

        serializer = SafeCardSerializer(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=serializer.errors)
        if not serializer.save():
            return response_data(message="Thêm thất bại")
        return response_data(message="Thêm thành công")

    def import_safe_card(self, request):
        data = request.data
        if "array" not in data or data["array"] == []:
            return response_data(status=4, message="Không có dữ liệu import")
        for item in data['array']:
            data_dict = self.import_vi_to_en_safe_card(EN=SAFE_CARD_INPUT, data=item)
            print(data_dict['status'])
            if not data_dict['status']:
                return response_data(message=data_dict['messages'], status=5)
        return response_data(message="Import thành công", status=1)

    def import_vi_to_en_safe_card(self, **kwargs):
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
                    data_dict[key_list[index]] = data[item]
                data_dict["updateTime"] = datetime.now()
            except:
                return {"status": False, "messages": "Lỗi định dạng"}
            serializer = SafeCardSerializer(data=data_dict)
            if not serializer.is_valid():
                return {"status": False, "messages": serializer.errors}
            if not serializer.save():
                return {"status": False, "messages": "Import không thành công"}
            return {"status": True}
        return {"status": False, "messages": "Dữ liệu import rỗng"}

    def update_situation_safe_card(self, request=None):
        try:
            today = datetime.now().date()
            day_45 = today + timedelta(days=45)

            queryset = SafeCard.objects.exclude(
                tinh_trang_the_chung_chi__in=["Hết Hạn", "Chưa Cấp"]
            )

            for data in queryset:
                try:
                    if data.ngay_het_han_ATLD <= day_45 and data.ngay_het_han_ATLD > today:
                        data.tinh_trang_the_chung_chi = "Sắp Hết Hạn"
                    elif data.ngay_het_han_ATLD <= today:
                        data.tinh_trang_the_chung_chi = "Hết Hạn"
                    data.save()
                except Exception as e_SafeCard:
                    print(e_SafeCard)
                    continue
            return response_data()
        except Exception as e:
            print(e)
            return response_data(status=4, message=str(e))
