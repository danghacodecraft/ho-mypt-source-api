from app.http.models.oauth_grants import OauthGrants
from rest_framework.serializers import ModelSerializer

class OauthGrantsSerializer(ModelSerializer):
    class Meta:
        model = OauthGrants
        fields = '__all__'
