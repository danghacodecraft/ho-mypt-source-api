from re import L
from rest_framework import serializers

from ...http.models.ptq import *


class PtqValidate(serializers.Serializer):
    childDepart = serializers.ListField(required=True)
    controlMonth = serializers.CharField(required=True)

class StatusValidate(serializers.Serializer):
    status = serializers.IntegerField(required=True)
    
    # def validate_status(self, value):
    #     queryset = PtqType.objects.filter(type__in=['OK', 'NOTOK', 'CANCEL', 'ADD']).values_list("id", flat=True)
    #     if value not in list(queryset):
    #         raise serializers.ValidationError("Status " + str(value) + " không nằm trong " + str(queryset))
    #     return value
  
class PtqImportValidate(serializers.Serializer):
    date_complete = serializers.CharField(required=True)
    date_check = serializers.CharField(required=True)
    deadline = serializers.CharField(required=True)
    region = serializers.CharField(required=True)
    partner = serializers.CharField(required=True)
    block_name = serializers.CharField(required=True)
    emp_name = serializers.CharField(required=True)
    MBN_account_name = serializers.CharField(required=True)
    emp_code = serializers.CharField(required=True)
    contract = serializers.CharField(required=True)
    error_type = serializers.CharField(required=True)
    duration_check = serializers.CharField(required=True)
    error_main = serializers.CharField(required=True)
    error_group = serializers.CharField(required=True)
    error_description = serializers.CharField(required=True)
    error_detail = serializers.CharField(required=True)
    punishment = serializers.CharField(required=True)
    error_number = serializers.CharField(required=True)
    uuid = serializers.CharField(required=True)
    update_by = serializers.CharField(required=True)
    
class GetToolChildDepartValidate(serializers.Serializer): 
    childDepart = serializers.ListField(required=True)
    
class EmailListValidate(serializers.Serializer):
    email = serializers.ListField(required=True)
    
class CodeListValidate(serializers.Serializer):
    code = serializers.ListField(required=True)

class ContractListValidate(serializers.Serializer):
    contract = serializers.ListField(required=True)

class IdValidate(serializers.Serializer):
    id = serializers.IntegerField()

class IdListValidate(serializers.Serializer):
    id = serializers.ListField()
    
class DateReportValidate(serializers.Serializer):
    dateStart = serializers.DateField()
    dateEnd = serializers.DateField()
    
class MonthValidate(serializers.Serializer):
    month = serializers.IntegerField()
    
class DateValidate(serializers.Serializer):
    dateStart = serializers.DateField(format="%Y-%m-%d")
    dateEnd = serializers.DateField(format="%Y-%m-%d")
    
class ListTypeValidate(serializers.Serializer):
    typeId = serializers.ListField()
    
    def validate_typeId(self, value):
        if value == []:
            raise serializers.ValidationError("typeId không có dữ liệu []")
        return value
    
class ExplanationValidate(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()
    
class DeleteReasonPtqValidate(serializers.Serializer):
    reason = serializers.CharField()

class NoteValidate(serializers.Serializer):
    note = serializers.CharField()
    
class ArrayValidate(serializers.Serializer):
    array = serializers.ListField()