from rest_framework import serializers
from ..models.ptq import *
from datetime import datetime
from ...configs.variable import *

class PtqSerializer(serializers.ModelSerializer):
    region = serializers.CharField(required=False, allow_null=True)
    partner = serializers.CharField(required=False, allow_null=True)
    blockName = serializers.CharField(source="block_name", required=False, allow_null=True)
    empName = serializers.CharField(source="emp_name", required=False, allow_null=True)
    contract = serializers.CharField(required=False, allow_null=True)
    errorType = serializers.CharField(source="error_type", required=False, allow_null=True)
    dateComplete = serializers.DateTimeField(format=DATETIME_FORMAT ,source="date_complete", required=False, allow_null=True)
    errorMain = serializers.CharField(source="error_main", required=False, allow_null=True)
    errorGroup = serializers.CharField(source="error_group", required=False, allow_null=True)
    errorDescription = serializers.CharField(source="error_description", required=False, allow_null=True)
    errorDetail = serializers.CharField(source="error_detail", required=False, allow_null=True)
    punishment = serializers.IntegerField(required=False, allow_null=True)
    accountMbn = serializers.CharField(source="account_mbn", required=False, allow_null=True)
    dateCheck = serializers.DateField(format=DATE_FORMAT, source="date_check", required=False, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)
    errorNumber = serializers.IntegerField(source="error_number", required=False, allow_null=True)
    deadline = serializers.DateField(format=DATE_FORMAT, required=False, allow_null=True)
    recorded = serializers.IntegerField(required=False, allow_null=True)
    recordedName = serializers.CharField(required=False, allow_null=True, source="get_type")
    note = serializers.CharField(required=False, allow_null=True)
    durationCheck = serializers.DateField(format="%m/%Y", source="date_check", required=False, allow_null=True)
    thematic = serializers.CharField(required=False, allow_null=True)
    isRead = serializers.BooleanField(source="is_read", required=False, allow_null=True)
    updatedBy = serializers.CharField(source="updated_by", required=False, allow_null=True)
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        VN = kwargs.pop('VN', None)
        explanation = kwargs.pop('explanation', False)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)                
        if VN is not None:
            fields = list(VN.keys())
            # for key in VN:
            #     fields.append(key)
            existing = set(self.fields)
            allowed = set(fields)
            for field_name in fields:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if explanation:
            self.fields["isDelete"] = serializers.BooleanField(default=False)
            self.fields["isEdit"] = serializers.BooleanField(default=False)
                
                    
    class Meta:
        model = Ptq
        fields = [
            "id","region","partner","blockName","empName","contract",
            "errorType","dateComplete","errorMain","errorGroup",
            "errorDescription","errorDetail","punishment",
            "accountMbn","dateCheck","email","errorNumber",
            "deadline","recorded","note","thematic","updatedBy",
            "createdAt","updatedAt","deletedAt","isRead","recordedName",
            "durationCheck", "explanation"
        ]

class OldPtqSerializer(serializers.ModelSerializer):

    class Meta:
        model = OldPtq
        fields = '__all__'
        
class PtqHistorySerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True)
    content = serializers.CharField(required=False, allow_null=True)
    ptqId = serializers.IntegerField(source="ptq_id", required=False, allow_null=True)
    feedback = serializers.CharField(required=False, allow_null=True)
    times = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.IntegerField(required=False, allow_null=True)
    recordedName = serializers.CharField(required=False, allow_null=True, source="get_type")
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        image = kwargs.pop('image', False)
        super().__init__(*args, **kwargs)
        
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
        if image:
            self.fields.pop("image")
            self.fields["image"] = serializers.ListField(source="list_img")
    class Meta:
        model = PtqHistory
        fields = [
           "id","image","content","ptqId","times","createdAt","updatedAt","deletedAt","feedback","status","recordedName"
        ]
        
class PtqTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
    
    class Meta:
        model = PtqType
        fields = [
           "id","type","createdAt","updatedAt","deletedAt","description"
        ]
        
        
class ToolsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, source="SCM_id")
    email = serializers.CharField(required=False)
    stockName = serializers.CharField(required=False, source="stock_name")
    itemCode = serializers.CharField(required=False, source="item_code")
    itemName = serializers.CharField(required=False, source="item_name")
    unitName = serializers.CharField(required=False, source="unit_name")
    sizeName = serializers.CharField(required=False, source="size_name")
    quantityNow = serializers.IntegerField(required=False, source="quantity_now")
    quantityHold = serializers.IntegerField(required=False, source="quantity_hold")
    startDate = serializers.DateField(required=False, source="start_date")
    expireDate = serializers.DateField(required=False, source="expire_date")
    zoneName = serializers.CharField(required=False, source="zone_name")
    DateofControl = serializers.CharField(required=False)
    CommentTools = serializers.CharField(required=False, source="CommentCDCD")
    updateBy = serializers.CharField(required=False, source="update_by")
    updateTime = serializers.DateTimeField(required=False, source="update_time")
    usageStatus = serializers.IntegerField(required=False, source="usage_status")
    status = serializers.IntegerField(required=False, source="tinh_trang")
    idHistory = serializers.CharField(required=False, source="id_history")
    idRepair = serializers.CharField(required=False, source="id_repair")
    tCheck = serializers.DateField(required=False, source="t_check")
    name = serializers.CharField(required=False, source="get_name")
    empCode = serializers.CharField(required=False, source="get_code")
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        
        VN = kwargs.pop('VN', None)
        
        super().__init__(*args, **kwargs)
        
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
            for field_name in allowed:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        
    class Meta:
        model = Tools
        # fields = "__all__"
        fields = [
            "id","email","stockName","itemCode","itemName",
            "unitName","sizeName","quantityNow","quantityHold",
            "startDate","expireDate","zoneName","DateofControl",
            "CommentTools","updateBy","updateTime","usageStatus",
            "status","idHistory","idRepair","tCheck","name", "empCode"
        ]
        
class DeleteReasonPtqSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(required=False)
    keyReason = serializers.CharField(required=False, source="key_reason")   
    createdAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="created_at", required=False, allow_null=True)
    updatedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="updated_at", required=False, allow_null=True)
    deletedAt = serializers.DateTimeField(format=DATETIME_FORMAT ,source="deleted_at", required=False, allow_null=True)
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        
        VN = kwargs.pop('VN', None)
        
        super().__init__(*args, **kwargs)
        
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
            for field_name in allowed:
                self.fields[VN[field_name]] = self.fields.pop(field_name)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
    class Meta:
        model = DeleteReasonPtq
        fields = ["id","reason","keyReason","createdAt","updatedAt","deletedAt"]