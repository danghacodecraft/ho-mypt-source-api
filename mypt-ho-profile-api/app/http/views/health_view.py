from ...core.helpers.response import *
from ...core.helpers.helper import *
from ..paginations.custom_pagination import *
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
from rest_framework import status
from ..serializers.hr_serializer import *
    

class HealthView(ViewSet):
    def health(self, request):
        domainName = request.get_host()
        try:
            # test ket noi redis
            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                                , port=project_settings.REDIS_PORT_CENTRALIZED
                                                , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                                password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                                , decode_responses=True, charset="utf-8")

            redisInstance.set("profile", "Day la value cua Redis key profile abcdef 123969", 3600)

            resData = {
                    "redisConInfo": {
                        "host": project_settings.REDIS_HOST_CENTRALIZED,
                        "port": project_settings.REDIS_PORT_CENTRALIZED,
                        "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                        "password": project_settings.REDIS_PASSWORD_CENTRALIZED
                    },
                    "testRedisVal": redisInstance.get("profile"),
                    "domainName": domainName
                }

            return response_data(data=resData)
        except:
            # print('data not ok')
            return Response({'statusCode':0, 'message':'data connection not ok'}, status.HTTP_200_OK)
    def add_kong(self, request):
        return response_data(data='ok')
