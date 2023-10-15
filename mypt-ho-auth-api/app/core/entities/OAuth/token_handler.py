import uuid
from app.http.models.user_infos import UserInfos
from app.http.serializers.user_infos_serializer import UserInfosSerializer
from app.http.models.ho_oauth_access_token import HoOauthAccessToken
from app.http.models.ho_oauth_refresh_token import HoOauthRefreshToken
from datetime import datetime
from datetime import timedelta
from app.configs import app_settings
from app.core.entities.my_jwt import MyJwt
import redis
import random
from app.core.entities.centralized_session import CentralizedSession
from app.http.entities.oauth_access_token_handler import OauthAccessTokenHandler
from app.http.entities.oauth_refresh_token_handler import OauthRefreshTokenHandler

from app.http.apis.mypt_ho_profile_apis import MyPtHoProfileapis
from app.http.entities.permission_handler import *

class TokenHandler:
    def genTokenByUser(self, userInfo, authData, clientGrant):
        userId = int(userInfo.get("user_id"))
        caseRefreshToken = False
        refreshTokenId = ""
        if authData.get("refreshTokenId", None) is not None:
            caseRefreshToken = True
            refreshTokenId = str(authData.get("refreshTokenId"))
            print("case refresh token : " + refreshTokenId)
            # TAM THOI : revoke het cac Access Token theo userId va refreshTokenId nay de chuan bi tao Access Token moi
            self.revokeAccessTokensByRefreshToken(userId, refreshTokenId)
            # TODO: revoke het cac Access Token & Refresh Token hien tai cua userId nay (tru refreshTokenId ra) neu muon tai 1 thoi diem, 1 email chi login tren 1 device duy nhat
            # self.revokeTokens(userId, True, refreshTokenId)
        else:
            print("case tao access token MOI")
            # TODO: revoke het cac Access Token & Refresh Token hien tai cua userId nay neu muon tai 1 thoi diem, 1 email chi login tren 1 device duy nhat
            # self.revokeTokens(userId, False, "")

        # TAO access token
        accessTokenModel = HoOauthAccessToken()
        accessTokenModel.id = self.genUuidForToken("createAccessToken", userId)
        newAccessTokenId = accessTokenModel.id

        accessTokenModel.user_id = userId
        accessTokenModel.client_id = str(clientGrant.get("client_id"))
        # Neu day la case "Tao lai Access Token tu Refresh Token"
        if caseRefreshToken == True:
            print("case refresh token 123")
            accessTokenModel.refresh_token_id = refreshTokenId
        # set cac field con lai
        # accessTokenModel.device_id = userInfo.get("device_id")
        # accessTokenModel.device_name = userInfo.get("device_name")
        # accessTokenModel.device_token = userInfo.get("device_token")
        # accessTokenModel.device_platform = userInfo.get("device_platform")
        accessTokenModel.grant_id = int(clientGrant.get("grant_id"))
        accessTokenModel.revoked = 0

        # set expires_at
        curDt = datetime.now()
        accessTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_ACCESS_TOKEN)
        accessTokenModel.expires_at = accessTokenExpiredDt.strftime("%Y-%m-%d %H:%M:%S")
        # save
        resCreateAccessToken = accessTokenModel.save()

        # TAO refresh token neu day la case "Tao Access Token moi" (khong danh cho case "Tao lai Access Token tu Refresh Token")
        if caseRefreshToken == False:
            refreshTokenModel = HoOauthRefreshToken()
            refreshTokenModel.id = self.genUuidForToken("createRefreshToken", userId)
            refreshTokenId = refreshTokenModel.id
            refreshTokenModel.user_id = userId
            refreshTokenModel.access_token_id = newAccessTokenId
            refreshTokenModel.client_id = str(clientGrant.get("client_id"))
            refreshTokenModel.revoked = 0
            refreshTokenExpiredDt = curDt + timedelta(minutes=app_settings.EXPIRES_AT_REFRESH_TOKEN)
            refreshTokenModel.expires_at = refreshTokenExpiredDt.strftime("%Y-%m-%d %H:%M:%S")
            resCreateRefreshToken = refreshTokenModel.save()
            # lay refresh token moi tao de update vao cot refresh_token_id cua bang oauth_access_tokens
            HoOauthAccessToken.objects.filter(id=newAccessTokenId).update(refresh_token_id=refreshTokenId, updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            # update lai cot access_token_id voi newAccessTokenId cho row oauth_refresh_tokens
            HoOauthRefreshToken.objects.filter(id=refreshTokenId).update(access_token_id=newAccessTokenId, updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # TODO: Luu vao redis, voi key là AccessTokenId
        if authData.get("isSaveCentralizedStorage") == True:
            resSaveCenSession = self.saveCentralizedSession({
                "id": newAccessTokenId,
                "expiresAt": accessTokenExpiredDt
            }, clientGrant, userInfo, authData)
            if resSaveCenSession.get("resSave") == False:
                return None

        # return
        jwtObj = MyJwt()
        return {
            "accessToken": jwtObj.createJtiToken(newAccessTokenId, {
                "issuedAt": int(curDt.timestamp()),
                "expiration": int(accessTokenExpiredDt.timestamp())
            }),
            "refreshToken": jwtObj.createJtiToken(refreshTokenId),
            "jti": newAccessTokenId
        }

    # revoke het cac Access Token & Refresh Token hien tai cua userId truyen vao
    # Neu day la case "Refresh token" (caseRefreshToken = True) : ko xoa row oauth_refresh_tokens cua refreshTokenId nay
    def revokeTokens(self, userId, caseRefreshToken = False, refreshTokenId = ""):
        # Lay ra cac access token (voi revoked = 0) cua userId nay
        oatHandler = OauthAccessTokenHandler()
        accessTokenObjs = oatHandler.getUnRevokedAccessTokensByUser(userId)
        # revoke cac access token cua userId nay
        resRevokeAccessTokens = oatHandler.revokeAccessTokensByUser(userId)
        # revoke cac refresh token cua userId nay
        # CHU Y : Neu day la case "Refresh token" (caseRefreshToken = True) : ko xoa row oauth_refresh_tokens cua refreshTokenId nay
        ortHandler = OauthRefreshTokenHandler()
        if caseRefreshToken == True and refreshTokenId != "":
            resRevokeRefreshTokens = ortHandler.revokeRefreshTokensByUser(userId, refreshTokenId)
        else:
            resRevokeRefreshTokens = ortHandler.revokeRefreshTokensByUser(userId)

        # xoa het data cac access token cua userId nay trong Redis
        if accessTokenObjs is not None:
            cenSessionObj = CentralizedSession()
            for accessTokenObj in accessTokenObjs:
                cenSessionObj.removeSession(accessTokenObj.get("id"))


    def revokeAccessTokensByRefreshToken(self, userId, refreshTokenId):
        print("[revokeAccessTokensByRefreshToken] revoke het cac access token cua refresh token : " + refreshTokenId + " va userId : " + str(userId))
        # Lay ra cac access token dang co refreshTokenId nay
        oatHandler = OauthAccessTokenHandler()
        accessTokenObjs = oatHandler.getAccessTokensByRefreshTokenId(userId, refreshTokenId)
        # update revoked thanh 1 trong DB
        resRevokeAccessToken = HoOauthAccessToken.objects.filter(user_id=userId, refresh_token_id=refreshTokenId, revoked=0).update(revoked=1, updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # TODO: xoa het cac key (la cac access token thuoc refreshTokenId) trong Redis
        cenSessionObj = CentralizedSession()
        for accessTokenObj in accessTokenObjs:
            cenSessionObj.removeSession(accessTokenObj.get("id"))

        return {
            "resRevoke": True
        }

    def saveCentralizedSession(self, accessTokenInfo, clientGrant, userInfo, authData):
        sessionData = {
            "clientId": str(clientGrant.get("client_id")),
            "grantId": int(clientGrant.get("grant_id")),
            "userId": int(userInfo.get("user_id")),
            "email": userInfo.get("email"),
            "fullName": userInfo.get("full_name"),
            "isTinPncEmployee": 0,
            "branch": "",
            "empCode": "",
            "empContractType": "",
            "childDepart": "",
            "parentDepart": "",
            "isHOEmp": 0,
            "jobTitle": "",
            "empAvatarImageUrl": "",
            "permissions": {},
            "featuresRoles": {}
        }

        # Tap hop cac phong ban (child_depart) ma user nay co quyen tuong tac de gui qua mypt-ho-profile-api de lay parent_depart, branch cua tung child_depart
        perHandler = PermissionHandler()
        persData = perHandler.getAllPermissionsByUser(int(userInfo.get("user_id")))
        permissionsData = persData.get("persData")

        print("pers Data : ")
        print(permissionsData)

        # Goi API ben mypt-ho-profile-api de lay thong tin profile, employee cua user nay
        profileapis = MyPtHoProfileapis()
        profileInfoData = profileapis.getProfileInfo(int(userInfo.get("user_id")), userInfo.get("email"), userInfo.get("full_name"), {"specificChildDeparts": persData.get("collectedSpecificChildDeparts")})
        print(profileInfoData)
        if profileInfoData is not None:
            sessionData["isTinPncEmployee"] = int(profileInfoData.get("isTinPncEmployee"))
            sessionData["branch"] = str(profileInfoData.get("branch"))
            sessionData["empCode"] = str(profileInfoData.get("empCode"))
            sessionData["empContractType"] = str(profileInfoData.get("empContractType"))
            sessionData["childDepart"] = str(profileInfoData.get("childDepart"))
            sessionData["parentDepart"] = str(profileInfoData.get("parentDepart"))
            sessionData["isHOEmp"] = int(profileInfoData.get("isHO"))
            sessionData["jobTitle"] = str(profileInfoData.get("jobTitle"))
            sessionData["empAvatarImageUrl"] = str(profileInfoData.get("empAvatarImageUrl", ""))
            sessionData["featuresRoles"] = profileInfoData.get("featuresRoles", {})
            # xu ly branchParentDeparts
            branchParentDeparts = profileInfoData.get("branchParentDeparts", None)
            if branchParentDeparts is not None:
                for perCode, perData in permissionsData.items():
                    specificChildDeparts = perData.get("specificChildDeparts")
                    if len(specificChildDeparts) > 0:
                        for specificChildDepart in specificChildDeparts:
                            childDepartLevelData = branchParentDeparts.get(specificChildDepart, None)
                            if childDepartLevelData is not None:
                                parent_depart = childDepartLevelData["parentDepart"]
                                branchStr = childDepartLevelData["branch"]
                                if parent_depart not in perData["branch_rights"][branchStr]:
                                    perData["branch_rights"][branchStr].append(parent_depart)
                                if perData["child_depart_rights"].get(parent_depart, None) is None:
                                    perData["child_depart_rights"][parent_depart] = []
                                if specificChildDepart not in perData["child_depart_rights"][parent_depart]:
                                    perData["child_depart_rights"][parent_depart].append(specificChildDepart)

                    # Da su dung xong specificChildDeparts, xoa no khoi perData
                    perData.pop("specificChildDeparts")
            else:
                print("branchParentDeparts is null, xoa specificChildDeparts trong permissionsData")
                for perCode, perData in permissionsData.items():
                    perData.pop("specificChildDeparts")
        else:
            for perCode, perData in permissionsData.items():
                perData.pop("specificChildDeparts")

        print(permissionsData)
        sessionData["permissions"] = permissionsData

        expiresAtTs = int(accessTokenInfo.get("expiresAt").timestamp())
        seconds = expiresAtTs - int(datetime.now().timestamp())
        print("so giay cho redis key nay la : " + str(seconds))

        cenSessionObj = CentralizedSession()
        resSaveSession = cenSessionObj.saveSession(accessTokenInfo.get("id"), sessionData, seconds)
        return resSaveSession

    def genUuidForToken(self, tokenType, userId):
        uuidStr = uuid.uuid4()
        return str(uuidStr)

        # rdNum = random.randint(1, 9999999)
        # strForUuid = tokenType + str(userId) + "_" + str(datetime.now().timestamp()) + "-" + str(rdNum)
        # uuidStr = uuid.uuid5(uuid.NAMESPACE_DNS, strForUuid)
        # return str(uuidStr)