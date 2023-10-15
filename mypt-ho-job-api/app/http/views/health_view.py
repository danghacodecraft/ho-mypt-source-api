from ...core.helpers.response import *
import redis
from django.conf import settings as project_settings
from rest_framework.viewsets import ViewSet


class HealthView(ViewSet):
    def health(self, request):
        domain_name = request.get_host()

        # test ket noi redis
        redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                           , port=project_settings.REDIS_PORT_CENTRALIZED
                                           , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                           password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                           , decode_responses=True, charset="utf-8")

        res_data = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "testRedisVal": redis_instance.get("profile"),
            "domainName": domain_name
        }

        return response_data(data=res_data)

    def add_kong(self):
        return response_data(data='ok')
