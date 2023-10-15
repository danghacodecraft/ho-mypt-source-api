from ..models.improved_car import *
from rest_framework import serializers


class ImprovedCarLikeSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        
        fields = kwargs.pop('fields', None)
        

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
    class Meta:
        model = ImprovedCarLike
        fields = [
            'id',
            'email',
            'id_tree',
            'state_like'
        ]

class ImprovedCarSerializer(serializers.ModelSerializer):
    typeTitle = serializers.IntegerField(source='type_title', required=False)
    emailCreate = serializers.CharField(source='email_create', required=False)
    nameImprovedCar = serializers.CharField(source='name_xe_cai_tien', required=False)
    groupImprovedCar = serializers.IntegerField(source='group_xe_cai_tien', required=False)
    memberGroup = serializers.CharField(source='member_group', required=False)
    currentStatus = serializers.CharField(source='current_status', required=False)
    updateTime = serializers.CharField(source='get_update_time', required=False)
    updateDate = serializers.CharField(source='get_update_date', required=False)
    imgImprovedCar = serializers.CharField(source='img_xe_cai_tien', required=False)
    parentDepart = serializers.CharField(source='parent_depart', required=False)
    sumLike = serializers.IntegerField(source='sum_like', required=False)
    sumComment = serializers.IntegerField(source='sum_comment', required=False)
    purpose = serializers.CharField(required=False)
    solution = serializers.CharField(required=False)
    effective = serializers.CharField(required=False)
    creative = serializers.CharField(required=False)
    possibility = serializers.CharField(required=False)
    note = serializers.CharField(required=False)
    branch = serializers.CharField(required=False)
    reject = serializers.IntegerField(required=False)
      
    class Meta:
        model = ImprovedCar
        fields = [
            'id','sumLike','sumComment','typeTitle','emailCreate','nameImprovedCar',
            'groupImprovedCar','memberGroup','currentStatus','purpose','solution',
            'effective','creative','possibility','note','updateDate','updateTime',
            'branch','imgImprovedCar','reject','parentDepart'
        ]
    def __init__(self, *args, **kwargs):
        
        fields = kwargs.pop('fields', None)
        
        show = kwargs.pop('show', False)
        
        profile = kwargs.pop('profile', False)
        
        image = kwargs.pop("image", False)

        super().__init__(*args, **kwargs)
                    
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if show:
            self.fields['show_comment'] = serializers.BooleanField(default=True)
            self.fields['limit_height'] = serializers.BooleanField(default=True)
            self.fields['isRate'] = serializers.BooleanField(default=False)
            self.fields['rate'] = serializers.DictField(source="sum_rate")
        if profile:
            self.fields['profile'] = serializers.DictField(source="get_profile")
        if image:
            self.fields['imgImprovedCar'] = serializers.ListField(source="list_img")
    
class ImprovedCarCommentSerializer(serializers.ModelSerializer):
    idTree = serializers.IntegerField(source="id_tree",required=False)
    create = serializers.DateTimeField(source="t_create",required=False, format='%H:%M:%S %d/%m/%Y')
    parent = serializers.IntegerField(required=False)
    email = serializers.CharField(required=False)
    msg = serializers.CharField(required=False)
    type = serializers.IntegerField(required=False)
    level = serializers.IntegerField(required=False)
    
    def __init__(self, *args, **kwargs):
        
        fields = kwargs.pop('fields', None)
        
        show = kwargs.pop('show', False)

        profile = kwargs.pop('profile', False) 
        
        super().__init__(*args, **kwargs)
        

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if show:
            self.fields['show_comment'] = serializers.BooleanField(default=True)
        if profile:
            self.fields['profile'] = serializers.DictField(source="get_profile")
        
    class Meta:
        model = ImprovedCarComment
        fields = [
            'id',
            'parent',
            'email',
            'msg',
            'idTree',
            'create',
            'type',
            'level'
        ]
        
class ImprovedCarGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    createdAt = serializers.DateTimeField(required=False,source="created_at")
    updatedAt = serializers.DateTimeField(required=False,source="updated_at")
    deletedAt = serializers.DateTimeField(required=False,source="deleted_at")
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
    class Meta:
        model = ImprovedCarGroup
        fields = [
            "id","name","createdAt","updatedAt","deletedAt"
        ]

    def get_all_values(fname):
        dict_data = {}
        try:
            queryset = ImprovedCarGroup.objects.all().values('name', 'id')
            for i in queryset:
                id = i['id']
                name = i['name']
                dict_data.update({
                    id: name
                })

        except Exception as ex:
            print("{} >> {} >>  Error/Loi: {}".format(fname, "get_all_values", ex))
        return dict_data
        
class RateTheArticleSerializer(serializers.ModelSerializer):
    idTree = serializers.IntegerField(required=False, source="id_tree")
    rate = serializers.IntegerField(required=False)
    content = serializers.CharField(required=False)
    effective = serializers.CharField(required=False)
    creative = serializers.CharField(required=False)
    possibility = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    createdAt = serializers.DateTimeField(required=False,source="created_at", format="%d-%m-%Y %H:%M:%S")
    updatedAt = serializers.DateTimeField(required=False,source="updated_at", format="%d-%m-%Y %H:%M:%S")
    deletedAt = serializers.DateTimeField(required=False,source="deleted_at", format="%d-%m-%Y %H:%M:%S")
    
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        not_fields = kwargs.pop('not_fields', None)
        profile = kwargs.pop('profile', False)
        super().__init__(*args, **kwargs)
        if profile:
            self.fields['profile'] = serializers.DictField(source="get_profile")
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if not_fields is not None:
            for field_name in not_fields:
                self.fields.pop(field_name)
                
    class Meta:
        model = RateTheArticle
        fields = [
            "id","rate","content","effective",
            "creative","possibility","email",
            "createdAt","updatedAt","deletedAt",
            "idTree"
        ]


class ImproveCarIdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    status = serializers.CharField(required=False)


class ImproveCarSearchDateSerializer(serializers.Serializer):
    startDate = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])
    endDate = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y"])

    def __init__(self, *args, **kwargs):
        super(ImproveCarSearchDateSerializer, self).__init__(*args, **kwargs)  # call the super()
        for field in self.fields:  # iterate over the serializer fields
            self.fields[field].error_messages['required'] = 'Thiếu trường %s' % field  # set the custom error message
            self.fields[field].error_messages['blank'] = 'Trường %s không được để trống' % field

    def validate(self, data):
        if data['startDate'] > data['endDate']:
            raise serializers.ValidationError("Từ ngày không được lớn hơn đến ngày")
        return data


class ListChildDepartSerializer(serializers.Serializer):
    listChildDepart = serializers.ListField(required=True)
    listTypeTitle = serializers.ListField(required=True)

    def __init__(self, *args, **kwargs):
        super(ListChildDepartSerializer, self).__init__(*args, **kwargs)  # call the super()
        for field in self.fields:  # iterate over the serializer fields
            self.fields[field].error_messages['required'] = 'Thiếu trường %s' % field  # set the custom error message


