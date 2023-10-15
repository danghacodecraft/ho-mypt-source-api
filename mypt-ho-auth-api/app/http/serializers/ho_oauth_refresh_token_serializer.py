from app.http.models.ho_oauth_refresh_token import HoOauthRefreshToken
from rest_framework.serializers import ModelSerializer

class HoOauthRefreshTokenSerializer(ModelSerializer):
    class Meta:
        model = HoOauthRefreshToken
        fields = '__all__'
