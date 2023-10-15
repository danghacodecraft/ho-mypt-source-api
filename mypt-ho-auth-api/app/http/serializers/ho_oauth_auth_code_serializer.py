from app.http.models.ho_oauth_auth_code import HoOauthAuthCode
from rest_framework.serializers import ModelSerializer

class HoOauthAuthCodeSerializer(ModelSerializer):
    class Meta:
        model = HoOauthAuthCode
        fields = '__all__'
