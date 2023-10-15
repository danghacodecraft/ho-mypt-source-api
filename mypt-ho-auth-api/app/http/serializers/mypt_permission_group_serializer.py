from ..models.mypt_permission_group import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class MyPTPermissionGroupSerializer(ModelSerializer):
    permissionGroupId = serializers.IntegerField(source='permission_group_id')
    permissionGroupName = serializers.CharField(source='permission_group_name')
    permissionGroupCode = serializers.CharField(source='permission_group_code')
    childDepart = serializers.CharField(source='child_depart')
    dateDeleted = serializers.DateTimeField(source='date_deleted')
    dateCreated = serializers.DateTimeField(source='date_created')
    dateModified = serializers.DateTimeField(source='date_modified')
    isDeleted = serializers.IntegerField(source='is_deleted')
    updatedBy = serializers.IntegerField(source='updated_by')
    createdBy = serializers.IntegerField(source='created_by')

    class Meta:
        model = MyPTPermissionGroup
        fields = '__all__'
