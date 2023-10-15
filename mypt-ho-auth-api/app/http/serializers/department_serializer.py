from rest_framework import serializers
from ..models.department import *


class DepartmentSerializer(serializers.ModelSerializer):
    parentDepart = serializers.CharField(source='parent_depart')

    class Meta:
        model = Department
        fields = ['parentDepart']
