from datetime import datetime
from datetime import timedelta
from django.conf import settings as project_settings
from app.core.entities.my_jwt import MyJwt
import redis
import ast

class CentralizedSession:
    redisInstance = None
    sessionPrefix = "session:"

    def __init__(self):
        self.redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
            , port=project_settings.REDIS_PORT_CENTRALIZED
            , db=project_settings.REDIS_DATABASE_CENTRALIZED, password=project_settings.REDIS_PASSWORD_CENTRALIZED
            , decode_responses=True, charset="utf-8")

    def saveSession(self, sessionKey, sessionData, seconds):
        if self.redisInstance is None:
            return {
                "resSave": False
            }

        finalSessionKey = self.sessionPrefix + sessionKey
        resSave = self.redisInstance.set(finalSessionKey, str(sessionData), seconds)
        print(resSave)
        if resSave == True:
            print("save centralized session thanh cong!")
            return {
                "resSave": True
            }
        else:
            print("save centralized session that bai!")
            return {
                "resSave": False
            }

    def removeSession(self, sessionKey):
        finalSessionKey = self.sessionPrefix + sessionKey
        self.redisInstance.delete(finalSessionKey)
        return {
            "resRemove": True
        }

    def validateSession(self, accessToken):
        result = {
            "errorCode": "access_token_failed",
            "errorMsg": "Access token failed",
            "sessionData": None
        }

        # Decode JWT auth token de lay duoc JTI
        jwtObj = MyJwt()
        payloadData = jwtObj.decodeJwtToken(accessToken, False)
        if payloadData is None:
            result["errorMsg"] = "AccessToken is invalid"
            return result
        print(payloadData)

        if payloadData.get("jti", None) is None:
            result["errorMsg"] = "AccessToken is not defined correctly"
            return result

        jtiStr = payloadData.get("jti")
        print("JTI lay duoc : " + jtiStr)

        # tim trong Redis co JTI nay hay ko
        sessionData = self.getSession(jtiStr)
        if sessionData is None:
            result["errorCode"] = "redis_session_expired"
            result["errorMsg"] = "Session expired"
            return result

        sessionData["jti"] = jtiStr

        result["errorCode"] = "no_error"
        result["errorMsg"] = "No error"
        result["sessionData"] = sessionData
        return result

    def getSession(self, sessionKey):
        finalSessionKey = self.sessionPrefix + sessionKey
        print("chuan bi lay Redis value cua key : " + finalSessionKey)
        sessionStr = self.redisInstance.get(finalSessionKey)
        print(sessionStr)
        if sessionStr is None:
            return None

        # convert string session nay thanh Dict
        sessionData = ast.literal_eval(sessionStr)
        print(sessionData)

        return sessionData