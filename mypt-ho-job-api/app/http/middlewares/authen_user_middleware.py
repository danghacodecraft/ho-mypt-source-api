from django.http import JsonResponse
from datetime import datetime
from app.configs import app_settings
from app.core.entities.centralized_session import CentralizedSession
from app.core.helpers import utils as utHelper

class AuthenUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        for routeUrl in routesMiddlewareData:
            if curUrl == routeUrl:
                middlewareApplied = True

        if middlewareApplied == False:
            response = self.get_response(request)
            return response

        excepRespondedData = {
            "statusCode": 3,
            "message": "Token is failed",
            "data": None
        }

        # redis_session_expired (code = 7) : app goi API user-token (voi grantType=refresh_token) de tao lai Access Token tu Refresh Token
        # access_token_failed (code = 3) : quay ve man hinh Login
        # connect_redis_failed (code = 8) : hien popup thong bao loi
        errorCodes = {
            "access_token_failed": 3,
            "redis_session_expired": 7,
            "connect_redis_failed": 8
        }

        headerAuthToken = request.headers.get("Authorization")
        print("[middleware " + className + "] ta co Bearer header auth token : " + str(headerAuthToken))

        if headerAuthToken is None:
            print("[middleware " + className + "] Header auth token is None")
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is none",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        headerAuthToken = str(headerAuthToken)
        if headerAuthToken == "":
            print("[middleware " + className + "] Header auth token is empty")
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is empty",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        # remove Bearer
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        print("[middleware " + className + "] new header auth token : " + newHeaderAuthToken)
        if newHeaderAuthToken == "":
            print("[middleware " + className + "] New Header auth token is empty")
            excepRespondedData = {
                "statusCode": errorCodes.get("access_token_failed"),
                "message": "Token is empty",
                "data": None
            }
            return JsonResponse(excepRespondedData)

        # validate session
        cenSessionObj = CentralizedSession()
        resValidateSession = cenSessionObj.validateSession(newHeaderAuthToken)
        if resValidateSession.get("errorCode") != "no_error":
            errorCode = resValidateSession.get("errorCode")
            errorResData = None
            if errorCode == "redis_session_expired":
                # this is case Redis Session Expired, extoken 
                exToken = utHelper.encrypt_aes(app_settings.AES_SECRET_KEY, str(int(datetime.now().timestamp())))
                errorResData = {
                    "extoken": exToken
                }

            excepRespondedData = {
                "statusCode": errorCodes.get(errorCode),
                "message": resValidateSession.get("errorMsg"),
                "data": errorResData
            }
            return JsonResponse(excepRespondedData)
        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        print("vao process request")

        return None

    def process_response(self, request, response):
        print('vao process response')

        return None
