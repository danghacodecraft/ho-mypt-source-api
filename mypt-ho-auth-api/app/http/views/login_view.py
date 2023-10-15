from rest_framework.viewsets import ViewSet
from ...core.helpers.response import *
from django.shortcuts import redirect
import jwt
import base64
import json
from datetime import datetime
from django.conf import settings as project_settings
from app.configs import app_settings
from app.core.helpers import utils as utHelper
from app.http.entities import global_data
from app.http.apis.fpt_adfs_apis import FptAdfsapis
from app.http.apis.microsoft_azure_apis import MicrosoftAzureapis
from app.http.entities.oauth_client_grants_handler import OauthClientGrantsHandler
from app.http.entities.authen_handler import AuthenHandler
import redis
import time
from app.http.apis.mypt_ho_profile_apis import MyPtHoProfileapis
from ..entities.permission_handler import *
from app.core.entities.my_jwt import MyJwt

class LoginView(ViewSet):
    def showLogin(self, request):
        domainName = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            print("day la env production : " + appEnv)
            domainName = "https://mypt-ho.fpt.vn"
        elif appEnv == "staging":
            print("day la env staging : " + appEnv)
            domainName = "http://mypt-ho-stag.fpt.vn"
        else:
            print("day la env local : " + appEnv)
            domainName = "http://localhost:4200"

        redirectUri = domainName + "/api/auth"
        print("redirect URI cho ADFS : " + redirectUri)

        authorization_redirect_url = "https://adfs.fpt.com.vn/adfs/oauth2/authorize/?response_type=code&client_id=MyTin-PNC&redirect_uri=" + redirectUri + "&scope=openid%20email%20profile"
        return redirect(authorization_redirect_url)

    def showAzureLogin(self, request):
        redirectUriAfterSuccess = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            print("day la env production : " + appEnv)
            redirectUriAfterSuccess = "https://ho.mypt.vn/api/auth"
        elif appEnv == "staging":
            print("day la env staging : " + appEnv)
            redirectUriAfterSuccess = "https://mypt-ho-stag.fpt.vn/api/auth"
        else:
            print("day la env local : " + appEnv)
            redirectUriAfterSuccess = "http://localhost:4200"

        print("redirect URI cho Azure : " + redirectUriAfterSuccess)

        redirect_url = "https://login.microsoftonline.com/4ebc9261-871a-44c5-93a5-60eb590917cd/oauth2/authorize?client_id=" + app_settings.AZURE_CLIENT_ID + "&response_type=code&response_mode=query&redirect_uri=" + redirectUriAfterSuccess

        print("URL Azure chuan bi redirect : " + redirect_url)

        return redirect(redirect_url)


    def doLogout(self, request):

        # return response_data({"authUser": global_data.authUserSessionData})

        authHandler = AuthenHandler()
        resLogout = authHandler.doLogout(global_data.authUserSessionData.get("jti", None))

        if resLogout.get("result") == True:
            redirectUriAfterLogoutAzure = ""
            appEnv = str(project_settings.APP_ENVIRONMENT)
            if appEnv == "production":
                redirectUriAfterLogoutAzure = "https://ho.mypt.vn/api/auth"
            elif appEnv == "staging":
                redirectUriAfterLogoutAzure = "https://mypt-ho-stag.fpt.vn/api/auth"
            else:
                redirectUriAfterLogoutAzure = "http://localhost:4200"

            resData = {
                "statusCode": 1,
                "message": "SUCCESS",
                "data": {
                    "resLogout": resLogout,
                    "azureLogoutUrl": "https://login.microsoftonline.com/fptcloud.onmicrosoft.com/oauth2/v2.0/logout?post_logout_redirect_uri=" + redirectUriAfterLogoutAzure,
                    "authUserSession": global_data.authUserSessionData
                }
            }
        else:
            resData = {
                "statusCode": 6,
                "message": "Error",
                "data": {
                    "resLogout": resLogout,
                    "authUserSession": global_data.authUserSessionData
                }
            }

        return Response(resData, status.HTTP_200_OK)


    def healthCheck(self, request):
        # test lay domain name tu request
        domainName = request.get_host()

        # test ket noi mysql db
        ocgHandler = OauthClientGrantsHandler()
        clientGrantInfo = ocgHandler.findByGrantIdAndClientId(9, app_settings.OAUTH_CLIENT_ID)

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("myptauthPhong", "Day la value cua Redis key myptauthPhong SIEU NHAN SUPERMAN SPIDER MAN", 3600)
        print("redis value cua myptauth : " + redisInstance.get("myptauthPhong"))

        print("ta co redis port : " + str(project_settings.REDIS_PORT_CENTRALIZED))
        print("minh co redis password : " + project_settings.REDIS_PASSWORD_CENTRALIZED)
        print("CHUNG TA co redis host : " + project_settings.REDIS_HOST_CENTRALIZED)

        resData = {
            "statusCode": 1,
            "message": "Success",
            "data": {
                "clientGrantInfo": clientGrantInfo,
                "redisConInfo": {
                    "host": project_settings.REDIS_HOST_CENTRALIZED,
                    "port": project_settings.REDIS_PORT_CENTRALIZED,
                    "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                    "password": project_settings.REDIS_PASSWORD_CENTRALIZED
                },
                "testRedisVal": redisInstance.get("myptauthPhong"),
                "domainName": domainName,
                "appEnv": project_settings.APP_ENVIRONMENT
            }
        }

        return Response(resData, status.HTTP_200_OK)

    # API nay de tao ra doan encode User Info de truyen vao API /user-token de tao Access Token
    def genLogginedUserToken(self, request):
        postData = request.data
        email = postData.get("email")
        fullName = postData.get("fullName")

        userInfoDic = {
            "email": email,
            "name": fullName
        }
        encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

        curTs = int(datetime.now().timestamp())
        exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

        resData = {
            "statusCode": 1,
            "message": "Success",
            "data": {
                "userToken": encodedUserInfoStr,
                "timeToken": exToken
            }
        }

        return Response(resData, status.HTTP_200_OK)

    # API nay se tao ra user token tu code do FPT ADFS tra ve. user token nay la dung de tao ra Access Token - Refresh Token
    def genUserTokenByCode(self, request):
        # lay param code
        adfsCode = request.data.get("code")
        if adfsCode is None:
            return response_data(None, 5, "missing ADFS code")
        adfsCode = str(adfsCode)
        if adfsCode == "":
            return response_data(None, 5, "ADFS code is empty")

        fptAdfsObj = FptAdfsapis()
        # set callBackUri
        protocol = "http://"
        domainName = request.get_host()
        if domainName == "apis-stag.fpt.vn" or domainName == "apis.fpt.vn":
            protocol = "https://"

        # callBackUri = protocol + domainName + "/" + app_settings.ROUTES_PREFIX + "adfs-token"
        # callBackUri = "https://mytinpnc.vn/api/auth"
        # callBackUri = "http://localhost:4200/api/auth"
        callBackUri = "http://localhost:4200"
        # return response_data({"callBackUri": callBackUri, "adfscode": adfsCode}, 1)

        adfsToken = fptAdfsObj.get_adfs_token(adfsCode, callBackUri)
        if adfsToken == "":
            return response_data(None, 6, "Get token by code failed")

        # return response_data({"adfsToken": adfsToken}, 1)

        # adfsToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjlETHhGbDhMYVh5cklVX1VMdWM0bHh4aXpCMCIsImtpZCI6IjlETHhGbDhMYVh5cklVX1VMdWM0bHh4aXpCMCJ9.eyJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjQyMDAiLCJpc3MiOiJodHRwOi8vYWRmcy5mcHQuY29tLnZuL2FkZnMvc2VydmljZXMvdHJ1c3QiLCJpYXQiOjE2NDg2OTQxODIsIm5iZiI6MTY0ODY5NDE4MiwiZXhwIjoxNjQ4Njk3NzgyLCJ1cG4iOlsicG5jLlBEWEBmcHQubmV0IiwicG5jLnBkeEBmcHQubmV0Il0sImVtYWlsIjoicG5jLlBEWEBmcHQubmV0IiwidW5pcXVlX25hbWUiOlsiUGhvbmcgUERYIiwiRlRFTFxccG5jLlBEWCJdLCJhcHB0eXBlIjoiQ29uZmlkZW50aWFsIiwiYXBwaWQiOiJNeVRpbi1QTkMiLCJhdXRobWV0aG9kIjoidXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFjOmNsYXNzZXM6UGFzc3dvcmRQcm90ZWN0ZWRUcmFuc3BvcnQiLCJhdXRoX3RpbWUiOiIyMDIyLTAzLTMxVDAyOjM2OjIyLjU3MFoiLCJ2ZXIiOiIxLjAiLCJzY3AiOiJvcGVuaWQifQ.aHY88H6ppbp6hf-ZSY_I5sLFyUTsXgKERaMWIIIJwXK_QqSbDlpP2Cld0TBpJIAv5f3fciXm7ZPbOpcDPgz_UMT4uaMFuOJ6fihdxaF9aqcfNzWPDp7LMrPA09nWbU38cmuoQspOb5xO8RAYlE-jPv57S15SfJqsqKrw0EzLZ0thm2m2y4F7FK58BQXTyhkvZw4DgOl7y5sW-BHug_9AKOgGvMN6PgFIZgsvrBzlX7DI40SVP70WIggjDkKi7nLVP1mrEpmga9F3qH9LO1CV_wmJDklFcVSny0AyiF2PGPJ6sPHTaFm1SM7zDCNZKVcYRsU6HAadYhLS6BZq4PAEHg"
        adfsTokenParts = adfsToken.split(".")
        if len(adfsTokenParts) != 3:
            return response_data(None, 6, "Get token failed")

        # them == vao cuoi string thi moi decode base64 duoc
        encodedStr = adfsTokenParts[1] + "=="
        loginUserInfoStr = base64.b64decode(encodedStr)
        loginUserInfo = json.loads(loginUserInfoStr)
        print("Da lay duoc login userinfo tu ADFS Token")
        print(loginUserInfo)
        userEmail = loginUserInfo.get("email").lower()
        userFullNames = loginUserInfo.get("unique_name")

        userInfoDic = {
            "email": userEmail,
            "name": userFullNames[0]
        }
        encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

        curTs = int(datetime.now().timestamp())
        print("cur timestamp : " + str(curTs))
        exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

        return response_data({
            "userToken": encodedUserInfoStr,
            "timeToken": exToken
        })

    # API nay se tao ra user token tu code do Azure tra ve. user token nay la dung de tao ra Access Token - Refresh Token
    def genUserTokenByAzureCode(self, request):
        # azureToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjJaUXBKM1VwYmpBWVhZR2FYRUpsOGxWMFRPSSJ9.eyJhdWQiOiJkNzk2MmE5My1lOWJhLTQ2MTQtODY4ZC1kNjVhMmY1YWZiMTMiLCJpc3MiOiJodHRwczovL2xvZ2luLm1pY3Jvc29mdG9ubGluZS5jb20vNGViYzkyNjEtODcxYS00NGM1LTkzYTUtNjBlYjU5MDkxN2NkL3YyLjAiLCJpYXQiOjE2NTcyNzQzNTEsIm5iZiI6MTY1NzI3NDM1MSwiZXhwIjoxNjU3Mjc4MjUxLCJhaW8iOiJBVlFBcS84VEFBQUEzL29aRVFxZERYTGkzbCtGSisyRmJyRzhBOTR0UkhRd09tNjJjMVd2dDc5OVlTN0FXMjR4a2YzQ3VXMGg5V1I1Ym5PYTU3YUtFUEpUUzZiaVc1OEZBMjNzYlJXYWwwdHJjYXRORjA0ektETT0iLCJuYW1lIjoiUXVhY2ggVG8gUGhvbmcgKEZURUwgUE5DKSIsIm9pZCI6IjU1MjI4YzBkLTU2YzUtNGNkZi05MDYwLTJiYzE4MTFlMDY0NCIsInByZWZlcnJlZF91c2VybmFtZSI6IlBob25nUVRAZnB0LmNvbS52biIsInJoIjoiMC5BVDRBWVpLOFRocUh4VVNUcFdEcldRa1h6Wk1xbHRlNjZSUkdobzNXV2k5YS14TS1BSWcuIiwic3ViIjoiTFduUXNmcVYzWURtUC03QmxGTUZSN0JfS1lNQUtCSVByT0ZqVTR2UGNoTSIsInRpZCI6IjRlYmM5MjYxLTg3MWEtNDRjNS05M2E1LTYwZWI1OTA5MTdjZCIsInV0aSI6IkJ6ZTQxMENCUTBxNU9ud2ZzdGRyQUEiLCJ2ZXIiOiIyLjAifQ.qy0kuc0ydGoiXdWsjXDwzHuKJmmN0nbrIgJmuhRbhhf_hg5xikeTqL1ht5rY8nmphOE-MfeociajKtIjo79pTkGfz4iKxYZHGl8QNyNS2bJXeTL8KaygcOueZF9Jii8-6JKii5iureKF-mAba962kSe5_pU4r1i3N8SrCErX93zZyc0SVfVQKFb7m_LacUXWWrZ1mkQixBb1yc5VjjBZAFS3lzk9rjWmkrAakTRh5A3kLHRocIo67btH9l1HyIhxrQGOoaUg-rO2-W4x9Dfl0SsNuNmiKOL83KBXBSvpZUMTY3ociJonHY1temw-6A7YrUhHB3HbkDnamN3GNwhSsQ"
        # jwtObj = MyJwt()
        # jwtObj.jwtAlgorithm = "RS256"
        # jwtObj.jwtSecretKey = "MIIDBTCCAe2gAwIBAgIQH4FlYNA+UJlF0G3vy9ZrhTANBgkqhkiG9w0BAQsFADAtMSswKQYDVQQDEyJhY2NvdW50cy5hY2Nlc3Njb250cm9sLndpbmRvd3MubmV0MB4XDTIyMDUyMjIwMDI0OVoXDTI3MDUyMjIwMDI0OVowLTErMCkGA1UEAxMiYWNjb3VudHMuYWNjZXNzY29udHJvbC53aW5kb3dzLm5ldDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMBDDCbY/cjEHfEEulZ5ud/CuRjdT6/yN9fy1JffjgmLvvfw6w7zxo1YkCvZDogowX8qqAC/qQXnJ/fl12kvguMWU59WUcPvhhC2m7qNLvlOq90yo+NsRQxD/v0eUaThrIaAveZayolObXroZ+HwTN130dhgdHVTHKczd4ePtDjLwSv/2a/bZEAlPys102zQo8gO8m7W6/NzRfZNyo6U8jsmNkvqrxW2PgKKjIS/UafK9hwY/767K+kV+hnokscY2xMwxQNlSHEim0h72zQRHltioy15M+kBti4ys+V7GC6epL//pPZT0Acv1ewouGZIQDfuo9UtSnKufGi26dMAzSkCAwEAAaMhMB8wHQYDVR0OBBYEFLFr+sjUQ+IdzGh3eaDkzue2qkTZMA0GCSqGSIb3DQEBCwUAA4IBAQCiVN2A6ErzBinGYafC7vFv5u1QD6nbvY32A8KycJwKWy1sa83CbLFbFi92SGkKyPZqMzVyQcF5aaRZpkPGqjhzM+iEfsR2RIf+/noZBlR/esINfBhk4oBruj7SY+kPjYzV03NeY0cfO4JEf6kXpCqRCgp9VDRM44GD8mUV/ooN+XZVFIWs5Gai8FGZX9H8ZSgkIKbxMbVOhisMqNhhp5U3fT7VPsl94rilJ8gKXP/KBbpldrfmOAdVDgUC+MHw3sSXSt+VnorB4DU4mUQLcMriQmbXdQc8d1HUZYZEkcKaSgbygHLtByOJF44XUsBotsTfZ4i/zVjnYcjgUQmwmAWD"
        # azureTokenData = jwtObj.decodeJwtToken(azureToken, False)
        #
        # return response_data({"azureTokenData": azureTokenData})

        # lay param code
        azureCode = request.data.get("code")
        if azureCode is None:
            return response_data(None, 5, "missing AZURE code")
        azureCode = str(azureCode)
        if azureCode == "":
            return response_data(None, 5, "AZURE code is empty")

        # goi API ben Azure de lay Token tu Azure Code
        azureObj = MicrosoftAzureapis()
        # dua theo APP_ENV de chon ra callBackUri
        callBackUri = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "production":
            callBackUri = "https://ho.mypt.vn/api/auth"
        elif appEnv == "staging":
            callBackUri = "https://mypt-ho-stag.fpt.vn/api/auth"
        else:
            callBackUri = "http://localhost:4200"
        # call API ben Azure
        azureObj.app_env = appEnv
        azureToken = azureObj.getAzureToken(azureCode, callBackUri)
        print("[genUserTokenByAzureCode] AZURE Token tra ve tu API la : " + azureToken)
        if azureToken == "":
            return response_data(None, 6, "Get Azure Token by code failed")

        # dung jwt decode Azure Token
        jwtObj = MyJwt()
        jwtObj.jwtAlgorithm = "RS256"
        azureTokenData = jwtObj.decodeJwtToken(azureToken, False)
        if azureTokenData is None:
            return response_data(None, 6, "Get Azure Token by code failed")

        userEmail = azureTokenData.get("preferred_username", "")
        if userEmail == "":
            return response_data(None, 6, "Get Azure Token by code failed because of missing email")
        userEmail = userEmail.lower()
        fullName = azureTokenData.get("name", "")

        userInfoDic = {
            "email": userEmail,
            "name": fullName
        }
        print(userInfoDic)
        encodedUserInfoStr = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(userInfoDic))

        curTs = int(datetime.now().timestamp())
        print("Azure cur timestamp : " + str(curTs))
        exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(curTs))

        return response_data({
            "userToken": encodedUserInfoStr,
            "timeToken": exToken
        })

    def testGetUserSession(self, request):

        # test ket noi redis
        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")

        resSetRedisKey = redisInstance.set("myptHoAuthPhong", "Day la value cua Redis key myptHoAuthPhong WEB HO MYPT", 3600)

        resData = {
            "redisConInfo": {
                "host": project_settings.REDIS_HOST_CENTRALIZED,
                "port": project_settings.REDIS_PORT_CENTRALIZED,
                "dbName": project_settings.REDIS_DATABASE_CENTRALIZED,
                "password": project_settings.REDIS_PASSWORD_CENTRALIZED
            },
            "domainName": request.get_host(),
            "hoAuthRedisValue": redisInstance.get("myptHoAuthPhong"),
            "hoAuthUserSession": global_data.authUserSessionData
        }

        return Response(resData, status.HTTP_200_OK)

    def testPermission(self, request):
        postData = request.data
        userId = postData.get("userId")

        perHandler = PermissionHandler()
        pers = perHandler.getAllPermissionsByUser(userId)

        return response_data({"pers": pers})