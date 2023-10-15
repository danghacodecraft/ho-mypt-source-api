from app.http.models.user_infos import UserInfos
from app.http.serializers.user_infos_serializer import UserInfosSerializer
from app.http.entities.oauth_access_token_handler import OauthAccessTokenHandler
from app.http.entities.oauth_refresh_token_handler import OauthRefreshTokenHandler
from app.core.entities.centralized_session import CentralizedSession

class AuthenHandler:
    def __init__(self):
        pass

    def doLogout(self, accessTokenJti):
        if accessTokenJti is None:
            return {
                "result": False,
                "errorCode": "ACCESS_TOKEN_JTI_NOT_FOUND"
            }
        accessTokenJti = str(accessTokenJti)

        # print("chuan bi tim user theo userId : " + accessTokenJti)
        # usQs = UserInfos.objects.filter(user_id=userId)[0:1]
        # userInfo_ser = UserInfosSerializer(usQs, many=True)
        # usersArr = userInfo_ser.data
        # if len(usersArr) <= 0:
        #     return {
        #         "result": False,
        #         "errorCode": "USER_NOT_FOUND"
        #     }
        # userInfo = usersArr[0]

        # Tim access token theo ID (accessTokenJti) de remove no
        print("chuan bi tim access token theo JTI : " + accessTokenJti)
        oatHandler = OauthAccessTokenHandler()
        oatRow = oatHandler.getAccessTokenById(accessTokenJti)
        if oatRow is None:
            return {
                "result": False,
                "errorCode": "ACCESS_TOKEN_NOT_FOUND"
            }

        # revoke access token nay
        resRevokeAccessToken = oatHandler.revokeAccessTokenById(accessTokenJti)
        # revoke refresh token
        ortHandler = OauthRefreshTokenHandler()
        resRevokeRefreshToken = ortHandler.revokeRefreshTokenById(oatRow.get("refresh_token_id"))

        # xoa key Access Token JTI trong Redis
        cenSessionObj = CentralizedSession()
        resRemoveRedisSession = cenSessionObj.removeSession(accessTokenJti)

        return {
            "result": True,
            "resRevokeAccessToken": resRevokeAccessToken,
            "resRevokeRefreshToken": resRevokeRefreshToken,
            "resRemoveRedisSession": resRemoveRedisSession
        }