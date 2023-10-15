from django.conf import settings as project_settings
from ..entities.my_jwt import MyJwt
import redis
import ast


def getUserAuthSessionData(bearerAccessToken):
    if bearerAccessToken is None:
        return None

    bearerAccessToken = str(bearerAccessToken)
    if bearerAccessToken == "":
        return None

    print("[getUserAuthSessionData] Bearer access token : " + bearerAccessToken)

    accessTokenStr = bearerAccessToken.replace("Bearer ", "")
    if accessTokenStr == "":
        return None

    print("[getUserAuthSessionData] Access token sau cung : " + accessTokenStr)

    # Decode JWT auth token de lay duoc JTI
    jwtObj = MyJwt()
    payloadData = jwtObj.decodeJwtToken(accessTokenStr, False)
    if payloadData is None:
        return None

    if payloadData.get("jti", None) is None:
        return None

    jtiStr = payloadData.get("jti")
    print("[getUserAuthSessionData] JTI lay duoc tu JWT token : " + jtiStr)

    sessionKey = "session:" + jtiStr

    centralRedisSer = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                        , port=project_settings.REDIS_PORT_CENTRALIZED
                                        , db=project_settings.REDIS_DATABASE_CENTRALIZED
                                        , password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                        , decode_responses=True, charset="utf-8")

    sessionStr = centralRedisSer.get(sessionKey)
    if sessionStr is None:
        print("[getUserAuthSessionData] Khong tim thay key Access Token nay trong Redis : " + sessionKey)
        return None

    print("[getUserAuthSessionData] Auth Session string lay tu Redis : " + sessionStr)

    # convert string session nay thanh Dict
    sessionData = ast.literal_eval(sessionStr)
    # luu them JTI
    sessionData["accessTokenJti"] = jtiStr

    print("[getUserAuthSessionData] Auth Session Data sau khi convert tu string: ")
    print(sessionData)

    return sessionData


def getJtiFromAccessToken(bearerAccessToken):
    if bearerAccessToken is None:
        return ""

    bearerAccessToken = str(bearerAccessToken)
    if bearerAccessToken == "":
        return ""

    print("[getJtiFromAccessToken] Bearer access token : " + bearerAccessToken)

    accessTokenStr = bearerAccessToken.replace("Bearer ", "")
    if accessTokenStr == "":
        return ""

    print("[getJtiFromAccessToken] Access token sau cung : " + accessTokenStr)

    # Decode JWT auth token de lay duoc JTI
    jwtObj = MyJwt()
    payloadData = jwtObj.decodeJwtToken(accessTokenStr, False)
    if payloadData is None:
        return ""

    if payloadData.get("jti", None) is None:
        return ""

    jtiStr = payloadData.get("jti")
    print("[getJtiFromAccessToken] JTI lay duoc tu JWT token : " + jtiStr)

    return jtiStr

# def getUserAuthSessionData(bearerAccessToken):
#     if bearerAccessToken is None:
#         return None
#
#     bearerAccessToken = str(bearerAccessToken)
#     if bearerAccessToken == "":
#         return None
#
#     print("[getUserAuthSessionData] Bearer access token : " + bearerAccessToken)
#
#     accessTokenStr = bearerAccessToken.replace("Bearer ", "")
#     if accessTokenStr == "":
#         return None
#
#     print("[getUserAuthSessionData] Access token sau cung : " + accessTokenStr)
#
#     # Decode JWT auth token de lay duoc JTI
#     jwtObj = MyJwt()
#     payloadData = jwtObj.decodeJwtToken(accessTokenStr, False)
#     if payloadData is None:
#         return None
#
#     if payloadData.get("jti", None) is None:
#         return None
#
#     jtiStr = payloadData.get("jti")
#     print("[getUserAuthSessionData] JTI lay duoc : " + jtiStr)
#
#     sessionKey = "session:" + jtiStr
#
#     if global_variables.centralRedisService is None:
#         print("[getUserAuthSessionData] Chua ket noi Redis centralized !")
#         try:
#             global_variables.centralRedisService = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
#                                                , port=project_settings.REDIS_PORT_CENTRALIZED
#                                                , db=project_settings.REDIS_DATABASE_CENTRALIZED,
#                                                password=project_settings.REDIS_PASSWORD_CENTRALIZED
#                                                , decode_responses=True, charset="utf-8")
#         except Exception as e:
#             return None
#     else:
#         redisAvai = False
#         try:
#             redisAvai = global_variables.centralRedisService.ping()
#             print("[getUserAuthSessionData] Ket qua ping redis : ")
#             print(redisAvai)
#         except Exception as e:
#             redisAvai = False
#
#         if redisAvai == True:
#             print("[getUserAuthSessionData] Da ket noi Redis centralized!")
#         else:
#             print("[getUserAuthSessionData] Ket noi Redis centralized bi ngat! Can connect lai!")
#             try:
#                 global_variables.centralRedisService = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
#                                                                          , port=project_settings.REDIS_PORT_CENTRALIZED
#                                                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED
#                                                                          , password=project_settings.REDIS_PASSWORD_CENTRALIZED
#                                                                          , decode_responses=True, charset="utf-8")
#             except Exception as e:
#                 return None
#
#     sessionStr = global_variables.centralRedisService.get(sessionKey)
#     if sessionStr is None:
#         return None
#
#     print("[getUserAuthSessionData] Auth session Str : " + sessionStr)
#
#     # convert string session nay thanh Dict
#     sessionData = ast.literal_eval(sessionStr)
#
#     print("[getUserAuthSessionData] Auth Session Data sau khi convert tu str: ")
#     print(sessionData)
#
#     return sessionData
