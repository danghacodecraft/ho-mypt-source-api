from app.http.models.ho_permission_with_route import *
from rest_framework.serializers import ModelSerializer

class HoPermissionWithRouteSerializer(ModelSerializer):
    class Meta:
        model = HoPermissionWithRoute
        fields = '__all__'
