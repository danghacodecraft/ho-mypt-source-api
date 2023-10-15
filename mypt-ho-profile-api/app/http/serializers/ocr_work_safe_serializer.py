from rest_framework import serializers
from ..models.ocr_work_safe import *

class OcrWorkSafeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="atld_id", required=False)
    empCode = serializers.CharField(source="emp_code", required=False, allow_blank=True, allow_null=True)
    trainingGroup = serializers.CharField(source="nhom_dao_tao", required=False, allow_blank=True, allow_null=True)
    certificate = serializers.CharField(source="cap_the_chung_chi", required=False,  allow_null=True, allow_blank=True)
    dateCertificate = serializers.DateField(format='%d/%m/%Y', source="ngay_cap_the_ATLD", required=False, allow_null=True)
    expirationDate = serializers.DateField(format='%d/%m/%Y', source="ngay_het_han_ATLD", required=False, allow_null=True)
    trainingStartDate = serializers.DateField(format='%d/%m/%Y', source="ngay_bat_dau_dao_tao", required=False, allow_null=True)
    trainingEndDate = serializers.DateField(format='%d/%m/%Y', source="ngay_ket_thuc_dao_tao", required=False, allow_null=True)
    statusCertificate = serializers.CharField(source="tinh_trang_the_chung_chi", required=False)
    pictureCertificate = serializers.CharField(source="hinh_anh_the_chung_nhan", required=False, allow_null=True, allow_blank=True)
    updateTime = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', source="update_time_atld", required=False)
    active = serializers.IntegerField(required=False, allow_null=True)
    numberCard = serializers.CharField(source='number_card', required=False, allow_null=True, allow_blank=True)
    updateBy = serializers.CharField(source="update_by", required=False)
    createdBy = serializers.CharField(source="created_by", required=False, allow_null=True, allow_blank=True)
    createdAt = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', source="created_time", required=False)
    confirm = serializers.IntegerField(required=False, allow_null=True)
    statusFile = serializers.IntegerField(source='status_file', required=False, allow_null=True)
    jobTitle = serializers.CharField(source='job_title', required=False, allow_null=True, allow_blank=True)
    # typeProvide = serializers.CharField(source='typeProvide', required=False)
    # department = DepartmentSerializer(fields = ['childDepart','branch','parentDepart','childDepart1','dienGiai','codeChildDepart','emp_info'])

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        VN = kwargs.pop('VN', None)

        super().__init__(*args, **kwargs)

        # if not emp:
        #     self.fields.pop("emp_info")
        #     # self.fields.pop("department")

        # data = self.fields.pop("emp_info")
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if VN is not None:
            fields = []
            for key in VN:
                fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)
            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = OcrWorkSafe
        fields = [
            "id", "empCode", "trainingGroup", "certificate",
            "dateCertificate", "expirationDate", "trainingStartDate",
            "trainingEndDate", "statusCertificate", "pictureCertificate",
            "updateTime", "updateBy",  "active", "numberCard", "createdBy", "createdAt", 'confirm', 'statusFile', "jobTitle"
        ]

