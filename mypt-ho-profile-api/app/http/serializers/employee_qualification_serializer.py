from rest_framework import serializers
from ..models.employee_qualification import EmployeeQualification

class EmployeeQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeQualification
        fields = "__all__"
