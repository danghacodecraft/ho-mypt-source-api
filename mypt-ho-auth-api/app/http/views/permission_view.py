# Models
from ..models.ho_permission import *
from ..models.ho_permission_group import *
from ..models.ho_permission_with_route import *
# Serializers
from ..serializers.ho_permission_serializer import *
from ..serializers.ho_permission_group_serializer import *
from ..serializers.ho_permission_with_route_serializer import *
# Helpers
from ...core.helpers.response import *
# Rest Framework
from rest_framework.viewsets import ViewSet
import redis
from django.conf import settings as project_settings
import ast


class HoPermissionView(ViewSet):
    def getAllPermissions(self, request):
        # Groups permissions
        queryset = HoPermissionGroup.objects.filter(is_deleted=False).all()
        serializer = HoPermissionGroupSerializer(queryset, many=True)
        permissionsGroup = {item['permission_group_id']: item['permission_group_code'] for item in serializer.data}
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

        data = {
            'permissions': permissions
        }
        return response_data(data)

    # API nay chi de goi private. API nay se luu tat ca lien ket giua cac API route cua cac service HO-MyPT voi permission code xuong Redis
    def savePermissionWithRouteToRedis(self, request):
        qs = HoPermissionWithRoute.objects.all()
        serializer = HoPermissionWithRouteSerializer(qs, many=True)
        rows = serializer.data
        if len(rows) <= 0:
            return response_data(None, 6, "Khong co data")

        dataForRedis = {}
        for row in rows:
            serviceName = row.get("service_name")
            apiRoute = row.get("api_route")
            if dataForRedis.get(serviceName, None) is None:
                dataForRedis[serviceName] = {}
            perCodesStr = row.get("permission_codes").strip()
            perCodes = []
            if perCodesStr != "":
                perCodes = perCodesStr.split(",")
            dataForRedis[serviceName][apiRoute] = perCodes

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        resSaveRedis = redisInstance.set("permissionsWithRoutes", str(dataForRedis))
        print(resSaveRedis)

        return response_data({"resSaveRedis": resSaveRedis, "dataForRedis": dataForRedis})

    # API nay chi de goi private. API nay se tra ve value cua key permissionsWithRoutes tu Redis
    def getPermissionWithRouteFromRedis(self, request):
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        permissionsWithRoutesStr = redisInstance.get("permissionsWithRoutes")
        if permissionsWithRoutesStr is None:
            return response_data(None, 6, "Khong co redis permissionsWithRoutes")
        else:
            permissionsWithRoutesData = ast.literal_eval(permissionsWithRoutesStr)
            return response_data({"permissionsWithRoutesFromRedis": permissionsWithRoutesData})