from rest_framework.serializers import *
from datetime import datetime
from app.core.helpers.utils import *


class DepartmentValidate(Serializer):
    # empCode = CharField(allow_null=True, allow_blank=False)
    parentDepart = CharField(allow_null=False, allow_blank=False)
    chiNhanh = CharField(allow_null=False, allow_blank=False)
    childDepart = CharField(allow_null=False, allow_blank=False)
    branch = CharField(allow_null=False, allow_blank=False)
    oldChildDepart = CharField(allow_null=True, allow_blank=True)

    # def validate_empCode(self, value):
    #     if value == "" or value is None:
    #         raise ValidationError("Mã nhân viên không được để trống")
    #     if len(value) != 8:
    #         raise ValidationError("Mã nhân viên phải đủ 8 số!")

    # def validate_empCode(self, empCode):
    #     if len(str(empCode)) != 8:
    #         empCode = str(empCode).zfill(8)
    #     return empCode
