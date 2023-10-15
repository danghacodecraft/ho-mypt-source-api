from ...core.helpers.response import *
import redis
from django.conf import settings as project_settings
from rest_framework.viewsets import ViewSet
from rest_framework import status
    

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

            resData = {
                "redisConInfo": {
                    "host": project_settings.REDIS_HOST_CENTRALIZED,
                    "port": project_settings.REDIS_PORT_CENTRALIZED,
                    "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                    "password": project_settings.REDIS_PASSWORD_CENTRALIZED
                },
                "testRedisVal": redisInstance.get("profile"),
                "domainName": domainName,
                "appEnv": project_settings.APP_ENVIRONMENT
            }

            return response_data(data=resData)
        except Exception as ex:
            return Response({'statusCode': 0, 'message': f'data connection not ok: {ex}'}, status.HTTP_200_OK)
    
    def add_kong(self, request):
        return response_data(data='ok')
