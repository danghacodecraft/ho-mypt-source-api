from rest_framework import serializers
from ..models.employee import *


class EmployeeSerializer(serializers.ModelSerializer):
    empName = serializers.CharField(source='emp_name')
    jobTitle = serializers.CharField(source='job_title')
    childDepart = serializers.CharField(source='child_depart')
    contractType = serializers.CharField(source='contract_type')

    class Meta:
        model = Employee
        fields = ['email', 'empName', 'jobTitle', 'childDepart', 'contractType']


class HomeEmployeeSerializer(serializers.HyperlinkedModelSerializer):
    empCode = serializers.CharField(source='emp_code')
    name = serializers.CharField(source='emp_name')
    avatarImg = serializers.CharField(source='avatar_img')

    class Meta:
        model = Employee
        # It is strongly recommended that you explicitly set all fields that should be serialized using the fields attribute
        # fields = ['emp_code', 'MBN_account_name', 'block_name', 'device_id', 'toa_do_van_phong', 'toa_do_kho', 'toa_do_lam_viec', 'ban_kinh_lam_viec', 'acctive_time']
        fields = ['empCode','name','avatarImg']


class CodeEmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = ['emp_code']


