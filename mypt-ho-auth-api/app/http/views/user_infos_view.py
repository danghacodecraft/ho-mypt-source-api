# Models
from ..models.employee import *
from ..models.user_infos import *
from ..models.user_right_checkin import *
from ..models.ho_user_permission import *
from ..models.mypt_user_permission import *
from ..models.department import *
# Serializers
from ..serializers.employee_serializer import *
from ..serializers.user_infos_serializer import *
from ..serializers.user_right_checkin_serializer import *
from ..serializers.ho_user_permission_serializer import *
from ..serializers.mypt_user_permission_serializer import *
from ..serializers.department_serializer import *
# Helpers
from ...core.helpers.response import *
# Rest Framework
from rest_framework.viewsets import ViewSet
# Django
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
# Utilities
import re
from django.conf import settings as project_settings
from django.db import IntegrityError, transaction
# entities
from ..entities.global_data import *
# Others Views
from .permission_tools_view import *


class UserInfosView(ViewSet):
    # Functions
    def getAllDepartsLevelsFromRedis(self):
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED
                                          , password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        return ast.literal_eval(redisInstance.get("allDepartsWithLevels"))

    def getParentDepart(self, childDepart):
        departmentQueryset = Department.objects.filter(child_depart=childDepart)
        departmentSerializer = DepartmentSerializer(departmentQueryset, many=True)
        if len(departmentSerializer.data) == 0:
            return None
        return departmentSerializer.data[0]['parentDepart']

    def mapChildDepartFromEmailFormat(self, emailFormat):
        if emailFormat == '@fpt.net':
            return 'ALLPNC'
        elif emailFormat == '@vienthongtin.com':
            return 'ALLTIN'
        elif emailFormat == '@fpt.com.vn':
            return 'ALL'
        return ''

    def mapPermissionToWebHO(self, right):
        hoPermission = {
            "0": [
                {
                    "permissionId": 1,
                    "permissionCode": "ALL"
                }
            ],
            "1": [
                {
                    "permissionId": 5,
                    "permissionCode": "QUAN_LY_DIEM_DANH_SHOW"
                }
            ],
            "2": [
                {
                    "permissionId": 5,
                    "permissionCode": "QUAN_LY_DIEM_DANH_SHOW"
                },
                {
                    "permissionId": 6,
                    "permissionCode": "QUAN_LY_DIEM_DANH_EDIT"
                }
            ],
            "3": [
                {
                    "permissionId": 29,
                    "permissionCode": "KIEM_SOAT_CHE_TAI_SHOW"
                },
                {
                    "permissionId": 31,
                    "permissionCode": "KIEM_SOAT_CHE_TAI_IMPORT"
                }
            ],
            "4": [
                {
                    "permissionId": 29,
                    "permissionCode": "KIEM_SOAT_CHE_TAI_SHOW"
                },
                {
                    "permissionId": 30,
                    "permissionCode": "KIEM_SOAT_CHE_TAI_EDIT"
                },
                {
                    "permissionId": 31,
                    "permissionCode": "KIEM_SOAT_CHE_TAI_IMPORT"
                }
            ],
            "5": [
                {
                    "permissionId": 9,
                    "permissionCode": "QUAN_LY_NHAN_VIEN_SHOW"
                }
            ],
            "6": [
                {
                    "permissionId": 9,
                    "permissionCode": "QUAN_LY_NHAN_VIEN_SHOW"
                },
                {
                    "permissionId": 10,
                    "permissionCode": "QUAN_LY_NHAN_VIEN_EDIT"
                }
            ],
            "7": [
                {
                    "permissionId": 15,
                    "permissionCode": "QUAN_LY_LUONG_SHOW"
                }
            ],
            "8": [
                {
                    "permissionId": 15,
                    "permissionCode": "QUAN_LY_LUONG_SHOW"
                },
                {
                    "permissionId": 16,
                    "permissionCode": "QUAN_LY_LUONG_EDIT",
                }
            ],
            "9": None,
            "10": [
                {
                    "permissionId": 23,
                    "permissionCode": "QUAN_LY_THU_VIEN"
                }
            ],
            "11": [
                {
                    "permissionId": 20,
                    "permissionCode": "RECRUIT_QUAN_LY_UNG_VIEN"
                },
                {
                    "permissionId": 21,
                    "permissionCode": "RECRUIT_DANH_GIA_UNG_VIEN"
                }
            ],
            "12": None,
            "13": [
                {
                    "permissionId": 17,
                    "permissionCode": "QUAN_LY_THE_ATLD_SHOW"
                },
                {
                    "permissionId": 18,
                    "permissionCode": "QUAN_LY_THE_ATLD_EDIT"
                },
                {
                    "permissionId": 28,
                    "permissionCode": "QUAN_LY_THE_ATLD_IMPORT"
                }
            ],
            "14": None,
            "15": [
                {
                    "permissionId": 24,
                    "permissionCode": "GAME"
                }
            ],
            "16": None,
            "17": None,
            "18": None,
            "19": [
                {
                    "permissionId": 2,
                    "permissionCode": "HO_TRO_KY_THUAT"
                }
            ],
            "20": [
                {
                    "permissionId": 4,
                    "permissionCode": "QUAN_LY_CCDC"
                }
            ],
            "21": [
                {
                    "permissionId": 11,
                    "permissionCode": "XEP_HANG_NHAN_VIEN_SHOW"
                },
                {
                    "permissionId": 12,
                    "permissionCode": "XEP_HANG_NHAN_VIEN_EDIT"
                }
            ],
            "22": None,
            "23": None,
            "24": None,
            "-1": None,
            "2a": [
                {
                    "permissionId": 5,
                    "permissionCode": "QUAN_LY_DIEM_DANH_SHOW"
                },
                {
                    "permissionId": 6,
                    "permissionCode": "QUAN_LY_DIEM_DANH_EDIT"
                }
            ]
        }
        return hoPermission[right]

    def mapEmailToUserID(self):
        userInfosQueryset = UserInfos.objects.all()
        userInfosSerializer = UserInfosSerializerForMyPT(userInfosQueryset, many=True)
        usersInformation = {}
        for userInfo in userInfosSerializer.data:
            usersInformation[userInfo['email']] = userInfo['userId']
        return usersInformation

    # apis
    def saveEmployee(self, request):
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # 1 - Save employee from mypt_employee to auth_user_infos
        queryset = Employee.objects.filter(status_working=1).order_by('email')
        serializer = EmployeeSerializer(queryset, many=True)
        try:
            with transaction.atomic():
                for item in serializer.data:
                    employee = UserInfos.objects.filter(email=item['email'])
                    if not employee.exists():
                        # Validate mail is valid
                        if not re.fullmatch(validateMailRegex, item['email']):
                            continue
                        newEmployee = UserInfos(email=item['email'].lower(),
                                                full_name=item['empName'])
                        newEmployee.save()
        except IntegrityError as e:
            print(e)
            return response_data("", statusCode=4, message="Error when save employee from mypt_employee "
                                                           "to auth_user_infos")
        # 2 - Save employee from mypt_user_right_checkin to mypt_auth_user_infos
        userRightCheckin = {}  # Save for add permission to mypt_ho_auth_user_permission
        queryset = UserRightCheckin.objects.all()
        serializer = UserRightCheckinSerializer(queryset, many=True)
        try:
            with transaction.atomic():
                for item in serializer.data:
                    userRightCheckin[item['email']] = item
                    employee = UserInfos.objects.filter(email=item['email'])

                    if not employee.exists():
                        # Validate mail is valid
                        if not re.fullmatch(validateMailRegex, item['email']):
                            continue
                        userEmail = item['email'].lower()
                        cutPosition = userEmail.find("@")
                        userName = userEmail[:cutPosition]
                        newEmployee = UserInfos(email=userEmail,
                                                full_name=userName)
        except IntegrityError as e:
            print(e)
            return response_data("", statusCode=4, message="Error when save employee from mypt_employee "
                                                           "to auth_user_infos")

        global_data.userRightCheckins = userRightCheckin
        return response_data('')

    def addAllPermissionsWebHO(self, request):
        # Add permission from mypt_auth_user_infos to mypt_ho_auth_user_permission
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        noChildDepartPermissions = ['HO_TRO_KY_THUAT', 'QUAN_LY_NGAY_CONG_SHOW', 'QUAN_LY_NGAY_CONG_EDIT',
                                    'RECRUIT_QUAN_LY_UNG_VIEN',
                                    'RECRUIT_DANH_GIA_UNG_VIEN', 'POWER_BI', 'GAME', 'PHAN_QUYEN_HO_MYPT',
                                    'PHAN_QUYEN_APP_MYPT',
                                    'QUAN_LY_NHAN_VIEN_IMPORT', 'QUAN_LY_THE_ATLD_IMPORT', 'KIEM_SOAT_CHE_TAI_EDIT',
                                    'KIEM_SOAT_CHE_TAI_IMPORT']
        userRightCheckin = {}  # Save for add permission to mypt_ho_auth_user_permission
        queryset = UserRightCheckin.objects.all()
        serializer = UserRightCheckinSerializer(queryset, many=True)

        for item in serializer.data:
            userRightCheckin[item['email']] = item

        queryset = UserInfos.objects.all()
        userInfoSerializer = UserInfosSerializer(queryset, many=True)

        for item in userInfoSerializer.data:
            if userRightCheckin.get(item['email'], None) is not None:
                userID = item['user_id']
                user = userRightCheckin[item['email']]
                listPermissions = user['perId'].split(',') if user['perId'] != '' else []
                # Validate mail is valid
                if not re.fullmatch(validateMailRegex, item['email']):
                    continue
                if len(listPermissions) > 0:
                    for right in listPermissions:
                        listHORight = self.mapPermissionToWebHO(right)

                        if listHORight is not None:
                            for hoRight in listHORight:
                                userPermission = HoUserPermission.objects.filter(user_id=userID,
                                                                                 permission_id=hoRight['permissionId'])
                                if not userPermission.exists():
                                    childDepartRight = user['childDepartRight']
                                    if hoRight.get('permissionCode', None) in noChildDepartPermissions:
                                        childDepartRight = ''
                                    elif childDepartRight is None or childDepartRight == '':
                                        userEmail = item['email']
                                        cutPosition = userEmail.find("@")
                                        emailFormat = userEmail[cutPosition:]
                                        childDepartRight = self.mapChildDepartFromEmailFormat(emailFormat)

                                    newUserPermission = HoUserPermission(user_id=userID,
                                                                         permission_id=hoRight['permissionId'],
                                                                         permission_code=hoRight['permissionCode'],
                                                                         child_depart=childDepartRight)
                                    try:
                                        newUserPermission.save()
                                    except Exception as e:
                                        print(e)
        return response_data('')

    def addAllPermissionsAppMyPT(self, request):
        page = request.data.get("page", None)
        if page is None:
            return response_data("", statusCode=4, message="Page mustn't be None !")

        employeeRecords = Employee.objects.filter(status_working=1).count()
        limit = 1
        while 500 * limit < employeeRecords:
            limit = limit + 1

        if page > limit:
            return response_data("", statusCode=4, message=f"Page must be less than {limit} !")

        LIST_PARENT_DEPART_TICKET_RIGHT = ["PNCV4", "PNCV5", "PNCV6", "PNCV7", "TINV1", "TINV2", "TINV3", "TINV4"]
        LIST_JOB_TITLE_TICKET_RIGHT = ['cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh', "cb xử lý sự cố"]
        LIST_JOB_TITLE_CHECKIN_RIGHT = ['cb kỹ thuật tkbt', 'cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh', 'cb xử lý sự cố']
        LIST_CONTRACT_CHECKIN_RIGHT = ['hợp đồng đào tạo nghề', 'hợp đồng thử việc', "hđ đào tạo nghề", "hđ thử việc"]

        startPosition = (page - 1) * 500
        endPosition = startPosition + 500

        if endPosition > employeeRecords:
            endPosition = employeeRecords

        employeeQueryset = Employee.objects.filter(status_working=1).order_by('email')[startPosition:endPosition]
        employeeSerializer = EmployeeSerializer(employeeQueryset, many=True)
        userInfosDict = self.mapEmailToUserID()

        for employee in employeeSerializer.data:
            employeeEmail = employee.get('email', None).lower()
            employeeId = userInfosDict.get(employeeEmail, None)
            employeeJobTitle = employee.get('jobTitle', None)
            employeeContractType = employee.get('contractType', None)
            employeeChildDepart = employee.get('childDepart', None)
            employeeParentDepart = self.getParentDepart(employeeChildDepart)

            if employeeJobTitle is not None:
                employeeJobTitle = employeeJobTitle.lower()
            if employeeContractType is not None:
                employeeContractType = employeeContractType.lower()

            # add cac quyen HTKT
            if employeeJobTitle in LIST_JOB_TITLE_TICKET_RIGHT or employeeChildDepart == "PSO" or employeeParentDepart in LIST_PARENT_DEPART_TICKET_RIGHT:
                newUserPermission1 = MyPTUserPermission(user_id=employeeId,
                                                        permission_id=4,
                                                        permission_code='XEM_TICKET_HTKT_CUA_TOI',
                                                        child_depart='')

                try:
                    newUserPermission1.save()
                except Exception as e:
                    print(e)

                newUserPermission2 = MyPTUserPermission(user_id=employeeId,
                                                        permission_id=9,
                                                        permission_code='TAO_TICKET_HTKT',
                                                        child_depart='')

                try:
                    newUserPermission2.save()
                except Exception as e:
                    print(e)

                newUserPermission3 = MyPTUserPermission(user_id=employeeId,
                                                        permission_id=10,
                                                        permission_code='DANH_GIA_TICKET_HTKT',
                                                        child_depart='')

                try:
                    newUserPermission3.save()
                except Exception as e:
                    print(e)


            # add cac quyen Diem danh
            if employeeJobTitle in LIST_JOB_TITLE_CHECKIN_RIGHT or employeeContractType in LIST_CONTRACT_CHECKIN_RIGHT:
                newUserPermission4 = MyPTUserPermission(user_id=employeeId,
                                                        permission_id=2,
                                                        permission_code='THUC_HIEN_DIEM_DANH',
                                                        child_depart='')

                try:
                    newUserPermission4.save()
                except Exception as e:
                    print(e)


                newUserPermission5 = MyPTUserPermission(user_id=employeeId,
                                                        permission_id=3,
                                                        permission_code='XEM_LICH_SU_DIEM_DANH',
                                                        child_depart='')

                try:
                    newUserPermission5.save()
                except Exception as e:
                    print(e)

        return response_data(None, 1, "Added success!")
