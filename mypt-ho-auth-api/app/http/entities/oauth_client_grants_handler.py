from app.http.models.oauth_client_grants import OauthClientGrants
from app.http.serializers.oauth_client_grants_serializer import OauthClientGrantsSerializer

class OauthClientGrantsHandler:
    def findByGrantIdAndClientId(self, grantId, clientId):
        print("chuan bi tim oauth_client_grants row theo : " + str(grantId) + " va " + clientId)
        cgQs = OauthClientGrants.objects.filter(grant_id=grantId, client_id=clientId)[0:1]
        ocg_ser = OauthClientGrantsSerializer(cgQs, many=True)
        clientGrantArr = ocg_ser.data
        # print(clientGrantArr)
        if len(clientGrantArr) > 0:
            clientGrantItem = clientGrantArr[0]
            print(clientGrantItem)
            return clientGrantItem
        else:
            return None