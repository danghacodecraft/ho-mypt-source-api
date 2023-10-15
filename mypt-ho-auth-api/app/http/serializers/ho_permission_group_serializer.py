from app.http.models.ho_permission_group import *
from rest_framework.serializers import ModelSerializer

class HoPermissionGroupSerializer(ModelSerializer):
    class Meta:
        model = HoPermissionGroup
        fields = '__all__'
