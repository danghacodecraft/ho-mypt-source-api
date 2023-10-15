import ast
from rest_framework import serializers
from ..models.hr import *
from ..models.contract import *
from ..models.user_profile import *
from ...core.helpers import helper
from ...core.helpers.helper import convert_vi_to_en
from ...http.validations.hr_validate import *
from ...core.helpers.no_accent_vietnamese import no_accent_vietnamese
from app.configs import service_api_config
from ..serializers.info_modify_history_serializer import InformationModifyHistorySerializer

class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    email = serializers.CharField(required=False, allow_null=True)
    birthday = serializers.DateField(format='%d/%m/%Y', required=False, allow_null=True)
    day = serializers.CharField(required=False, allow_null=True)
    month = serializers.CharField(required=False, allow_null=True)
    year = serializers.CharField(required=False, allow_null=True)
    mstcn = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sex = serializers.CharField(required=False, allow_null=True)
    cmnd = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField(source='emp_code', required=False, allow_null=True, max_length=8, allow_blank=True,)
    name = serializers.CharField(source='emp_name', required=False, allow_null=True)
    jobTitle = serializers.CharField(source='job_title', required=False, allow_null=True, allow_blank=True)
    childDepart = serializers.CharField(source='child_depart', required=False, allow_null=True, allow_blank=True)
    mobilePhone = serializers.CharField(source='mobile_phone', required=False, allow_null=True, allow_blank=True)
    dependentInfo = serializers.CharField(source='dependent_info', required=False, allow_null=True, allow_blank=True)
    contractType = serializers.CharField(source='contract_type', required=False, allow_null=True, allow_blank=True)
    contractCode = serializers.CharField(source='contract_code', required=False, allow_null=True, allow_blank=True)
    contractBegin = serializers.DateField(format='%d/%m/%Y', source='contract_begin', required=False, allow_null=True)
    contractEnd = serializers.DateField(format='%d/%m/%Y', source='contract_end', required=False, allow_null=True)
    accountNumber = serializers.CharField(source='account_number', required=False, allow_null=True, allow_blank=True)
    typeSalary = serializers.CharField(source='type_salary', required=False, allow_null=True, allow_blank=True)
    statusWorking = serializers.IntegerField(source='status_working', required=False, allow_null=True)
    dateJoinCompany = serializers.DateField(format='%d/%m/%Y', source='date_join_company', required=False,
                                            allow_null=True)
    dateQuitJob = serializers.DateField(format='%d/%m/%Y', source='date_quit_job', required=False, allow_null=True)
    updateTime = serializers.DateTimeField(source='update_time', required=False, allow_null=True)
    updateBy = serializers.CharField(source='update_by', required=False, allow_null=True, allow_blank=True)
    avatarImg = serializers.CharField(source='avatar_img', required=False, allow_null=True, allow_blank=True)
    idUser = serializers.CharField(source='id_user', required=False, allow_null=True, allow_blank=True)

    placeOfBirth = serializers.CharField(source='place_of_birth', required=False, allow_null=True, allow_blank=True)
    nationality = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date = serializers.DateField(format='%d/%m/%Y', source='ngay_cap_cmnd', required=False, allow_null=True)
    issuedAt = serializers.CharField(source='noi_cap_cmnd', required=False, allow_null=True, allow_blank=True)
    placeOfPermanent = serializers.CharField(source='place_of_permanent', required=False, allow_null=True,
                                             allow_blank=True)
    degree = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    workplace = serializers.CharField(required=False, allow_null=True, max_length=255, allow_blank=True,
                                      error_messages={
                                          "max_length": "Vượt quá độ dài tối đa, nơi làm việc là mã tòa nhà/văn phòng"
                                      })
    level = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    socialInsuranceSalaryPay = serializers.CharField(source='social_insurance_salary_pay', required=False,
                                                     allow_null=True, allow_blank=True)
    placeToJoinSocialInsurance = serializers.CharField(source='place_to_join_social_insurance', required=False,
                                                       allow_null=True, allow_blank=True)
    taxIdentificationPlace = serializers.CharField(source='tax_identification_place', required=False, allow_null=True, allow_blank=True)
    taxIdentificationDate = serializers.DateField(format='%d/%m/%Y',
                                                  source='tax_identification_date',
                                                  required=False,
                                                  allow_null=True)

    maritalStatus = serializers.IntegerField(source='marital_status',
                                            allow_null=True,
                                            default=None)
    bankName = serializers.CharField(source='bank_name', required=False, allow_null=True, allow_blank=True)
    healthInsurance = serializers.CharField(source='health_insurance', required=False, allow_null=True,allow_blank=True)
    socialInsurance = serializers.CharField(source='social_insurance', required=False, allow_null=True,allow_blank=True)

    foxpay = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fullChildDepart = serializers.SerializerMethodField()
    levelDepart = serializers.SerializerMethodField()
    branch = serializers.SerializerMethodField()
    parentDepart = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    plurality = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    officerTitle = serializers.CharField(source="officer_title", required=False, allow_null=True, allow_blank=True, default=None)
    idPhone = serializers.CharField(source="id_phone", required=False, allow_null=True, allow_blank=True, default=None)
    comment = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    contractTypeCode = serializers.CharField(source="contract_type_code", required=False, allow_null=True, allow_blank=True, default=None)
    jobCode = serializers.CharField(source="job_code", required=False, allow_null=True, allow_blank=True, default=None)
    officerCode = serializers.CharField(source="officer_code", required=False, allow_null=True, allow_blank=True, default=None)

    createdAt = serializers.DateTimeField(source='created_at', required=False, allow_null=True)
 
    def __init__(self, *args, **kwargs):

        # self.contracts_type = kwargs.pop('contractType', None)

        fields = kwargs.pop('fields', None)

        VN = kwargs.pop('VN', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if VN is not None:
            fields = []
            for key in VN:
                fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)

            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def to_representation(self, instance):
        data = super(EmployeeSerializer, self).to_representation(instance)

        if "Giới tính" in data:
            sex = data["Giới tính"]
            if sex == "M":
                data.update({"Giới tính": "Nam"})
            elif sex == "F":
                data.update({"Giới tính": "Nữ"})
        return data

    def get_fullChildDepart(self, emp_object):
        department = Department.objects.filter(child_depart=emp_object.child_depart) \
            .values("parent_depart", "chi_nhanh", "child_depart")
        if len(department) > 0:
            return f"{department[0]['parent_depart']}/{department[0]['chi_nhanh']}/{department[0]['child_depart']}"
        return None

    def get_parentDepart(self, emp_object):
        department = Department.objects.filter(child_depart=emp_object.child_depart) \
            .values_list("parent_depart", flat=True)
        if len(department) > 0:
            return department[0]
        return None
    
    def get_levelDepart(self, emp_object):
        department = Department.objects.filter(child_depart=emp_object.child_depart) \
            .values_list("level_department", flat=True)
        if len(department) > 0:
            return department[0]
        
    def get_branch(self, emp_object):
        department = Department.objects.filter(child_depart=emp_object.child_depart) \
            .values_list("branch", flat=True)
        if len(department) > 0:
            return department[0]

    def get_unit(self, emp_object):
        department = Department.objects.filter(child_depart=emp_object.child_depart) \
            .values("chi_nhanh")
        if len(department) > 0:
            return department[0]['chi_nhanh']
        return None

    def validate_childDepart(self, child_depart):   
        if not Department.objects.filter(child_depart=child_depart).exists():
            raise serializers.ValidationError('Phòng ban không tồn tại!')
        return child_depart

    def get_all_emp_code(status_working=None, fname=""):
        list_data = []
        try:
            if not is_null_or_empty(status_working):
                queryset = Employee.objects.filter(status_working=status_working).values('emp_code')
                if len(queryset) > 0:
                    for i in queryset:
                        list_data.append(i['emp_code'])
            else:
                queryset = Employee.objects.all().values('emp_code')
                if len(queryset) > 0:
                    for i in queryset:
                        list_data.append(i['emp_code'])
        except Exception as ex:
            print("{} >> {} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), "get_all_emp_code", fname, ex))
        return list_data

    def genarate_modify_history(self, key, modified_value):
        pass

    def create(self, validated_data):
        contract_data = {
            "emp_code": validated_data.get("emp_code", None),
            "contract_type": validated_data.get("contract_type", None),
            "contract_code": validated_data.get("contractCode", None),
            "contract_start_date": validated_data.get("contract_begin", None),
            "contract_end_date": validated_data.get("contract_end", None),
            "update_time": validated_data.get("update_time", None),
            "update_by": validated_data.get("update_by", None),
        }

        if not Contract.objects.filter(
            emp_code=validated_data.get("emp_code", ""),
            contract_type=validated_data.get("contract_type", "")
        ).exists():
            Contract.objects.create(**contract_data)
        employee = Employee.objects.create(**validated_data)
        return employee

    def update(self, instance, validated_data):
        modification = []

        for k, v in validated_data.items():
            if v != getattr(instance, k) and k not in ['email', 'emp_code']:
                modification.append({
                    "email": instance.email,
                    "emp_code": instance.emp_code,
                    "old_value": str(getattr(instance, k)),
                    "new_value": str(v),
                    "key_semantic": self.Meta.model._meta.get_field(k).verbose_name,
                    "key_name": k
                })
                setattr(instance, k, v)

        contract_data = {
            "emp_code": validated_data.get("emp_code", None),
            "contract_type": validated_data.get("contract_type", None),
            "contract_code": validated_data.get("contract_code", None),
            "contract_start_date": validated_data.get("contract_begin", None),
            "contract_end_date": validated_data.get("contract_end", None),
            "update_time": validated_data.get("update_time", None),
            "update_by": validated_data.get("update_by", None),
        }
        try:
            history = InformationModifyHistorySerializer(data=modification, many=True)
            if not history.is_valid():
                print(history.errors)
            else:
                history.save()
        except Exception as e:
            print(e)


        try:
            instance.save()

            # cap nhat hop dong
            if not Contract.objects.filter(
                emp_code=validated_data.get("emp_code", ""),
                contract_type=validated_data.get("contract_type", "")
            ).exists():
                Contract.objects.create(**contract_data)

            # cap nhat profile
            app_env = project_settings.APP_ENVIRONMENT
            _user_email = validated_data.get("email", instance.email)
            response = helper.request_api(
                host=service_api_config.SERVICE_CONFIG["HO-AUTH"][app_env],
                func=service_api_config.SERVICE_CONFIG["HO-AUTH"]["get-user-id-by-email"][
                                           "func"],
                method=service_api_config.SERVICE_CONFIG["HO-AUTH"]["get-user-id-by-email"][
                                           "method"],
                data={
                    "email": _user_email 
                        if app_env == "production" 
                        else _user_email.replace("stag_", "") 
                }
            )
            if response:
                response = response.json()
                if response.get("statusCode") == 1:
                    user_id = response['data']['userId']
                    UserProfile.objects.filter(user_id=user_id).update(
                        birthday=validated_data.get("birthday", instance.birthday),
                        sex=validated_data.get("sex", instance.sex),
                        mobile_phone=validated_data.get("mobile_phone", instance.mobile_phone),
                        place_of_birth=validated_data.get("place_of_birth", instance.place_of_birth),
                        nationality=validated_data.get("nationality", instance.nationality),
                        marital_status=validated_data.get("marital_status", instance.marital_status)
                    )
        except Exception as e:
            print(e)

        return instance
    
    def validate(self, data):
        for item in data:
            if str.__subclasscheck__(data[item].__class__):
                if data[item].strip() == "":
                    data[item] = None
        return data

    @staticmethod
    def marital_status_mapping(status):
        pattern = {
            "Chưa kết hôn": 0,
            "Đã kết hôn": 1,
            "Kết hôn": 1,
            "Đã ly hôn": 2
        }
        return pattern.get(status, None)

    @staticmethod
    def gender_mapping(status):
        pattern = ["O", "M", "F"]
        if int.__subclasscheck__(status.__class__) and status >= 0 and status < len(pattern):
            return pattern[status]
        return None

    class Meta:
        model = Employee
        fields = [
            'email', 'code', 'name',
            'birthday', 'day', 'month',
            'year', 'jobTitle',
            'childDepart', 'fullChildDepart',
            'parentDepart', 'unit',
            'mobilePhone', 'mstcn', 'dependentInfo',
            'contractType', 'contractCode', 'contractBegin', 'contractEnd',
            'accountNumber', 'typeSalary', 'sex',
            'statusWorking', 'cmnd', 'dateJoinCompany',
            'dateQuitJob', 'updateTime', 'updateBy',
            'avatarImg', 'idUser',

            'placeOfBirth', 'nationality', 'date',
            'issuedAt', 'placeOfPermanent',
            'degree', 'workplace', 'level',
            'socialInsuranceSalaryPay',
            'placeToJoinSocialInsurance',
            'taxIdentificationPlace',
            'taxIdentificationDate',

            'maritalStatus', 'bankName',
            'healthInsurance', 'socialInsurance',

            'foxpay', "officerTitle", "comment", "plurality",
            "idPhone", "contractTypeCode", "jobCode", "officerCode","levelDepart", "branch",

            'createdAt'
        ]


    def get_job_title_from_emp_code(emp_code):
        job_title = ""
        try:
            data = Employee.objects.filter(emp_code=emp_code).values()
            if len(data) > 0:
                info = data[0]
                job_title = info['job_title']
        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), "get_job_title_from_emp_code", ex))
        return job_title

    def get_info_present_atld(list_emp_code):
        dict_info = {}
        try:
            queryset = Employee.objects.filter(emp_code__in=tuple(list_emp_code)).values('child_depart', 'emp_code',
                                                                                         'emp_name',
                                                                                         'date_join_company',
                                                                                         'sex', 'birthday', 'cmnd',
                                                                                         'status_working',
                                                                                         'date_quit_job', 'job_title')

            queryset_child_depart = Employee.objects.filter(emp_code__in=tuple(list_emp_code)).values_list(
                'child_depart', flat=True)
            list_rs_child_depart = list(queryset_child_depart)
            if len(queryset) > 0:
                qr_set_parent_depart = Department.objects.filter(child_depart__in=tuple(list_rs_child_depart)).values(
                    'chi_nhanh', 'parent_depart', 'child_depart')
                dict_child_depart = {}
                for k in qr_set_parent_depart:
                    dict_child_depart.update({
                        k['child_depart']: {
                            'parent_depart': k['parent_depart'],
                            'chi_nhanh': k['chi_nhanh']
                        }
                    })

                for i in queryset:
                    emp_code = i['emp_code']
                    # ticket['t_assigned'].strftime('%d/%m/%Y %H:%M:%S')

                    date_join_company = ""
                    if not is_null_or_empty(i['date_join_company']):
                        date_join_company = convert_date_db_to_str_date_export(i['date_join_company'])

                    birthday = ""
                    if not is_null_or_empty(i['birthday']):
                        birthday = convert_date_db_to_str_date_export(i['birthday'])
                    dict_detail_child_depart = dict_child_depart.get(i['child_depart'], {})
                    parent_depart = dict_detail_child_depart.get('parent_depart', '')
                    chi_nhanh = dict_detail_child_depart.get('chi_nhanh', '')
                    dict_info.update({
                        emp_code: {
                            "childDepart": i['child_depart'],
                            "dateJoinCompany": date_join_company,
                            "name": i['emp_name'],
                            "sex": i['sex'],
                            "birthday": birthday,
                            "cmnd": i['cmnd'],
                            "statusWorking": i['status_working'],
                            "dateQuitJob": i['date_quit_job'],
                            'parentDepart': parent_depart,
                            'agency': chi_nhanh,
                            'jobTitle': i['job_title']

                            # "jobTitle": i['job_title']
                        }

                    })
        except Exception as ex:
            print("{} >>  get_info_present_atld >> Error/Loi : {} ".format(get_str_datetime_now_import_db(), ex))
        return dict_info


