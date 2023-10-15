from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from app.core.helpers import utils as utHelper
from datetime import datetime
from app.configs import app_settings

class TimeAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        print("[middleware " + className + "] goi truoc khi response ne : " + curUrl)

        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        for routeUrl in routesMiddlewareData:
            if curUrl == routeUrl:
                middlewareApplied = True

        if middlewareApplied == False:
            print("route " + curUrl + " ko duoc apply middleware " + className)
            response = self.get_response(request)
            return response

        excepRespondedData = {
            "statusCode": 3,
            "message": "Token is failed",
            "data": None
        }

        headerAuthToken = request.headers.get("Authorization")
        print("[middleware " + className + "] ta co time header auth token : " + str(headerAuthToken))

        if headerAuthToken is None:
            print("Header auth token is None")
            return JsonResponse(excepRespondedData)

        headerAuthToken = str(headerAuthToken)
        if headerAuthToken == "":
            print("Header auth token is empty")
            return JsonResponse(excepRespondedData)

        timeStr = utHelper.decrypt_aes(app_settings.AES_SECRET_KEY, headerAuthToken)
        authTimeStamp = int(timeStr)

        # cong them 120s
        expiredTs = authTimeStamp + 15
        # lay timestamp hien tai
        curTs = int(datetime.now().timestamp())
        print("Cur TS : " + str(curTs) + " ; Expired TS : " + str(expiredTs))
        if curTs > expiredTs:
            print("[middleware " + className + "] da qua thoi gian cho phep chay API " + curUrl)
            return JsonResponse(excepRespondedData)

        # authDt = datetime.fromtimestamp(authTimeStamp)
        # expiredDt = datetime.fromtimestamp(expiredTs)
        #
        # authDt_str = datetime.strftime(authDt, "%Y-%m-%d %H:%M:%S")
        # print("time lay tu header : " + authDt_str)
        #
        # expiredDt_str = datetime.strftime(expiredDt, "%Y-%m-%d %H:%M:%S")
        # print("ket qua : " + expiredDt_str)

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
