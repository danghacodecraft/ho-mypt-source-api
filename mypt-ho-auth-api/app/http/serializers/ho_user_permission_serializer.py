from rest_framework import serializers

from app.http.models.ho_user_permission import *
from rest_framework.serializers import ModelSerializer


class HoUserPermissionSerializer(ModelSerializer):
    userId = serializers.IntegerField(source='user_id')
    permissionId = serializers.IntegerField(source='permission_id')
    permissionCode = serializers.CharField(source='permission_code')
    childDepart = serializers.CharField(source='child_depart')
    dateCreated = serializers.DateTimeField(source='date_created')
    dateModified = serializers.DateTimeField(source='date_modified')
    updatedBy = serializers.IntegerField(source='updated_by')
    createdBy = serializers.IntegerField(source='created_by')

    class Meta:
        model = HoUserPermission
        fields = '__all__'