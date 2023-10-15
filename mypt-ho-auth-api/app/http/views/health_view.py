from ...core.helpers.response import *
from ...core.helpers.helper import *
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
    

class HealthView(ViewSet):
    def health(self, request):
        domainName = request.get_host()
            
        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                            , port=project_settings.REDIS_PORT_CENTRALIZED
                                            , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                            password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                            , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("myptHoAuth", "Day la value cua Redis key myptHoAuth zxcjkl 333999", 3600)
        print("redis value : " + redisInstance.get("myptHoAuth"))

        print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
        print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
        print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

        resData = {
                "redisConInfo": {
                    "host": project_settings.REDIS_HOST_CENTRALIZED,
                    "port": project_settings.REDIS_PORT_CENTRALIZED,
                    "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                    "password": project_settings.REDIS_PASSWORD_CENTRALIZED
                },
                "myptHoAuthRedisVal": redisInstance.get("myptHoAuth"),
                "domainName": domainName
            }

        return response_data(data=resData)