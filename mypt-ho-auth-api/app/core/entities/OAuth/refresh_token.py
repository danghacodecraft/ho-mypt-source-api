from app.http.entities.oauth_refresh_token_handler import OauthRefreshTokenHandler
from app.http.entities.user_infos_handler import UserInfosHandler
from app.core.entities.OAuth.token_handler import TokenHandler
from app.core.entities.my_jwt import MyJwt
from datetime import datetime
from app.http.models.ho_oauth_refresh_token import HoOauthRefreshToken

class RefreshToken:
    def verifyGenToken(self, authData, clientGrant):
        # check param refreshToken trong POST data (authData)
        if authData.get("refreshToken", None) is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }

        jwtObj = MyJwt()
        # decode refreshToken de lay jti (refresh token id)
        refreshTokenPayloadData = jwtObj.decodeJwtToken(str(authData.get("refreshToken")))
        if refreshTokenPayloadData is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        if refreshTokenPayloadData.get("jti", None) is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        refreshTokenId = refreshTokenPayloadData.get("jti")
        # check refresh token id nay co trong bang oauth_refresh_tokens hay ko
        ortHandler = OauthRefreshTokenHandler()
        refreshTokenInfo = ortHandler.getRefreshTokenById(refreshTokenId)
        if refreshTokenInfo is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        if int(refreshTokenInfo.get("revoked")) == 1:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }
        # check expires_at cua refreshTokenInfo de xem refresh token nay co het han chua
        rtExpireStr = refreshTokenInfo.get("expires_at")
        print(rtExpireStr)
        rtExpireStr = rtExpireStr.replace("T", " ").replace("Z", "")
        print(rtExpireStr)
        rtExpireDt = datetime.strptime(rtExpireStr, "%Y-%m-%d %H:%M:%S")
        rtExpireTs = int(rtExpireDt.timestamp())
        curTs = int(datetime.now().timestamp())
        print("refresh token expire ts : " + str(rtExpireTs) + " ; " + str(curTs))
        if rtExpireTs <= curTs:
            print("Refresh token expired!")
            # update cot revoked cua Refresh Token nay thanh 1
            HoOauthRefreshToken.objects.filter(id=refreshTokenInfo.get("id")).update(revoked=1, updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # return
            return {
                "resGen": False,
                "errorCode": "RESPONSE_REFRESH_TOKEN_FAILED",
                "data": None
            }

        # Lay thong tin user tu cot user_id trong bang oauth_refresh_tokens
        userId = int(refreshTokenInfo.get("user_id"))
        userInfosHandlerObj = UserInfosHandler()
        userInfo = userInfosHandlerObj.getUserByUserId(userId)
        if userInfo is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_USER_NOT_FOUND_BY_USER_ID",
                "data": None
            }

        tokenHandlerObj = TokenHandler()
        # chuan bi data de tao token
        newAuthData = {
            "refreshTokenId": refreshTokenInfo.get("id"),
            "isSaveCentralizedStorage": True
        }
        resultGetToken = tokenHandlerObj.genTokenByUser(userInfo, newAuthData, clientGrant)
        print(resultGetToken)

        if resultGetToken is None:
            return {
                "resGen": False,
                "errorCode": "RESPONSE_GEN_TOKEN_FAILED",
                "data": None
            }

        return {
            "resGen": True,
            "errorCode": None,
            "data": resultGetToken
        }