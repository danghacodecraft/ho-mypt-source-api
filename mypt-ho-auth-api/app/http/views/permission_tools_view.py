# Models
from ..models.ho_permission import *
from ..models.ho_permission_group import *
from ..models.ho_permission_with_route import *
from ..models.user_infos import *
from ..models.ho_user_permission import *
from ..models.mypt_user_permission import *
from ..models.mypt_permission import *
from ..models.mypt_permission_group import *
from ..models.emails_prepare_add_pers_fea_roles import *
from ..models.features_roles import *
from ..models.features_roles_emails import *
# Serializers
from ..serializers.ho_permission_serializer import *
from ..serializers.ho_permission_group_serializer import *
from ..serializers.ho_permission_with_route_serializer import *
from ..serializers.user_infos_serializer import *
from ..serializers.ho_user_permission_serializer import *
from ..serializers.mypt_user_permission_serializer import *
from ..serializers.mypt_permission_serializer import *
from ..serializers.mypt_permission_group_serializer import *
from ..serializers.emails_prepare_add_pers_fea_roles_serializer import *
from ..serializers.features_roles_serializer import *
from ..serializers.features_roles_emails_serializer import *
# Helpers
from ...core.helpers.response import *
from ..entities import global_data
# Rest Framework
from rest_framework.viewsets import ViewSet
# Utilities
import re
import ast
import redis
from django.conf import settings as project_settings
from django.db import IntegrityError, transaction
from datetime import datetime


