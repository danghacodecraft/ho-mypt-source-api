from rest_framework import serializers
from datetime import datetime
from app.core.helpers.utils import *


class EmployeeValidate(serializers.Serializer):
    empName = serializers.CharField(required=False, default="")
    empMail = serializers.EmailField(required=False, default="")
    empCode = serializers.CharField(required=False, default="")

class RequiredEmployeeCodeValidate(serializers.Serializer):
    employee_code = serializers.CharField(required=True)
