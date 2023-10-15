from ..models.mypt_permission import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class MyPTPermissionSerializer(ModelSerializer):
    permissionId = serializers.IntegerField(source='permission_id')
    permissionName = serializers.CharField(source='permission_name')
    permissionCode = serializers.CharField(source='permission_code')
    permissionGroupId = serializers.IntegerField(source='permission_group_id')
    hasDepartRight = serializers.IntegerField(source='has_depart_right')
    dateDeleted = serializers.DateTimeField(source='date_deleted')
    dateCreated = serializers.DateTimeField(source='date_created')
    dateModified = serializers.DateTimeField(source='date_modified')
    isDeleted = serializers.IntegerField(source='is_deleted')
    updatedBy = serializers.IntegerField(source='updated_by')
    createdBy = serializers.IntegerField(source='created_by')

    class Meta:
        model = MyPTPermission
        fields = '__all__'
