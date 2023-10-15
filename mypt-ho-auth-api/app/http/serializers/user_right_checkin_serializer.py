from rest_framework import serializers

from app.http.models.user_right_checkin import *
from rest_framework.serializers import ModelSerializer


class UserRightCheckinSerializer(ModelSerializer):
    perId = serializers.CharField(source='per_id')
    childDepartRight = serializers.CharField(source='child_depart_right')

    class Meta:
        model = UserRightCheckin
        fields = ['email', 'perId', 'childDepartRight']