class DepartmentFilterSerializer(serializers.ModelSerializer):
    childDepart = serializers.CharField(source='child_depart')
    # branch = serializers.CharField(source='branch')
    parentDepart = serializers.CharField(source='parent_depart')
    chiNhanh = serializers.CharField(source="chi_nhanh")
    childDepart1 = serializers.CharField(source='child_depart1')
    dienGiai = serializers.CharField(source='dien_giai')
    codeChildDepart = serializers.CharField(source='code_child_depart')

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Department
        fields = ['childDepart', 'branch', 'parentDepart', 'chiNhanh',
                  'childDepart1', 'dienGiai', 'codeChildDepart']


class DepartmentSerializer(serializers.ModelSerializer):
    childDepart = serializers.CharField(source='child_depart')
    # branch = serializers.CharField(source='branch')
    parentDepart = serializers.CharField(source='parent_depart')
    chiNhanh = serializers.CharField(source="chi_nhanh")
    childDepart1 = serializers.CharField(source='child_depart1')
    dienGiai = serializers.CharField(source='dien_giai')
    codeChildDepart = serializers.CharField(source='code_child_depart')

    techManagerEmail = serializers.CharField(source='tech_manager_email')

    # def validate_branch(self, value):
    #     if 'django' not in value.lower():
    #         raise serializers.ValidationError("Blog post is not about Django")
    #     return value

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        emp_info = kwargs.pop('emp_info', False)

        super().__init__(*args, **kwargs)

        if emp_info:
            self.fields['emp_info'] = EmployeeSerializer(many=True, fields=['code', 'name'])

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def get_all_info_from_list_child_depart(list_child_depart, fname=""):
        dict_info = {}
        try:
            queryset = Department.objects.filter(child_depart=tuple(list_child_depart)).values('parent_depart',
                                                                                               'chi_nhanh')
            if len(queryset) > 0:
                for i in queryset:
                    dict_info.update({
                        i['child_depart']: {
                            "parentDepart": i['parent_depart'],
                            "department": i['chi_nhanh']
                        }
                    })

        except Exception as ex:
            print("{} >> {} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname,
                                                           "get_all_info_from_child_depart", ex))
        return dict_info

    def get_parent_depart_from_child_depart(child_depart):
        parent_depart = ""
        branch = ""
        dict_info = {}

        try:

            info_depart = Department.objects.filter(child_depart__in=tuple(child_depart)).values()
            if len(info_depart) > 0:
                for k in info_depart:
                    data_info = k
                    parent_depart = data_info['parent_depart']
                    department = data_info['chi_nhanh']
                    branch = data_info['branch']
                    tinh_tp = data_info['tinh_tp']
                    doi_tac = data_info['chi_nhanh']
                    loop_mail_kt = data_info['loop_mail_kt']
                    name_child_depart = data_info['child_depart']

                    child_depart_2 = data_info['child_depart']
                    dict_info.update({
                        child_depart_2: {
                            "department": department,
                            "parentDepart": parent_depart,
                            "branch": branch,
                            "tinh_tp": tinh_tp,
                            "doi_tac": doi_tac,
                            "loop_mail_kt": loop_mail_kt,
                            "name_child_depart": name_child_depart
                        }
                    })
        except Exception as ex:
            print("======================get_child_depart_from_emp_code===============")
            print("{} >> Error/Loi : {}".format(get_str_datetime_now_import_db(), ex))
        return dict_info

    def get_all_info_for_child_depart(fname="", time_log=""):
        dict_data = {}
        try:
            qr = Department.objects.all().values()
            for i in qr:
                child_depart = i['child_depart']
                parent_depart = i['parent_depart']
                agency = i['chi_nhanh']
                dict_data.update({
                     child_depart:{
                         'parent_depart': parent_depart,
                         'agency': agency
                     }

                })

        except Exception as ex:
            print("{} >> {} >> {} >> Error/loi: {}".format(time_log, fname, "get_all_info_for_child_depart", ex))
        return dict_data

    class Meta:
        model = Department
        fields = ['childDepart', 'branch', 'parentDepart', 'chiNhanh',
                  'childDepart1', 'dienGiai', 'codeChildDepart', 'emp_info', 'techManagerEmail']
        # fields = ['childDepart', 'branch', 'parentDepart', 'chiNhanh',
        #           'childDepart1', 'dienGiai', 'codeChildDepart', 'techManagerEmail']


class EmployeeRankSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    empCode = serializers.CharField(required=False, source="emp_code")
    empName = serializers.CharField(required=False, source="emp_name")
    month = serializers.IntegerField(required=False, source="thang")
    year = serializers.IntegerField(required=False, source="nam")
    email = serializers.CharField(required=False)
    # monthYear = serializers.CharField(required=False, source="thang_nam")
    empRankInfo = serializers.CharField(required=False, source="emp_rank_info")

    jobLevel = serializers.FloatField(required=False, source="bac_nghe")

    updateTime = serializers.DateTimeField(required=False, source="update_time")
    updateBy = serializers.CharField(required=False, source="update_by")

    # parentDepart = serializers.CharField(required=False, source="parent_depart")
    # childDepart = serializers.CharField(required=False, source="child_depart")

    class Meta:
        model = EmployeeRank
        fields = [
            "id", "empCode", "empName", "month", "year", "email", "empRankInfo", "jobLevel", "updateTime", "updateBy"
        ]

    def validate_empRankInfo(self, empRankInfo):
        dict_emp_rank = ast.literal_eval(empRankInfo)
        for (key, value) in dict_emp_rank.items():
            if isinstance(value, float) or isinstance(value, int):
                dict_emp_rank.update({key: str(value)})

        return dict_emp_rank

    def to_representation(self, data):
        emp_rank_info = ast.literal_eval(data.emp_rank_info)
        return {
            # "Id": item['id'],
            "Mã NV": data.emp_code,
            "Họ và tên": data.emp_name,
            "Email": data.email,
            "Tháng": data.thang,
            "Năm": data.nam,
            # "monthYear": item['monthYear'],
            **emp_rank_info,
            "Bậc": data.bac_nghe
        }


