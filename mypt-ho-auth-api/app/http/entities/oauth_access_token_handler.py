from app.http.models.ho_oauth_access_token import HoOauthAccessToken
from app.http.serializers.ho_oauth_access_token_serializer import HoOauthAccessTokenSerializer
from datetime import datetime

class OauthAccessTokenHandler:
    def getAccessTokensByRefreshTokenId(self, userId, refreshTokenId):
        print("chuan bi tim cac AccessToken theo RefreshTokenId : " + str(userId) + " ; " + refreshTokenId)
        oatQs = HoOauthAccessToken.objects.filter(user_id=userId, refresh_token_id=refreshTokenId, revoked=0)
        oat_ser = HoOauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def getUnRevokedAccessTokensByUser(self, userId):
        print("chuan bi tim cac AccessToken theo UserId : " + str(userId))
        oatQs = HoOauthAccessToken.objects.filter(user_id=userId, revoked=0)
        oat_ser = HoOauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr
        else:
            return None

    def revokeAccessTokensByUser(self, userId):
        rowsUpdated = HoOauthAccessToken.objects.filter(user_id=userId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated

    def getAccessTokenById(self, accessTokenId):
        print("chuan bi tim row AccessToken theo ID : " + accessTokenId)
        oatQs = HoOauthAccessToken.objects.filter(id=accessTokenId)[0:1]
        oat_ser = HoOauthAccessTokenSerializer(oatQs, many=True)
        oatArr = oat_ser.data
        if len(oatArr) > 0:
            return oatArr[0]
        else:
            return None

    def revokeAccessTokenById(self, accessTokenId):
        rowsUpdated = HoOauthAccessToken.objects.filter(id=accessTokenId, revoked=0).update(revoked=1,updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return rowsUpdated