class HoPermissionToolsView(ViewSet):
    # Functions
    def getAllDepartsLevelsFromRedis(self):
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        return redisInstance.get("allDepartsWithLevels")

    def mapAllChildDepart(self, allDeparts):
        departs = {}
        for item in allDeparts:  # item = "ALLPNC", "ALLTIN"
            for parent in allDeparts[item]:
                for child in allDeparts[item][parent]:
                    childDepart = {
                        "branch": item,
                        "parent": parent
                    }
                    departs[child] = childDepart

        departs["ALL"] = {
            "branch": "ALL"
        }

        departs["ALLTIN"] = {
            "branch": "ALLTIN"
        }

        departs["ALLPNC"] = {
            "branch": "ALLPNC"
        }

        return departs

    def validateChildDeparts(self, childDeparts, hasDepartRight):
        # 1. True
        # 2. Child depart is not in allDepartsWithLevels
        # 3. Child departs have parent depart and child depart at the same time
        allDepartsWithLevels = ast.literal_eval(self.getAllDepartsLevelsFromRedis())
        allChildDeparts = self.mapAllChildDepart(allDepartsWithLevels['allDeparts'])

        hasALL = True if 'ALL' in childDeparts else False
        hasALLTIN = True if 'ALLTIN' in childDeparts else False
        hasALLPNC = True if 'ALLPNC' in childDeparts else False

        if len(childDeparts) == 1 and childDeparts[0] == '':  # child_depart = 0
            if hasDepartRight == 0:
                return 1, "True"
            else:
                return 2, "has_depart_right = 1 so child_depart cannot be empty !"

        for depart in childDeparts:
            validChildDepart = allChildDeparts.get(depart, None)
            if validChildDepart is None:
                return 2, "Child depart is not in allDepartsWithLevels"
            elif hasALL and len(childDeparts) != 1:
                return 3, "Child departs have parent depart and child depart at the same time"
            elif hasALLTIN and hasALLPNC and len(childDeparts) != 2:
                return 3, "Child departs have parent depart and child depart at the same time"
            elif hasALLTIN and not hasALLPNC:
                if depart == 'ALLTIN':
                    continue
                elif validChildDepart['branch'] == 'ALLTIN':
                    return 3, "Child departs have parent depart and child depart at the same time"
            elif hasALLPNC and not hasALLTIN:
                if depart == 'ALLPNC':
                    continue
                elif validChildDepart['branch'] == 'ALLPNC':
                    return 3, "Child departs have parent depart and child depart at the same time"

        return 1, "True"

    def validatePermission(self, permissionCode):
        permissionQueryset = HoPermission.objects.filter(is_deleted=False, permission_code=permissionCode)
        if not permissionQueryset.exists():
            return False
        return True

    def validatePermissionMyPT(self, permissionCode):
        permissionQueryset = MyPTPermission.objects.filter(is_deleted=False, permission_code=permissionCode)
        if not permissionQueryset.exists():
            return False
        return True

    # apis
    def getAllPermissionsHO(self, request):
        # Groups permissions
        queryset = HoPermissionGroup.objects.filter(is_deleted=False).all()
        serializer = HoPermissionGroupSerializer(queryset, many=True)
        permissionsGroup = {item['permission_group_id']: item['permission_group_code'] for item in serializer.data if
                            item['is_deleted'] == 0}
        # Permissions
        queryset = HoPermission.objects.filter(is_deleted=False).all()
        serializer = HoPermissionSerializer(queryset, many=True)

        permissions = []

        if serializer.data:
            for item in serializer.data:
                permissionsGroupCode = permissionsGroup.get(item['permission_group_id'])
                permissionsDict = {
                    'permissionName': item['permission_name'],
                    'permissionCode': item['permission_code'],
                    'permissionGroupCode': permissionsGroupCode
                }
                permissions.append(permissionsDict)

        return response_data(permissions)

    def getAllPermissionGroupsHO(self, request):
        # Groups permissions
        queryset = HoPermissionGroup.objects.filter(is_deleted=False).all()
        serializer = HoPermissionGroupSerializer(queryset, many=True)
        permissionGroups = []

        for item in serializer.data:
            if item['is_deleted'] == 0:
                groupPermissionDict = {
                    "permissionGroupName": item['permission_group_name'],
                    "permissionGroupCode": item['permission_group_code']
                }
                permissionGroups.append(groupPermissionDict)

        return response_data(permissionGroups)

    def getPermissionsByGroupCodeHO(self, request):
        permissionGroupCode = request.data.get("permissionGroupCode", None)
        if permissionGroupCode is None:
            return response_data(None, 5, "Permission group code is \'None\' ! ")

        permissionGroupQueryset = HoPermissionGroup.objects.filter(permission_group_code=permissionGroupCode)
        if not permissionGroupQueryset.exists():
            return response_data(None, 6, f'Not found permission group code \'{permissionGroupCode}\'! ')

        permissionGroupSerializer = HoPermissionGroupSerializer(permissionGroupQueryset, many=True)
        permissionGroupId = permissionGroupSerializer.data[0]['permission_group_id']

        permissionQueryset = HoPermission.objects.filter(permission_group_id=permissionGroupId, is_deleted=False)
        if not permissionQueryset.exists():
            return response_data(None, 6, f'Not found permission group code \'{permissionGroupCode}\'! ')

        permissionSerializer = HoPermissionSerializer(permissionQueryset, many=True)
        permissions = []

        for item in permissionSerializer.data:
            permission = {
                "permissionName": item['permission_name'],
                "permissionCode": item['permission_code'],
                "hasDepartRight": item['has_depart_right']
            }
            permissions.append(permission)

        return response_data(permissions)

    def getAllowedAssignPermissionsWebHo(self, request):
        authUserSession = global_data.authUserSessionData
        authUserId = authUserSession.get('userId', None)
        allowedPermissions = []

        if authUserId is None:
            return response_data(None, 5, "Auth user session is None !")

        userPermissionQueryset = HoUserPermission.objects.filter(user_id=authUserId)
        if not userPermissionQueryset.exists():
            return response_data(None, 6, f'User \'{authUserSession["email"]}\' not found permission !')

        userPermissionSerializer = HoUserPermissionSerializer(userPermissionQueryset, many=True)
        hoPermissionQueryset = HoPermission.objects.filter(is_deleted=False)
        hoPermissionSerializer = HoPermissionSerializer(hoPermissionQueryset, many=True)

        # If user has permission ALL then print all permissions in mypt_ho_auth_permission tb
        if userPermissionSerializer.data[0]['permissionCode'] == 'ALL':
            for item in hoPermissionSerializer.data:
                permission = {
                    "permissionName": item['permission_name'],
                    "permissionCode": item['permission_code'],
                    "hasDepartRight": item['has_depart_right']
                }
                allowedPermissions.append(permission)

        # If user is a person who can assign permissions for staff
        elif next((item for item in userPermissionSerializer.data if item["permissionCode"] == "PHAN_QUYEN_HO_MYPT"),
                  None):
            hoPermissions = {item['permission_code']:
                                 {"permissionName": item['permission_name'],
                                  "permissionCode": item['permission_code'],
                                  "hasDepartRight": item['has_depart_right']} for item in hoPermissionSerializer.data}
            for item in userPermissionSerializer.data:
                if item['permissionCode'] == "PHAN_QUYEN_HO_MYPT":
                    continue
                allowedPermissions.append(hoPermissions[item['permissionCode']])

        return response_data(allowedPermissions)

    def getLoggedInUserPermissionsHO(self, request):
        authUserSession = global_data.authUserSessionData
        authUserId = authUserSession.get('userId', None)

        if authUserId is None:
            return response_data(None, 5, "Auth user session is None !")

        userPermissionQueryset = HoUserPermission.objects.filter(user_id=authUserId)
        if not userPermissionQueryset.exists():
            return response_data(None, 6, f'User \'{authUserSession["email"]}\' not found permission !')

        userPermissionSerializer = HoUserPermissionSerializer(userPermissionQueryset, many=True)

        userPermissions = []
        for item in userPermissionSerializer.data:
            permission = {
                "permissionCode": item['permission_code'],
                "childDepart": item['childDepart'].split(",")
            }
            userPermissions.append(permission)

        return response_data(userPermissions)

    def addUserPermissionsByEmailHO(self, request):
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        userEmail = request.data.get("email", None)
        permissions = request.data.get("permissions", None)
        # Check input
        if userEmail is None or permissions is None or len(permissions) == 0 or not re.fullmatch(validateMailRegex,
                                                                                                 userEmail):
            return response_data(None, 5, "Invalid input !")
        # Add user permission transaction
        try:
            with transaction.atomic():
                # Find user in mypt_auth_user_infos. If not found, add user to mypt_auth_user_infos
                userInfoQueryset = UserInfos.objects.filter(email=userEmail)
                if not userInfoQueryset.exists():
                    cutPosition = userEmail.find("@")
                    userName = userEmail[:cutPosition]
                    newUser = UserInfos(email=userEmail.lower(),
                                        full_name=userName)
                    newUser.save()
                # Create new user permission
                userInfoQueryset = UserInfos.objects.filter(email=userEmail)
                userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
                userId = userInfoSerializer.data[0]['user_id']

                for permission in permissions:
                    # Validate permission
                    isValidPermission = self.validatePermission(permission['permissionsCode'])
                    if not isValidPermission:
                        transaction.set_rollback(True)  # Roll back
                        return response_data(None, statusCode=5,
                                             message=f"Permission code {permission['permissionsCode']} isn't in mypt_ho_auth_permission")

                    # Validate child depart
                    permissionQueryset = HoPermission.objects.filter(permission_code=permission['permissionsCode'])
                    permissionSerializer = HoPermissionSerializer(permissionQueryset, many=True)

                    hasDepartRight = permissionSerializer.data[0]['has_depart_right']
                    if hasDepartRight == 0:
                        listChildDepart = ['']
                        childDepart = ""
                    else:
                        listChildDepart = [item.strip() for item in permission['childDeparts'].split(',')]
                        childDepart = ",".join(listChildDepart)

                    isValidChildDepart, errorMessage = self.validateChildDeparts(listChildDepart, hasDepartRight)
                    if isValidChildDepart != 1:
                        transaction.set_rollback(True)  # Roll back
                        return response_data(None, statusCode=5, message=errorMessage)

                    # Add user permission
                    permissionId = permissionSerializer.data[0]['permissionId']
                    HoUserPermission.objects.update_or_create(
                        user_id=userId,
                        permission_id=permissionId,
                        permission_code=permission['permissionsCode'],
                        defaults={"child_depart": childDepart}
                    )
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4, message="Error when save user permission to "
                                                             "auth_user_permissions")

        return response_data(None)

    def addUserPermissionsByEmailAppMyPT(self, request):
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        userEmail = request.data.get("email", None)
        permissions = request.data.get("permissions", None)
        # Check input
        if userEmail is None or permissions is None or len(permissions) == 0 or not re.fullmatch(validateMailRegex,
                                                                                                 userEmail):
            return response_data(None, 5, "Invalid input !")
        # Add user permission transaction
        try:
            with transaction.atomic():
                # Find user in mypt_auth_user_infos. If not found, add user to mypt_auth_user_infos
                userInfoQueryset = UserInfos.objects.filter(email=userEmail)
                if not userInfoQueryset.exists():
                    cutPosition = userEmail.find("@")
                    userName = userEmail[:cutPosition]
                    newUser = UserInfos(email=userEmail.lower(),
                                        full_name=userName)
                    newUser.save()
                # Create new user permission
                userInfoQueryset = UserInfos.objects.filter(email=userEmail)
                userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
                userId = userInfoSerializer.data[0]['user_id']

                for permission in permissions:
                    # Validate permission
                    isValidPermission = self.validatePermissionMyPT(permission['permissionsCode'])
                    if not isValidPermission:
                        transaction.set_rollback(True)  # Roll back
                        return response_data(None, statusCode=5,
                                             message=f"Permission code {permission['permissionsCode']} isn't in mypt_auth_permission")

                    # Validate child depart
                    permissionQueryset = MyPTPermission.objects.filter(permission_code=permission['permissionsCode'])
                    permissionSerializer = MyPTPermissionSerializer(permissionQueryset, many=True)

                    childDepart = ""
                    # Add user permission
                    permissionId = permissionSerializer.data[0]['permissionId']
                    MyPTUserPermission.objects.update_or_create(
                        user_id=userId,
                        permission_id=permissionId,
                        permission_code=permission['permissionsCode'],
                        defaults={"child_depart": childDepart}
                    )
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4, message="Error when save user permission to "
                                                             "auth_user_permissions")

        return response_data(None)

    def updateOneChildDepartUserPermissionHO(self, request):
        userId = request.data.get("userId", None)
        permissionId = request.data.get("permissionId", None)
        childDeparts = request.data.get("childDeparts", None)
        userPermissionRecord = HoUserPermission.objects.filter(user_id=userId, permission_id=permissionId)
        if not userPermissionRecord.exists():
            return response_data(None, statusCode=5, message="Not found user permission !")
        try:
            with transaction.atomic():
                userPermissionRecord.update(child_depart=childDeparts)
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4, message="Error when update child_depart in user permission")

        return response_data(None)

    def deleteOneUserPermissionHO(self, request):
        userId = request.data.get("userId", None)
        permissionId = request.data.get("permissionId", None)
        try:
            with transaction.atomic():
                # Find user permissions
                userPermissionRecord = HoUserPermission.objects.filter(user_id=userId, permission_id=permissionId)
                if not userPermissionRecord.exists():
                    return response_data(None, statusCode=5, message="Not found user permission !")
                # Delete user permission
                userPermissionRecord.delete()
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4, message="Error when update child_depart in user permission")

        return response_data(None)

    def deleteAllUserPermissionHO(self, request):
        userId = request.data.get("userId", None)
        try:
            with transaction.atomic():
                # Find user permissions
                userPermissionRecord = HoUserPermission.objects.filter(user_id=userId)
                if not userPermissionRecord.exists():
                    return response_data(None, statusCode=5, message="Not found user permission !")
                # Delete user permission
                userPermissionRecord.delete()
        except IntegrityError as e:
            print(e)
            return response_data(None, statusCode=4, message="Error when delete all user permission")

        return response_data(None)

    # API nay chi de goi private. API nay duoc goi luc import nhan vien moi de cap cac quyen tren app My PT cho nhan vien moi ngay luc import
    def addMyPTPermissionsToTechEmp(self, request):
        empEmail = request.data.get("empEmail", None)
        empName = request.data.get("empName", None)
        if empName is None:
            empName = ""

        jobTitle = request.data.get("jobTitle", None)
        contractType = request.data.get("contractType", None)
        childDepart = request.data.get("childDepart", None)

        # Check input
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if empEmail is None or not re.fullmatch(validateMailRegex, empEmail):
            return response_data(None, 5, "Missing email or Invalid email!")
        empEmail = empEmail.lower()

        if jobTitle is None or jobTitle.strip() == "":
            return response_data(None, 5, "Missing job title!")
        if contractType is None or contractType.strip() == "":
            return response_data(None, 5, "Missing contract type!")
        if childDepart is None or childDepart.strip() == "":
            return response_data(None, 5, "Missing child depart!")

        jobTitle = jobTitle.lower().strip()
        contractType = contractType.lower().strip()
        childDepart = childDepart.strip()

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        allDepartsWithLevels = None
        allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")
        if allDepartsWithLevelsStr is None:
            allDepartsWithLevels = None
        else:
            allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)

        if allDepartsWithLevels is None:
            return response_data(None, 5, "Missing allDepartsWithLevels data!")

        # Tin parent depart tu child depart
        parentDepart = ""
        for branchStr, parent_departs in allDepartsWithLevels["allDeparts"].items():
            print("parent departs cua branch : " + branchStr)
            print(parent_departs)
            for parent_depart, child_departs_by_parent in parent_departs.items():
                print("child departs cua parent : " + parent_depart)
                print(child_departs_by_parent)
                if childDepart in child_departs_by_parent:
                    print("Da tim thay trong parent depart : " + parent_depart)
                    parentDepart = parent_depart
                    break
            if parentDepart != "":
                break

        if parentDepart == "":
            return response_data(None, 6, "Parent depart not found!")

        LIST_PARENT_DEPART_TICKET_RIGHT = ["PNCV4", "PNCV5", "PNCV6", "PNCV7", "TINV1", "TINV2", "TINV3", "TINV4"]
        LIST_JOB_TITLE_TICKET_RIGHT = ['cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh', "cb xử lý sự cố"]
        LIST_JOB_TITLE_CHECKIN_RIGHT = ['cb kỹ thuật tkbt', 'cb hỗ trợ kỹ thuật từ xa', 'cb hỗ trợ kỹ thuật tại nhà kh','cb xử lý sự cố']
        LIST_CONTRACT_CHECKIN_RIGHT = ['hợp đồng đào tạo nghề', 'hợp đồng thử việc', "hđ đào tạo nghề", "hđ thử việc"]

        # Check emp nay co add quyen HTKT duoc ko
        allowHtktPers = False
        if jobTitle in LIST_JOB_TITLE_TICKET_RIGHT or childDepart == "PSO" or parentDepart in LIST_PARENT_DEPART_TICKET_RIGHT:
            allowHtktPers = True

        # Check emp nay co add quyen Diem danh duoc ko
        allowCheckinPers = False
        if jobTitle in LIST_JOB_TITLE_CHECKIN_RIGHT or contractType in LIST_CONTRACT_CHECKIN_RIGHT:
            allowCheckinPers = True

        # return response_data({
        #     "emp_email": empEmail,
        #     "emp_name": empName,
        #     "jobTitle": jobTitle,
        #     "contractType": contractType,
        #     "parentDepart": parentDepart,
        #     "allowHtktPers": allowHtktPers,
        #     "allowCheckinPers": allowCheckinPers
        # })

        # Find user in mypt_auth_user_infos. If not found, add user to mypt_auth_user_infos
        empStt = "CHUA TON TAI"
        userId = 0
        userInfoQueryset = UserInfos.objects.filter(email=empEmail)
        if not userInfoQueryset.exists():
            # Neu ko co param empName, su dung phan truoc @ cua email de lam name
            if empName == "":
                cutPosition = empEmail.find("@")
                empName = empEmail[:cutPosition]
            # tao user_infos
            newUser = UserInfos(email=empEmail, full_name=empName)
            newUser.save()
            # sau khi insert, get lai user_infos theo email
            userInfoQueryset = UserInfos.objects.filter(email=empEmail)
            if userInfoQueryset.exists():
                userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
                userId = int(userInfoSerializer.data[0]['user_id'])
            else:
                return response_data(None, 4, "Error when creating user acc from email!")
        else:
            empStt = "DA TON TAI"
            userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
            userId = int(userInfoSerializer.data[0]['user_id'])

        if userId <= 0:
            return response_data(None, 5, "User ID invalid!")

        # return response_data({
        #     "user_id": userId,
        #     "empStt": empStt
        # })

        # add cac quyen HTKT
        if allowHtktPers == True:
            # add quyen XEM_TICKET_HTKT_CUA_TOI
            newUserPermission1 = MyPTUserPermission(user_id=userId,
                                                    permission_id=4,
                                                    permission_code='XEM_TICKET_HTKT_CUA_TOI',
                                                    child_depart='')
            try:
                newUserPermission1.save()
            except Exception as e:
                print(e)

            # add quyen TAO_TICKET_HTKT
            newUserPermission2 = MyPTUserPermission(user_id=userId,
                                                    permission_id=9,
                                                    permission_code='TAO_TICKET_HTKT',
                                                    child_depart='')
            try:
                newUserPermission2.save()
            except Exception as e:
                print(e)

            # add quyen DANH_GIA_TICKET_HTKT
            newUserPermission3 = MyPTUserPermission(user_id=userId,
                                                    permission_id=10,
                                                    permission_code='DANH_GIA_TICKET_HTKT',
                                                    child_depart='')
            try:
                newUserPermission3.save()
            except Exception as e:
                print(e)

        # add cac quyen Diem danh
        if allowCheckinPers == True:
            # add quyen THUC_HIEN_DIEM_DANH
            newUserPermission4 = MyPTUserPermission(user_id=userId,
                                                    permission_id=2,
                                                    permission_code='THUC_HIEN_DIEM_DANH',
                                                    child_depart='')
            try:
                newUserPermission4.save()
            except Exception as e:
                print(e)

            # add quyen XEM_LICH_SU_DIEM_DANH
            newUserPermission5 = MyPTUserPermission(user_id=userId,
                                                    permission_id=3,
                                                    permission_code='XEM_LICH_SU_DIEM_DANH',
                                                    child_depart='')

            try:
                newUserPermission5.save()
            except Exception as e:
                print(e)

        return response_data({
            "emp_email": empEmail,
            "emp_name": empName,
            "jobTitle": jobTitle,
            "contractType": contractType,
            "parentDepart": parentDepart,
            "allowHtktPers": allowHtktPers,
            "allowCheckinPers": allowCheckinPers,
            "empStt": empStt,
            "user_id": userId
        })

    # API nay de goi private. API nay lay ra cac email tu table emails_prepare_add_permissions_and_fea_roles
    # de add cac quyen HO & HO feature roles cho cac email do
    def addHoPersAndFeaRolesForEmails(self, request):
        # check coi co email duoc truyen vao hay ko truoc. Neu ko co thi moi lay tu table emails_prepare_add_permissions_and_fea_roles
        emailsWithChildDepart = request.data.get("emailsWithChildDepart", [])
        if not isinstance(emailsWithChildDepart, list):
            return response_data(None, 5, "Param emails is not array!")

        if len(emailsWithChildDepart) == 0:
            # Neu ko co email trong param emailsWithChildDepart : lay cac email tu table emails_prepare_add_permissions_and_fea_roles
            emailLimit = int(request.data.get("emailLimit", 5))
            emailsQs = EmailsPrepareAddPersFeaRoles.objects.filter(is_processed=0).order_by("id")[0:emailLimit]
            emailsSr = EmailsPrepareAddPersFeaRolesSerializer(emailsQs, many=True)
            emailsRows = emailsSr.data
            if len(emailsRows) == 0:
                return response_data(None, 6, "No any email to handle!")
            # print(emailsRows)
            emailsWithChildDepart = []
            for emailRow in emailsRows:
                emailsWithChildDepart.append({
                    "email": emailRow["email"],
                    "childDepart": emailRow["childDepart"]
                })

        # return response_data(emailsWithChildDepart)

        # xu ly kiem tra cac permission code trong param permissions
        persData = []
        permissions = request.data.get("permissions", None)
        if permissions is not None and isinstance(permissions, list) and len(permissions) > 0:
            for permissionCode in permissions:
                permissionQueryset = HoPermission.objects.filter(permission_code=permissionCode)
                if not permissionQueryset.exists():
                    return response_data(None, 6, "Permission " + permissionCode + " does not exist!")
                permissionSerializer = HoPermissionSerializer(permissionQueryset, many=True)
                perData = permissionSerializer.data[0]
                persData.append({
                    "perId": perData["permissionId"],
                    "perCode": perData["permissionCode"],
                    "hasDepartRight": perData["hasDepartRight"]
                })

        # return response_data(persData)

        # xu ly param feaRoles
        feaRoles = request.data.get("feaRoles", None)
        # Neu ko co param feaRoles va permissions, stop API nay
        if feaRoles is None and len(persData) == 0:
            return response_data(None, 5, "No any feature role and permission!")

        feaRolesData = []
        if feaRoles is not None:
            for feaCode, roleCode in feaRoles.items():
                # check co ton tai feaCode & roleCode nay trong bang features_roles hay ko
                feaRoleQs = FeaturesRoles.objects.filter(feature_code=feaCode, role_code=roleCode, platform="ho")
                if not feaRoleQs.exists():
                    return response_data(None, 6, "Role " + roleCode + " of the feature " + feaCode + " does not exist!")
                feaRoleSerializer = FeaturesRolesSerializer(feaRoleQs, many=True)
                feaRoleItem = feaRoleSerializer.data[0]
                feaRolesData.append({
                    "roleId": feaRoleItem["role_id"],
                    "roleCode": feaRoleItem["role_code"],
                    "feaCode": feaRoleItem["feature_code"]
                })
                pass

        # return response_data({
        #     "emailsWithChildDepart": emailsWithChildDepart,
        #     "persData": persData,
        #     "feaRolesData": feaRolesData
        # })

        # Bat dau gan permission & fea role cho cac email
        processedEmails = []
        validateMailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for emailItem in emailsWithChildDepart:
            emailStr = emailItem["email"]
            # Check input
            if not re.fullmatch(validateMailRegex, emailStr):
                continue
            emailStr = emailStr.lower()

            # Find user in mypt_auth_user_infos. If not found, add user to mypt_auth_user_infos
            empStt = "CHUA TON TAI"
            userId = 0
            userInfoQueryset = UserInfos.objects.filter(email=emailStr)
            if not userInfoQueryset.exists():
                print("email " + emailStr + " chua co User acc!")
                cutPosition = emailStr.find("@")
                fullName = emailStr[:cutPosition]
                # tao user_infos
                newUser = UserInfos(email=emailStr, full_name=fullName)
                newUser.save()
                # sau khi insert, get lai user_infos theo email
                userInfoQueryset = UserInfos.objects.filter(email=emailStr)
                if userInfoQueryset.exists():
                    userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
                    userId = int(userInfoSerializer.data[0]['user_id'])
                else:
                    print("Error when creating user acc from email : " + emailStr)
                    continue
            else:
                print("email " + emailStr + " da co User acc!")
                empStt = "DA TON TAI"
                userInfoSerializer = UserInfosSerializer(userInfoQueryset, many=True)
                userId = int(userInfoSerializer.data[0]['user_id'])

            if userId <= 0:
                print("User ID invalid, for the email : " + emailStr)
                continue

            # Gan cac quyen trong persData cho user nay
            for perItem in persData:
                childDepartStr = ""
                if perItem['hasDepartRight'] == 0:
                    childDepartStr = ""
                else:
                    childDepartStr = emailItem["childDepart"]

                # Add user permission
                HoUserPermission.objects.update_or_create(
                    user_id=userId,
                    permission_id=perItem["perId"],
                    permission_code=perItem['perCode'],
                    defaults={"child_depart": childDepartStr}
                )

            # Gan fea roles cho email nay
            for feaRoleIt in feaRolesData:
                roleEmailQs = FeaturesRolesEmails.objects.filter(email=emailStr, role_id=feaRoleIt["roleId"])
                if not roleEmailQs.exists():
                    print("Email " + emailStr + " is NOT assigned with role " + str(feaRoleIt["roleId"]) + " - " + feaRoleIt["roleCode"] + " so now will assign!")
                    roleEmailRecord = FeaturesRolesEmails(email=emailStr, role_id=feaRoleIt["roleId"], role_code=feaRoleIt["roleCode"], feature_code=feaRoleIt["feaCode"])
                    roleEmailRecord.save()
                else:
                    print("Email " + emailStr + " is assigned with role " + str(feaRoleIt["roleId"]) + " - " + feaRoleIt["roleCode"] + " already!")

            # update is_processed cua email nay thanh 1 trong table emails_prepare_add_permissions_and_fea_roles
            EmailsPrepareAddPersFeaRoles.objects.filter(email=emailStr).update(is_processed=1, date_modified=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            processedEmails.append(emailStr)

        return response_data({
            "processedEmails": processedEmails
        })