class EmployeeRankSerializerEN(EmployeeRankSerializer):
    def to_representation(self, data):
        emp_rank_info = ast.literal_eval(data.emp_rank_info)
        emp_rank_info_en = {}
        for k, v in emp_rank_info.items():
            en_key = convert_vi_to_en(k).replace(" ", "_").lower()
            emp_rank_info_en[en_key] = v
        return {
            "id": data.id,
            "emp_code": data.emp_code,
            "emp_name": data.emp_name,
            "email": data.email,
            "month": data.thang,
            "year": data.nam,
            # "monthYear": item['monthYear'],
            **emp_rank_info_en,
            # "emp_rank_info": data.emp_rank_info,
            "job_level": data.bac_nghe,
            "edit_job_level": check_editable_emp_rank(data.thang, data.nam)
        }


class SafeCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="atld_id", required=False)
    empCode = serializers.CharField(source="emp_code", required=False)
    trainingGroup = serializers.CharField(source="nhom_dao_tao", required=False, allow_blank=True)
    certificate = serializers.CharField(source="cap_the_chung_chi", required=False)
    dateCertificate = serializers.DateField(format='%d/%m/%Y', source="ngay_cap_the_ATLD", required=False)
    expirationDate = serializers.DateField(format='%d/%m/%Y', source="ngay_het_han_ATLD", required=False)
    trainingStartDate = serializers.DateField(format='%d/%m/%Y', source="ngay_bat_dau_dao_tao", required=False)
    trainingEndDate = serializers.DateField(format='%d/%m/%Y', source="ngay_ket_thuc_dao_tao", required=False)
    statusCertificate = serializers.CharField(source="tinh_trang_the_chung_chi", required=False)
    pictureCertificate = serializers.CharField(source="hinh_anh_the_chung_nhan", required=False, allow_null=True,
                                               allow_blank=True)
    updateTime = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', source="update_time_atld", required=False)
    active = serializers.IntegerField(required=False, allow_null=True)
    numberCard = serializers.CharField(source='number_card', required=False, allow_null=True, allow_blank=True)
    updateBy = serializers.CharField(source="update_by", required=False)
    createdBy = serializers.CharField(source="created_by", required=False, allow_null=True, allow_blank=True)
    createdAt = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', source="created_time", required=False)
    jobTitle = serializers.CharField(source='job_title', required=False, allow_null=True, allow_blank=True)

    childDepart = serializers.CharField(source="child_depart", required=False, allow_null=True, allow_blank=True)
    parentDepart = serializers.CharField(source="parent_depart", required=False, allow_null=True, allow_blank=True)
    agency = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(source="emp_name", required=False, allow_null=True, allow_blank=True)
    dateJoinCompany = serializers.DateField(format='%d/%m/%Y', source="date_join_company", required=False,
                                            allow_null=True)
    sex = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    birthday = serializers.DateField(format='%d/%m/%Y', required=False, allow_null=True)
    cmnd = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    dateQuitJob = serializers.DateField(format='%d/%m/%Y', source="date_quit_job", required=False, allow_null=True)

    # typeProvide = serializers.CharField(source='typeProvide', required=False)
    # department = DepartmentSerializer(fields = ['childDepart','branch','parentDepart','childDepart1','dienGiai','codeChildDepart','emp_info'])
    # emp_info = EmployeeSerializer(
    #     fields=["childDepart", "dateJoinCompany", "name", "sex", "birthday", "cmnd", "statusWorking", "dateQuitJob",
    #             "jobTitle"])

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        emp = kwargs.pop('emp', False)
        VN = kwargs.pop('VN', None)

        super().__init__(*args, **kwargs)

        # if not emp:
        #     self.fields.pop("emp_info")
        # self.fields.pop("department")

        # data = self.fields.pop("emp_info")
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if VN is not None:
            fields = []
            for key in VN:
                fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)
            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = SafeCard
        fields = [
            "id", "empCode", "trainingGroup", "certificate",
            "dateCertificate", "expirationDate", "trainingStartDate",
            "trainingEndDate", "statusCertificate", "pictureCertificate",
            "updateTime", "updateBy", "active", "numberCard", "createdBy", "createdAt", 'jobTitle',
            'childDepart', 'agency', 'parentDepart', 'dateJoinCompany', 'name', 'sex', 'birthday', 'cmnd', 'dateQuitJob'
        ]

    def check_emp_code_in_list_train(emp_code):
        ok = False
        try:
            str_date_input = get_interval_list_train_safe_card()
            if SafeCard.objects.filter(ngay_het_han_ATLD__lte= str_date_input,
                                       emp_code=emp_code).exists():
                ok = True

        except Exception as ex:
            print("check_emp_code_in_list_train >> {} >> Error/Loi:{}".format(get_str_datetime_now_import_db(), ex))
            ok = False
        return ok

    def list_train_available(fname=""):
        list_emp_code = []
        try:
            str_date_input = get_interval_list_train_safe_card()
            qr = SafeCard.objects.filter(ngay_het_han_ATLD__lte= str_date_input).values_list('emp_code', flat=True)
            if len(qr) > 0:
                list_emp_code = list(qr)
        except Exception as ex:
            print("{} >> Error/Loi: {}".format(fname, ex))
        return list_emp_code

    def auto_update_active_from_emp_code_and_date_provide_card(emp_code, ngay_cap_the):
        # ngay_cap_the = "%Y-%m-%d"
        ok = True
        try:
            data = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__gt=ngay_cap_the).order_by(
                "-ngay_cap_the_ATLD").values()

            if len(data) > 0:

                info = data[0]
                max_date = info['ngay_cap_the_ATLD']
                SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=max_date).update(active=0)
                SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=max_date).update(active=1)
            else:
                SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the).update(active=1)
                SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=ngay_cap_the).update(active=0)


        except Exception as ex:
            ok = False
            print("{} >> {} >> Error/Loi >> {}".format(get_str_datetime_now_import_db(), "auto_update_active", ex))
        return ok

    def get_list_id_update_active(emp_code, ngay_cap_the):
        list_id_active_0 = []
        list_id_active_1 = []
        try:
            data = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__gt=ngay_cap_the).order_by(
                "-ngay_cap_the_ATLD").values()

            if len(data) > 0:

                info = data[0]
                max_date = info['ngay_cap_the_ATLD']
                # SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=max_date).update(active=0)
                # SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=max_date).update(active=1)
                query0 = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=max_date).values_list(
                    'atld_id', flat=True)
                list_id_active_0 = list(query0)
                query1 = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=max_date).values_list('atld_id',
                                                                                                            flat=True)
                list_id_active_1 = list(query1)




            else:
                # SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the).update(active=1)
                # SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=ngay_cap_the).update(active=0)

                query1 = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD=ngay_cap_the).values_list(
                    'atld_id', flat=True)
                list_id_active_1 = list(query1)
                query0 = SafeCard.objects.filter(emp_code=emp_code, ngay_cap_the_ATLD__lt=ngay_cap_the).values_list(
                    'atld_id', flat=True)
                list_id_active_0 = list(query0)


        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi >> {}".format(get_str_datetime_now_import_db(), "get_list_id_update_active", ex))
        return list_id_active_0, list_id_active_1

    def get_status_card_from_expire_date(str_date, fname=""):
        state = "Còn hạn"
        try:
            if not is_null_or_empty(str_date):
                ngay_het_han = convert_str_date_input_to_datetime(str_date)
                ngay_hien_tai = get_current_date()

                day_45 = ngay_hien_tai + timedelta(days=45)

                if ngay_het_han <= ngay_hien_tai:
                    state = "Hết hạn"
                elif ngay_het_han > ngay_hien_tai:
                    if ngay_het_han <= day_45:
                        state = "Sắp hết hạn"

                # if ngay_het_han <= day_45 and ngay_het_han > ngay_hien_tai:
                #     state = "Sắp hết hạn"
                # elif ngay_het_han <= ngay_hien_tai:
                #     state = "Hết hạn"

                # if day_45 >= ngay_hien_tai:
                #     state = "Sắp hết hạn"
                #     if ngay_het_han <= ngay_hien_tai:
                #         state = "Hết hạn"


        except Exception as ex:
            print("{} >> {} >> Error/Loi >> {}".format(get_str_datetime_now_import_db(),
                                                       "get_status_card_from_exprire_date", ex))
        return state


class TypeGroupTrainingWorkSafeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    jobTitle = serializers.CharField(required=False,
                                     allow_blank=True, allow_null=True, source='job_title')
    trainGroup = serializers.CharField(required=False,
                                       allow_blank=True, allow_null=True, source='train_group')
    typeCard = serializers.CharField(required=False,
                                     allow_blank=True, allow_null=True, source='type_card')

    class Meta:
        model = TypeGroupTrainingWorkSafe
        fields = [
            "id", "jobTitle", "trainGroup", "typeCard"
        ]

    def get_info_from_job_title(job_title):
        train_group = "Nhóm 1"
        type_card = "NV thuộc đối tượng cấp Chứng Nhận"
        try:
            data = TypeGroupTrainingWorkSafe.objects.filter(job_title=job_title).values()
            if len(data) > 0:
                info = data[0]
                train_group = info['train_group']
                type_card = info['type_card']
        except Exception as ex:
            print("{} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), "get_info_from_job_title", ex))

        return train_group, type_card

    def get_all_info_for_job_title(fname=""):
        dict_data = {}
        try:
            qr = TypeGroupTrainingWorkSafe.objects.all().values()
            for i in qr:
                job_title = i['job_title']
                train_group = i['train_group']
                type_card = i['type_card']
                dict_data.update({
                    job_title: {
                        'train_group': train_group,
                        'type_card': type_card
                    }
                })
        except Exception as ex:
            print("{} >> {} >> {} >> Error/Loi: {} ".format(get_str_datetime_now_import_db(), "get_all_info_for_job_title", fname, ex))
        return dict_data



class HistoriesDeleteCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    cardId = serializers.IntegerField(required=False,
                                      source='card_id')
    updateAt = serializers.DateTimeField(required=False, allow_null=True,
                                         format="%d/%m/%Y %H:%M:%S", source='update_at')
    updateBy = serializers.CharField(required=False,
                                     allow_blank=True, source='update_by')
    infoCard = serializers.CharField(required=False,
                                     allow_blank=True, source='info_card')

    class Meta:
        model = HistoriesDeleteCard
        fields = [
            "id", "cardId", "updateAt", "updateBy", "infoCard"
        ]
