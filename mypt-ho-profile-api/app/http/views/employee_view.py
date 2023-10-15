from rest_framework.viewsets import ViewSet
from ...core.helpers.response import *
from django.db.models import Q
from ..models.hr import Employee
from ..serializers.hr_serializer import EmployeeSerializer
from .. validations import employee_validate
from ...configs.excel_table import EMPLOYEE_JOB
from django.core.cache import cache

class EmployeeView(ViewSet):
    def filteration_condition(self, request):
        data = request.data.copy()
        data_item = employee_validate.EmployeeValidate(data=data)
        data_item.is_valid()
        data_item = data_item.data
        queryset = Employee.objects.filter()
        if data_item['empName'] == data_item['empMail'] == data_item['empCode'] == "":
            if "childDepart" in data and len(data['childDepart'])>0:
                queryset = queryset.filter(child_depart__in=data["childDepart"])
            if "mail" in data and len(data['mail'])>0:
                queryset = queryset.filter(email__in=data["mail"])
            serializer = EmployeeSerializer(queryset, many=True, VN=EMPLOYEE_JOB, fields=EMPLOYEE_JOB.keys())
            return response_data(serializer.data)
        if data_item['empName'] != "":
            queryset = queryset.filter(emp_name__contains=data_item['empName'])
        if data_item['empMail'] != "":
            queryset = queryset.filter(email=data_item['empMail'])
        if data_item['empCode'] != "":
            queryset = queryset.filter(emp_code=data_item['empCode'])
        serializer = EmployeeSerializer(queryset, many=True, VN=EMPLOYEE_JOB, fields=EMPLOYEE_JOB.keys())
        return response_data(serializer.data)

    def all_distinct_emp(self, request):
        data = request.data.copy()
        return self.set_group_key(data)
        
    def set_group_key(self, data):
        key_redis = data.get('key_redis', 'all_job_title')
        result = []
        try:
            value_redis = data.get('field', 'job_title')
            _where = {str(value_redis)+'__isnull':False}
            queryset = Employee.objects.filter(**_where).values_list(value_redis,flat=True)
            distinct_data = list(set(queryset))
            cache.set(key_redis, distinct_data, version='employee', timeout=None)
            result = cache.get(key=key_redis, version='employee')
            return response_data(result)
        except:
            return response_data(status=5, message="check lai input")
        
    def all_group_emp(self, request):
        data = request.data.copy()
        result = []
        key_redis = str(data.get('key_redis', 'job_title'))
        field = str(data.get('field', 'email'))
        group = cache.get(key='all_'+key_redis, version='employee')
        if group is None:
            self.set_group_key({'key_redis':'all_'+key_redis, 'field':key_redis})
            group = cache.get(key='all_'+key_redis, version='employee')
            
        for item in group:
            value = cache.get(key_redis+':'+item, version='employee')
            if value is None:
                _where = {key_redis:item, field+'__isnull':False}
                queryset = Employee.objects.filter(**_where).values_list(field, flat=True)
                distinct_data = list(set(queryset))
                cache.set(key_redis+':'+item, {field: distinct_data}, version='employee', timeout=None)
                value = cache.get(key_redis+':'+item, version='employee')
                field_exists = value.get(field, None)
            else:
                field_exists = value.get(field, None)
            if field_exists is None:
                _where = {key_redis:item, field+'__isnull':False}
                queryset = Employee.objects.filter(**_where).values_list(field, flat=True)
                distinct_data = list(set(queryset))
                cache.set(key_redis+':'+item, {**value,**{field: distinct_data}}, version='employee', timeout=None)
            value = cache.get(key_redis+':'+item, version='employee')
            
            result.append({
                key_redis: item,
                field: value.get(field, [])
            })
        return response_data(result)
    
    