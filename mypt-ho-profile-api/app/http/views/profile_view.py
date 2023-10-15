import os

import numpy as np
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist

from ...core.helpers.global_variable import STATUS_CODE_FAILED, MESSAGE_API_FAILED, AVATAR_DEFAULT
from ...core.helpers.response import *
from ...core.helpers.utils import empty,  get_str_datetime_now_import_db, is_null_or_empty
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
from ..models.hr import Department, DepartmentFilter
from ..models.hr import Employee
from ..serializers.user_profile_serializer import *
from ..serializers.hr_serializer import EmployeeSerializer
from ..serializers.hr_serializer import DepartmentSerializer, DepartmentFilterSerializer
import ast
from django.db import connection, transaction
from django.db.models import F
from ..models.features_roles import FeaturesRoles
from ..models.features_roles_emails import FeaturesRolesEmails
from ..serializers.features_roles_serializer import FeaturesRolesSerializer
from ..serializers.features_roles_emails_serializer import FeaturesRolesEmailsSerializer
from datetime import datetime
from ...core.helpers import auth_session_handler as authSessionHandler


class ProfileView(ViewSet):
    # API nay chi de goi private. API nay chi de cho service mypt-ho-auth-api goi, trong t/h tao Access Token
    def get_profile_info(self, request):
        email = request.data['email']
        email = email.lower()
        userId = request.data['userId']
        fullName = request.data['fullName']
        specificChildDeparts = request.data.get("specificChildDeparts", [])

        # Tim xem userId nay co profile hay chua
        profileQs = UserProfile.objects.filter(user_id=userId)[0:1]
        profileSer = UserProfileSerializer(profileQs, many=True)
        profileArrs = profileSer.data

        newUserProfile = None
        link_avatar = ""
        if len(profileArrs) <= 0:
            is_has_profile = False
            # print("Chuan bi tao user profile cho userId " + str(userId))
            # Neu chua co profile : tao profile cho userId nay
            newUserProfile = UserProfile()
            newUserProfile.user_id = userId
            newUserProfile.email = email
            newUserProfile.full_name = fullName
            newUserProfile.save()
        else:
            is_has_profile = True
            link_avatar = profileArrs[0]['avatar_img']
            # print("Da ton tai user profile cua userId " + str(userId))

        # xu ly specificChildDeparts
        branchParentDepartsData = {}
        if len(specificChildDeparts) > 0:
            childDepartsQs = Department.objects.filter(child_depart__in=specificChildDeparts)
            childDepartsSer = DepartmentSerializer(childDepartsQs, many=True)
            departRows = childDepartsSer.data
            if len(departRows) > 0:
                for departRow in departRows:
                    childDepartStr = departRow.get("childDepart")
                    branchParentDepartsData[childDepartStr] = {
                        "chiNhanh": departRow.get("chiNhanh"),
                        "parentDepart": departRow.get("parentDepart"),
                        "branch": departRow.get("branch")
                    }
            else:
                branchParentDepartsData = None
        else:
            branchParentDepartsData = None

        # lay thong tin features roles cua email nay
        feaRolesData = self.getFeaturesRolesByEmail(email)

        # Tim thong tin employee dua theo email
        queryset = Employee.objects.filter(email=email)
        serializer = EmployeeSerializer(queryset, many=True)
        if len(serializer.data) <= 0:
            # print("Khong tim thay row employee cua email : " + email)
            return response_data({
                "isTinPncEmployee": 0,
                "childDepart": "",
                "parentDepart": "",
                "agency": "",
                "isHO": 0,
                "branch": "",
                "empCode": "",
                "jobTitle": "",
                "empContractType": "",
                "empAvatarImageUrl": AVATAR_DEFAULT['male'],
                "branchParentDeparts": branchParentDepartsData,
                "featuresRoles": feaRolesData
            })

        # CAP NHAT THONG TIN PROFILE TAI DAY
        try:
            employee_serializer = serializer.data[0]
            if is_has_profile:
                # da ton tai profile
                # print("===PROFILE DA TON TAI===")
                current_user_profile = profileQs[0]
                is_save = False
                if empty(current_user_profile.birthday):
                    current_user_profile.birthday = datetime.strptime(employee_serializer["birthday"],
                                                                      "%d/%m/%Y").date()
                    is_save = True
                if empty(current_user_profile.sex):
                    current_user_profile.sex = employee_serializer["sex"]
                    is_save = True
                if empty(current_user_profile.mobile_phone):
                    current_user_profile.mobile_phone = employee_serializer["mobilePhone"]
                    is_save = True
                if empty(current_user_profile.place_of_birth):
                    current_user_profile.place_of_birth = employee_serializer["placeOfBirth"]
                    is_save = True
                if empty(current_user_profile.nationality):
                    current_user_profile.nationality = employee_serializer["nationality"]
                    is_save = True
                if current_user_profile.marital_status is None:
                    current_user_profile.marital_status = employee_serializer["maritalStatus"]
                    is_save = True
                if is_save:
                    current_user_profile.save()
            else:
                # print("===PROFILE MOI===")
                # profile moi
                UserProfile.objects.filter(user_id=userId).update(
                    birthday=datetime.strptime(employee_serializer["birthday"], "%d/%m/%Y").date(),
                    sex=employee_serializer["sex"],
                    mobile_phone=employee_serializer["mobilePhone"],
                    place_of_birth=employee_serializer["placeOfBirth"],
                    nationality=employee_serializer["nationality"],
                    marital_status=employee_serializer["maritalStatus"])
            if is_null_or_empty(link_avatar):
                if employee_serializer["sex"] == "F":
                    link_avatar = AVATAR_DEFAULT['female']
                else:
                    link_avatar = AVATAR_DEFAULT['male']
        except Exception as ex:
            print(f"{datetime.now()} >> cap nhat profile tu employee >> {ex}")

        empData = serializer.data[0]

        # chuan bi data de response
        profileData = {
            "isTinPncEmployee": 1,
            "childDepart": empData["childDepart"],
            "parentDepart": "",
            "isHO": 0,
            "branch": "",
            "empCode": empData["code"],
            "jobTitle": empData["jobTitle"],
            "empContractType": "",
            "empAvatarImageUrl": link_avatar,
            "branchParentDeparts": branchParentDepartsData,
            "featuresRoles": feaRolesData
        }

        emp_con_type = str(empData["contractType"])
        empConTypeToCheck = emp_con_type.lower()
        # print("emp contract type luc dau : " + emp_con_type + " ; luc sau : " + empConTypeToCheck)
        if empConTypeToCheck in app_settings.EMPLOYEE_CONTRACT_TYPES['new']:
            # print("day la nhan vien new")
            profileData['empContractType'] = 'new'
        else:
            # print("day la nhan vien official")
            profileData['empContractType'] = 'official'

        # tim Department dua theo child_depart
        departQs = Department.objects.filter(child_depart=empData["childDepart"])[0:1]
        departSer = DepartmentSerializer(departQs, many=True)
        departArrs = departSer.data
        if len(departArrs) <= 0:
            # print("Khong tim thay department theo code : " + empData["childDepart"])
            return response_data(None, 6, "Depart not found")

        departData = departArrs[0]
        # print("mypt-ho-profile Da tim thay branch cua depart " + empData["childDepart"] + " : " + departData[
        #     "parentDepart"] + " : " +
        #       departData["branch"])
        profileData["parentDepart"] = departData["parentDepart"]
        profileData["branch"] = departData["branch"]
        profileData["agency"] = departData["chiNhanh"] if departData["chiNhanh"] else ""

        if profileData["parentDepart"] == "PNCHO" or profileData["parentDepart"] == "TINHO":
            profileData["isHO"] = 1

        # tim full URL avatar cua employee tu cot avatar_img
        # empAvatarImageUrl = ""
        # empAvatarImg = str(empData["avatarImg"]).strip()
        # # print("empAvatarImg : " + empAvatarImg)
        # if empAvatarImg.lower() == "none":
        #     empAvatarImg = ""
        # if empAvatarImg != "":
        #     # lay link avatar trong bang storage_uuid_data_tb
        #     storageQs = StorageUuidLink.objects.filter(uuid=empAvatarImg)[0:1]
        #     storageSer = StorageUuidLinkSerializer(storageQs, many=True)
        #     storageArr = storageSer.data
        #     if len(storageArr) > 0:
        #         empAvatarImageUrl = storageArr[0].get("link_data", "")
        #
        # profileData["empAvatarImageUrl"] = empAvatarImageUrl
        # print("empAvatarImageUrl cuoi cung : " + empAvatarImageUrl)

        return response_data(profileData)

    def getFeaturesRolesByEmail(self, email):
        email = email.lower()
        query = "SELECT fea_role.role_code, fea_role.feature_code FROM " + FeaturesRolesEmails._meta.db_table + " AS fea_role_email INNER JOIN " + FeaturesRoles._meta.db_table + " AS fea_role ON fea_role_email.role_id = fea_role.role_id WHERE fea_role_email.email = \"" + email + "\" AND fea_role.platform = \"ho\""
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        feaRoles = {}
        for row in rows:
            feaRoles[row[1]] = row[0]
        return feaRoles

    # API nay duoc goi khi vao cac trang web can check permission,
    # API se tra ve cac permission cua user nay, va danh sach tat ca phong ban,
    # kem theo do la profile cua user nay
    def get_profile_and_user_permissions(self, request):

        userData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        userData.pop("clientId")
        userData.pop("grantId")

        allDepartsWithLevels = None
        # Tim trong redis, lay ra data departs trong value cua key : allDepartsWithLevels
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")

        if allDepartsWithLevelsStr is None:
            # print("Khong co Redis allDepartsWithLevels")
            allDepartsWithLevels = None
        else:
            # print("Lay departs tu redis allDepartsWithLevels ne !")
            allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)
            # print(allDepartsWithLevels)

        if allDepartsWithLevels is None:
            # print("Lay departs tu database, sau do luu vao redis allDepartsWithLevels")
            allDepartsWithLevels = self.getAllDepartsWithLevels([])
            # print(allDepartsWithLevels)
            # luu allBranches, allDeparts vao redis
            dataForRedis = {
                "allBranches": allDepartsWithLevels["allBranches"],
                "allDeparts": allDepartsWithLevels["allDeparts"],
                "allChildDeparts": allDepartsWithLevels["allChildDeparts"]
            }
            redisInstance.set("allDepartsWithLevels", str(dataForRedis))

        # khong can do ra
        userData["allBranches"] = allDepartsWithLevels["allBranches"]
        userData["allDeparts"] = allDepartsWithLevels["allDeparts"]
        userData["allChildDeparts"] = allDepartsWithLevels["allChildDeparts"]

        return response_data(userData)

    # API nay chi de goi private. API nay se lay tat ca child depart luu xuong Redis
    def save_all_departs_to_redis(self, request):
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        allDepartsWithLevels = self.getAllDepartsWithLevels([])
        # luu allBranches, allDeparts vao redis
        dataForRedis = {
            "allBranches": allDepartsWithLevels["allBranches"],
            "allDeparts": allDepartsWithLevels["allDeparts"],
            "allChildDeparts": allDepartsWithLevels["allChildDeparts"]
        }
        redisInstance.set("allDepartsWithLevels", str(dataForRedis))

        return response_data({"departsData": dataForRedis})

    # API nay chi de goi private. API nay se tra ve value cua key allDepartsWithLevels tu Redis
    def get_all_departs_levels_from_redis(self, request):
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")
        if allDepartsWithLevelsStr is None:
            return response_data(None, 6, "Khong co redis allDepartsWithLevels")
        else:
            allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)
            return response_data({"departsDataFromRedis": allDepartsWithLevels})

    def getAllDepartsWithLevels(self, specificChildDeparts=[]):
        # chuan bi output : allBranches, allDeparts, allChildDeparts
        allBranches = {
            "PNC": [],
            "TIN": []
        }
        allDeparts = {
            "ALLPNC": {},
            "ALLTIN": {}
        }
        allChildDeparts = []

        specificBranchParentDeparts = {}

        childDepartsQs = Department.objects.order_by(
            F('order').asc(nulls_last=True)).all()
        childDepartsSer = DepartmentSerializer(childDepartsQs, many=True)
        childDepartsRows = childDepartsSer.data
        print(childDepartsRows)

        for childDepartRow in childDepartsRows:
            childDepartStr = childDepartRow.get("childDepart")
            if childDepartStr not in ["ALL", "ALLPNC", "ALLTIN"]:
                branchStr = childDepartRow.get("branch")
                parentDepartStr = childDepartRow.get("parentDepart")
                # chiNhanh = childDepartRow.get("chiNhanh")

                if parentDepartStr not in allBranches[branchStr]:
                    allBranches[branchStr].append(parentDepartStr)
                branchAllStr = "ALL" + branchStr

                # allDepart
                if allDeparts[branchAllStr].get(parentDepartStr, None) is None:
                    allDeparts[branchAllStr][parentDepartStr] = []
                if childDepartStr not in allDeparts[branchAllStr][parentDepartStr]:
                    allDeparts[branchAllStr][parentDepartStr].append(childDepartStr)

                # to chuc specificBranchParentDeparts theo specificChildDeparts
                if len(specificChildDeparts) > 0:
                    if childDepartStr in specificChildDeparts:
                        specificBranchParentDeparts[childDepartStr] = {
                            "parentDepart": parentDepartStr,
                            "branch": branchStr
                        }

        # danh sach phong ban can filter
        child_departs_filter_qs = DepartmentFilter.objects.exclude(
            child_depart__in=["ALL", "ALLTIN", "ALLPNC"]).order_by(
            F('order').asc(nulls_last=True)).all()
        child_departs_filter_ser = DepartmentFilterSerializer(child_departs_filter_qs, many=True)
        child_departs_filter_rows = child_departs_filter_ser.data
        for child_depart_row in child_departs_filter_rows:
            allChildDeparts.append({"childDepart": child_depart_row.get("childDepart"),
                                    "unit": child_depart_row.get("chiNhanh"),
                                    "parentDepart": child_depart_row.get("parentDepart"),
                                    "branch": child_depart_row.get("branch")
                                    })

        if specificBranchParentDeparts == {}:
            specificBranchParentDeparts = None

        return {
            "allBranches": allBranches,
            "allDeparts": allDeparts,
            "allChildDeparts": allChildDeparts,
            "specificBranchParentDeparts": specificBranchParentDeparts
        }

    def get_child_depart(self, request):
        # postData = request.data
        # branch = postData.get('branch')

        data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        branch = data_token.get('branch', '')

        dictChildDepart = []

        try:
            querySet = Department.objects.filter(branch=branch).exclude(child_depart="ALLPNC").exclude(
                child_depart="ALL").exclude(child_depart="ALLTIN")
            serializer = DepartmentSerializer(querySet, many=True)
            list_data = serializer.data

            if len(list_data) > 0:
                for i in list_data:
                    dictChildDepart.append(i.get('childDepart'))
                return response_data(data=dictChildDepart)
        except:
            return response_data(data=None, message="Không có gì hết")

        return response_data(data=None)

    def get_user_profile_by_list_email(self, request):
        data = request.data

        if 'list_email' not in data or not isinstance(data['list_email'], list):
            return response_data(status=6, message='list_email not found')
        list_email = data['list_email']
        user_profiles = UserProfile.objects.filter(email__in=list_email).values(
            'email', 'full_name', 'avatar_img', 'sex')
        dict_response = {}
        for dict_item in user_profiles:
            avata_img = dict_item['avatar_img']
            sex = dict_item['sex']
            dict_response.update({
                dict_item['email'].lower(): {
                    "sex": sex,
                    "fullName": dict_item['full_name'],
                    "avatarImg": avata_img if avata_img
                    else (AVATAR_DEFAULT['female'] if sex == 'F' else AVATAR_DEFAULT['male']),
                }
            })

        return response_data(data=dict_response)

    def get_list_email_by_list_child_depart(self, request):
        data = request.data

        if 'list_child_depart' not in data or not isinstance(data['list_child_depart'], list):
            return response_data(status=6, message='List child depart not found', data=[])
        list_child_depart = data['list_child_depart']
        lst_email = Employee.objects.filter(child_depart__in=list_child_depart).values_list('email', flat=True)

        return response_data(data=lst_email)

    def get_email_from_code_or_name(self, request):
        data = request.data
        emails = []

        if 'code' in data and data['code']:
            emails = Employee.objects.filter(emp_code=data['code']).values_list('email', flat=True)

        if 'name' in data and data['name']:
            emails = Employee.objects.filter(emp_name__icontains=data['name']).values_list('email', flat=True)

        return response_data(data={"emails": emails})

    # API nay chi de goi private. Dau tien la do mypt-ho-auth-api goi
    def get_feature_roles_by_codes(self, request):
        # xu ly param feaRolesCodes
        feaRolesCodes = request.data.get("feaRolesCodes", None)
        # Neu ko co param feaRolesCodes, stop API nay
        if feaRolesCodes is None:
            return response_data(None, 5, "No any feature role codes!")

        feaRolesData = []
        if feaRolesCodes is not None:
            for feaCode, roleCode in feaRolesCodes.items():
                # check co ton tai feaCode & roleCode nay trong bang features_roles hay ko
                feaRoleQs = FeaturesRoles.objects.filter(feature_code=feaCode, role_code=roleCode, platform="ho")
                if not feaRoleQs.exists():
                    return response_data(None, 6,
                                         "Role " + roleCode + " of the feature " + feaCode + " does not exist!")
                feaRoleSerializer = FeaturesRolesSerializer(feaRoleQs, many=True)
                feaRoleItem = feaRoleSerializer.data[0]
                feaRolesData.append({
                    "roleId": feaRoleItem["role_id"],
                    "roleCode": feaRoleItem["role_code"],
                    "feaCode": feaRoleItem["feature_code"]
                })

        return response_data({"feaRolesData": feaRolesData})

    # API nay chi de goi private. Dau tien la do mypt-ho-auth-api goi
    def check_email_has_feature_roles_by_codes(self, request):
        # Check co param email hay ko
        emailStr = request.data.get("email", "")
        if emailStr == "":
            return response_data(None, 5, "No email address!")

        # xu ly param feaRolesCodes
        feaRolesCodes = request.data.get("feaRolesCodes", None)
        # Neu ko co param feaRolesCodes, stop API nay
        if feaRolesCodes is None:
            return response_data(None, 5, "No any feature role codes!")

        feaRolesData = []
        if feaRolesCodes is not None:
            for feaCode, roleCode in feaRolesCodes.items():
                # check co ton tai feaCode & roleCode nay trong bang features_roles hay ko
                feaRoleQs = FeaturesRoles.objects.filter(feature_code=feaCode, role_code=roleCode)
                if not feaRoleQs.exists():
                    return response_data(None, 6,
                                         "Role " + roleCode + " of the feature " + feaCode + " does not exist!")
                feaRoleSerializer = FeaturesRolesSerializer(feaRoleQs, many=True)
                feaRoleItem = feaRoleSerializer.data[0]
                feaRolesData.append({
                    "roleId": feaRoleItem["role_id"],
                    "roleCode": feaRoleItem["role_code"],
                    "feaCode": feaRoleItem["feature_code"]
                })

        if len(feaRolesData) <= 0:
            return response_data(None, 6, "No any feature roles!")

        rolesAssigned = []
        rolesAssignedAlready = []

        for feaRoleIt in feaRolesData:
            roleEmailQs = FeaturesRolesEmails.objects.filter(email=emailStr, role_id=feaRoleIt["roleId"])
            if not roleEmailQs.exists():
                print(
                    "Email " + emailStr + " is NOT assigned with role " + str(feaRoleIt["roleId"]) + " - " + feaRoleIt[
                        "roleCode"] + " so now will assign!")
                roleEmailRecord = FeaturesRolesEmails(email=emailStr, role_id=feaRoleIt["roleId"],
                                                      role_code=feaRoleIt["roleCode"],
                                                      feature_code=feaRoleIt["feaCode"])
                roleEmailRecord.save()
                rolesAssigned.append(feaRoleIt)
            else:
                print("Email " + emailStr + " is assigned with role " + str(feaRoleIt["roleId"]) + " - " + feaRoleIt[
                    "roleCode"] + " already!")
                rolesAssignedAlready.append(feaRoleIt)

        return response_data({
            "rolesAssigned": rolesAssigned,
            "rolesAssignedAlready": rolesAssignedAlready
        })

    def update_email_for_employee(self, request):
        try:
            result_success = []
            result_fail = []
            getDataExcel = request.FILES['file_xlsx']

            dataExcel = pd.read_excel(getDataExcel, dtype={'Mã nhân viên': str})

            # fill những ô trống thành null
            dataExcel = dataExcel.replace(np.NaN, None)

            # Thay đổi tên các key cần đổi tên
            dataExcel = dataExcel.rename(columns={'Mã nhân viên': 'empCode', 'Họ và tên': 'fullName',
                                                  'Email mới': 'emailNew'})
            data = dataExcel.to_dict(orient='records')

            # cho vào transaction để tránh thao tác sai dữ liệu
            with transaction.atomic():
                for obj in data:
                    email_old = None
                    email_new = obj['emailNew']
                    emp_code = obj['empCode']

                    try:
                        # lấy thông tin nhân sự hiện tại
                        queryset = Employee.objects.get(emp_code=emp_code)
                        old_email = queryset.email

                        # cập nhật thông tin mới cho nhân sự
                        Employee.objects.filter(emp_code=emp_code).update(email=email_new)
                        FeaturesRolesEmails.objects.filter(email=email_old).update(email=email_new)
                        result_success.append(obj)
                    except ObjectDoesNotExist:
                        result_fail.append(obj)
                        continue
                count_success = len(result_success)
                count_fail = len(result_fail)
                result = {
                    'lenList': count_success + count_fail,
                    'countSuccess': count_success,
                    'countFail': count_fail,
                    'success': result_success,
                    'fail': result_fail
                }
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_email_for_employee.__name__, ex))
            return response_data(None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return response_data(result)

    def update_department_for_employee(self, request):
        try:
            result_update = []
            result_fail = []
            getData = request.FILES['file_xlsx']
            dataExcel = pd.read_excel(getData, dtype={'Mã nhân viên': str})

            # fill những ô trống thành null
            dataExcel = dataExcel.replace(np.NaN, None)

            # Thay đổi tên các key cần đổi tên
            dataExcel = dataExcel.rename(columns={'Mã nhân viên': 'empCode', 'Họ và tên': 'fullName',
                                                  'Email': 'email', 'Chi nhánh': 'chiNhanh', 'Vùng': 'parentDepart',
                                                  'Bộ phận': 'childDepart'})
            data = dataExcel.to_dict(orient='records')

            # cho vào transaction để tránh thao tác sai dữ liệu
            with transaction.atomic():
                for obj in data:
                    if obj['empCode'] != 8:
                        obj['empCode'] = str(obj['empCode']).zfill(8)
                    data = Employee.objects.filter(emp_code=obj['empCode'])
                    if data:
                        data.update(child_depart=obj['childDepart'], update_time=get_str_datetime_now_import_db())
                        result_update.append(obj)
                    else:
                        result_fail.append(obj)

                count_update = len(result_update)
                count_fail = len(result_fail)
                result = {
                    'lenList': count_update,
                    'countUpdate': count_update,
                    'countFail': count_fail,
                    'update': result_update,
                    'fail': result_fail
                }

                # chỉ chạy những đoạn này trên local
                if project_settings.APP_ENVIRONMENT == 'local':
                    path = "C:/Users/" + os.getlogin() + "/Downloads"
                    isExist = os.path.exists(path)
                    if not isExist:
                        os.makedirs(path)
                    if count_fail != 0:
                        df = pd.DataFrame(result_fail)
                        df.to_excel(path + "/" + 'Airlines.xlsx')
        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_department_for_employee.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(result)
