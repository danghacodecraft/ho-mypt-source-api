from app.http.entities.user_infos_handler import UserInfosHandler
from app.core.entities.OAuth.token_handler import TokenHandler

class AccountCredentialsGrant:
    def genAuthorCode(self, userId, authData, grantId):
        return ""

    def verifyGenToken(self, authData, clientGrant):
        userId = int(authData.get("userId"))
        print("[AccountCredentialsGrant] lay duoc userId tu postData (authData) : " + str(userId))
        # get user by userId
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