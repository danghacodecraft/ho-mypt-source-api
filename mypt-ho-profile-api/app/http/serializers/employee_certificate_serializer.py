from rest_framework import serializers
from ..models.employee_certificate import EmployeeCertificate

class EmployeeCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCertificate
        fields = "__all__"