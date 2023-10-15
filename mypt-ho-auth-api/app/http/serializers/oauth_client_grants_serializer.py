from app.http.models.oauth_client_grants import OauthClientGrants
from rest_framework.serializers import ModelSerializer

class OauthClientGrantsSerializer(ModelSerializer):
    class Meta:
        model = OauthClientGrants
        fields = '__all__'
