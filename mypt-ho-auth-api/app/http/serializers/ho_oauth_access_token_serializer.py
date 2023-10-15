from app.http.models.ho_oauth_access_token import HoOauthAccessToken
from rest_framework.serializers import ModelSerializer

class HoOauthAccessTokenSerializer(ModelSerializer):
    class Meta:
        model = HoOauthAccessToken
        fields = '__all__'
