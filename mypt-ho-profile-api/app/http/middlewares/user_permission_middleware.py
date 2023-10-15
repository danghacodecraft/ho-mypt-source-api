from django.http import JsonResponse
from django.conf import settings as project_settings
from app.configs import app_settings
from ...core.helpers import auth_session_handler as authSessionHandler
import redis
import ast
import json


class UserPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        middlewareApplied = False
        curUrl = request.path
        className = self.__class__.__name__.lower()
        # print("[" + className + "] URL API hien tai : " + curUrl)
        routesMiddlewareData = app_settings.MIDDLEWARE_APPLIED_FOR_ROUTES.get(className)
        if curUrl in routesMiddlewareData:
            middlewareApplied = True

        if middlewareApplied == False:
            # print("route " + curUrl + " KHONG duoc apply middleware " + className)
            response = self.get_response(request)
            return response

        excepRespondedData = {
            "statusCode": 6,
            "message": "No permission for this API",
            "data": None
        }

        # Check URL hien tai dang duoc map voi permission nao (check trong Redis centralized)
        apiRoute = curUrl.replace("/" + app_settings.ROUTES_PREFIX, "")
        # print("[" + className + "] api route : " + apiRoute + " ; " + "service name : " + app_settings.SERVICE_NAME)

        redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                          , port=project_settings.REDIS_PORT_CENTRALIZED
                                          , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                          password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                          , decode_responses=True, charset="utf-8")
        permissionsWithRoutesStr = redisInstance.get("permissionsWithRoutes")
        if permissionsWithRoutesStr is None:
            # print("[" + className + "] Ko ton tai redis permissionsWithRoutes! Ko duoc di tiep API nay nua!")
            excepRespondedData["message"] = "No permission with route data"
            return JsonResponse(excepRespondedData)

        permissionsWithRoutesData = ast.literal_eval(permissionsWithRoutesStr)
        # print(permissionsWithRoutesData)

        if permissionsWithRoutesData.get(app_settings.SERVICE_NAME, None) is None:
            # print("[" + className + "] Ko co service " + app_settings.SERVICE_NAME + " trong redis permissionsWithRoutes ! Ko duoc di tiep API nay nua!")
            excepRespondedData["message"] = "No service in permission with route data"
            return JsonResponse(excepRespondedData)

        servicePersRoutes = permissionsWithRoutesData[app_settings.SERVICE_NAME]
        if servicePersRoutes.get(apiRoute, None) is None:
            # print("[" + className + "] Ko ton tai API route " + apiRoute + " trong service " + app_settings.SERVICE_NAME + " trong redis permissionsWithRoutes ! Ko duoc di tiep API nay nya!")
            excepRespondedData["message"] = "No API route in service in permission with route data"
            return JsonResponse(excepRespondedData)

        perCodesByApiRoute = servicePersRoutes[apiRoute]
        # print("[" + className + "] API route " + apiRoute + " trong service " + app_settings.SERVICE_NAME + " duoc map voi quyen : ")
        # print(perCodesByApiRoute)

        # check permisssions trong User session xem co quyen tinh nang nay ko
        userPerCode = ""
        userPerData = {}
        userPersData = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))["permissions"]

        # Neu trong permissions co quyen ALL
        userHasRight = False
        if userPersData.get("ALL", None) is not None:
            userHasRight = True
            userPerCode = "ALL"
            userPerData = userPersData.get("ALL")
        else:
            # di qua tung permission trong perCodesByApiRoute
            for perCodeByApiRoute in perCodesByApiRoute:
                if userPersData.get(perCodeByApiRoute, None) is not None:
                    userHasRight = True
                    userPerCode = perCodeByApiRoute
                    userPerData = userPersData.get(perCodeByApiRoute)
                    break

        if userHasRight == False:
            print("[" + className + "] User nay ko co quyen chay API nay!")
            excepRespondedData["message"] = "Bạn không có quyền thực hiện tính năng này!"
            return JsonResponse(excepRespondedData)

        # print("[" + className + "] permission đang check la : " + userPerCode)
        # print(userPerData)

        # tiep theo la check quyen phong ban (neu has_depart_right = 1)
        if userPerData["has_depart_right"] == 1:
            # print("[" + className + "] Permisssion " + userPerCode + " can check quyen phong ban")
            # check trong input cua API co param childDepart (danh sach bo phan) hay ko
            decodedBodyDataStr = ""
            bodyDataStr = request.body
            try:
                decodedBodyDataStr = bodyDataStr.decode("utf-8")
            except Exception as ex:
                decodedBodyDataStr = ""

            # print("body data sau khi decode : " + decodedBodyDataStr + " ;")

            if decodedBodyDataStr == "":
                print("[" + className + "] Khong co params trong body. Cho phep di tiep API!")
                response = self.get_response(request)
                return response

            bodyParams = None
            try:
                bodyParams = json.loads(decodedBodyDataStr)
            except Exception as ex:
                bodyParams = None

            # print(bodyParams)

            if bodyParams is None:
                # print("[" + className + "] Khong co JSON input params trong body. Cho phep chay tiep API!")
                response = self.get_response(request)
                return response

            childDepartsParamArr = bodyParams.get("childDepart", None)
            if childDepartsParamArr is None:
                # print("[" + className + "] Khong co param childDepart duoc truyen len API. Cho phep di tiep API!")
                response = self.get_response(request)
                return response
                # excepRespondedData["message"] = "Missing child departs"
                # return JsonResponse(excepRespondedData)

            if not isinstance(childDepartsParamArr, list):
                # print("[" + className + "] param childDepart khong phai array, list. Cho phep di tiep API!")
                response = self.get_response(request)
                return response

            # print(childDepartsParamArr)
            if len(childDepartsParamArr) <= 0:
                # print("[" + className + "] param childDepart empty. Cho phep di tiep API!")
                response = self.get_response(request)
                return response
                # excepRespondedData["message"] = "Empty child departs"
                # return JsonResponse(excepRespondedData)

            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                              , port=project_settings.REDIS_PORT_CENTRALIZED
                                              , db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                              , decode_responses=True, charset="utf-8")
            allDepartsWithLevels = None
            allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")
            if allDepartsWithLevelsStr is None:
                allDepartsWithLevels = None
            else:
                allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)

            if allDepartsWithLevels is None:
                excepRespondedData["message"] = "Missing data"
                return JsonResponse(excepRespondedData)

            # check tung child depart trong childDepartsParamArr : xem permission nay co apply cho cac child depart nay ko
            hasRightOnChildDeparts = True
            for childDepartParam in childDepartsParamArr:
                childDepartParam = str(childDepartParam)
                # print("[" + className + "] Check tung child trong childDepartsParamArr : " + childDepartParam)
                hasRightOnChildDepart = False
                # check child_depart_rights truoc
                for parentDepart, childDepartsByParent in userPerData["child_depart_rights"].items():
                    # print("[" + className + "] Tim trong parent depart cua child_depart_rights : " + parentDepart)
                    if childDepartParam in childDepartsByParent:
                        # print("[" + className + "] Da tim thay child depart " + childDepartParam + " trong parent depart " + parentDepart)
                        hasRightOnChildDepart = True
                        break

                # Neu check xong trong child_depart_rights ma hasRightOnChildDepart van bang False thi check tiep trong branch_rights
                if hasRightOnChildDepart == False:
                    # print("[" + className + "] Khong co " + childDepartParam + " trong child_depart_rights, chuan bi tim trong branch_rights TIN")
                    # check tren TIN
                    if "ALL" in userPerData["branch_rights"]["TIN"]:
                        # print("[" + className + "] Co ALL trong branch_rights TIN")
                        for parent_depart, child_departs_by_parent in allDepartsWithLevels["allDeparts"][
                            "ALLTIN"].items():
                            # print("[" + className + "] Tim trong parent depart cua branch_rights TIN : " + parent_depart)
                            if childDepartParam in child_departs_by_parent:
                                # print("[" + className + "] Da tim thay child depart " + childDepartParam + " trong parent depart cua branch_rights TIN " + parent_depart)
                                hasRightOnChildDepart = True
                                break
                    else:
                        pass
                        # print("[" + className + "] Khong co ALL trong branch_rights TIN! Nen can tim tiep trong branch_rights PNC")

                    # Neu hasRightOnChildDepart van bang False thi check tren PNC
                    if hasRightOnChildDepart == False and "ALL" in userPerData["branch_rights"]["PNC"]:
                        # print("[" + className + "] hasRightOnChildDepart van bang false & co ALL trong branch_rights PNC")
                        for parent_depart, child_departs_by_parent in allDepartsWithLevels["allDeparts"][
                            "ALLPNC"].items():
                            # print("[" + className + "] Tim trong parent depart cua branch_rights PNC : " + parent_depart)
                            if childDepartParam in child_departs_by_parent:
                                # print("[" + className + "] Da tim thay child depart " + childDepartParam + " trong parent depart cua branch_rights PNC " + parent_depart)
                                hasRightOnChildDepart = True
                                break
                    else:
                        pass
                        # print("[" + className + "] hasRightOnChildDepart da bang True hoac khong co ALL trong branch_rights PNC")

                if hasRightOnChildDepart == False:
                    # print("[" + className + "] Permission " + userPerCode + " cua user nay KHONG duoc phep apply cho child depart " + childDepartParam)
                    hasRightOnChildDeparts = False
                    break
                else:
                    pass
                    # print("[" + className + "] Permission " + userPerCode + " cua user nay da duoc phep apply cho child depart " + childDepartParam)

            if hasRightOnChildDeparts == False:
                # print("[" + className + "] Permission " + userPerCode + " cua user nay KHONG duoc phep apply tren 1 hoac vai child depart trong param childDepart! Nen KHONG DUOC PHEP di tiep API!")
                excepRespondedData["message"] = "No right on child depart(s)"
                return JsonResponse(excepRespondedData)
            else:
                pass
                # print("[" + className + "] Permission " + userPerCode + " cua user nay DA DUOC PHEP apply tren tat ca child depart trong param childDepart!")
        else:
            pass
            # print("[" + className + "] Permisssion " + userPerCode + " KHONG can check quyen phong ban")

        # print("[" + className + "] Permission check hop le! Duoc phep di tiep API!")
        response = self.get_response(request)
        return response

    def checkChildDepartExistInParent(self, childDepart):
        pass

    def process_request(self, request):
        # print("vao process request")

        return None

    def process_response(self, request, response):
        # print('vao process response')

        return None
