import requests
import json
from app.configs import app_settings
from django.conf import settings as project_settings

class MyPtHoProfileapis:
    base_uri = ""

    def __init__(self):
        domainName = ""
        appEnv = str(project_settings.APP_ENVIRONMENT)
        if appEnv == "staging":
            print("MyPtHOProfileapis : moi truong staging")
            domainName = app_settings.MYPT_HO_PROFILE_STAGING_DOMAIN_NAME
        elif appEnv == "production":
            print("MyPtHOProfileapis : moi truong production")
            domainName = app_settings.MYPT_HO_PROFILE_PRODUCTION_DOMAIN_NAME
        else:
            print("MyPtHOProfileapis : moi truong local")
            domainName = app_settings.MYPT_HO_PROFILE_LOCAL_DOMAIN_NAME

        self.base_uri = domainName + "/mypt-ho-profile-api"

    def getProfileInfo(self, userId, email, fullName, extra = {}):
        apiUrl = self.base_uri + "/get-profile-info"
        inputParamsStr = json.dumps({
            "userId": int(userId),
            "email": email,
            "fullName": fullName,
            "specificChildDeparts": extra.get("specificChildDeparts", [])
        })
        headersDict = {
            "Content-Type": "application/json"
        }
        print("URL mypt-ho-profile-api get profile info : " + apiUrl + " ; " + inputParamsStr)
        print(headersDict)

        try:
            responseObj = requests.post(apiUrl, headers=headersDict, data=inputParamsStr, timeout=5)
            print("Result call API mypt-ho-profile get profile info : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            print(responseData)
            # return responseData

            if responseData.get("statusCode", None) is None:
                return None

            infoData = None
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                infoData = responseData.get("data")

            return infoData
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("api_auth :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("api_auth :Connection Timeout")

        return None


    def healthCheck(self):
        apiUrl = self.base_uri + "/health"

        print("URL mypt-ho-profile-api health : " + apiUrl)

        try:
            responseObj = requests.get(apiUrl, timeout=5)
            print("Result call API mypt-ho-profile-api health : " + responseObj.text)
            responseData = json.loads(responseObj.text)
            print(responseData)
            # return responseData

            if responseData.get("statusCode", None) is None:
                return None

            infoData = None
            resCode = int(responseData.get("statusCode"))
            if resCode == 1:
                infoData = responseData.get("data")

            return infoData
        except Exception as ex:
            if isinstance(ex, requests.exceptions.ReadTimeout):
                # logger.info("api_auth :Connection Timeout")
                print("api_auth :Connection Timeout")
            if isinstance(ex, requests.exceptions.ConnectionError):
                # logger.info("api_auth :Connection Error")
                print("api_auth :Connection Timeout")

        return None