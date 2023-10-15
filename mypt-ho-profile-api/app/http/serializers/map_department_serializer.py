from rest_framework import serializers
from ..models.map_department import *

class MapDepartmentSerializer(serializers.Serializer):
    agency = serializers.CharField(required=True)
    agencyInside = serializers.CharField(source='agency_inside', required=False, allow_null=True, allow_blank=True)
    parentDepart = serializers.CharField(source='parent_depart', required=False, allow_null=True, allow_blank=True)
    parentDepartOld = serializers.CharField(source='parent_depart_old', required=False, allow_null=True, allow_blank=True)
    code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    company = serializers.CharField( required=False, allow_null=True, allow_blank=True)
    technicalManager = serializers.CharField(source='technical_manager', required=False, allow_null=True, allow_blank=True)
    city = serializers.CharField( required=False, allow_null=True, allow_blank=True)
    lat = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lng = serializers.CharField( required=False, allow_null=True, allow_blank=True)
    au = serializers.CharField( required=False, allow_null=True, allow_blank=True)
# add fields au to models
    # def create(self, validated_data):
    #     MapDepartment.objects.create(**validated_data)
    #     return validated_data

    class Meta:
        model = MapDepartment
        # fields = '__all__'
        fields = ['id','branch', 'branchOld', 'parentDepart', 'code', 'company', 'technicalManager',
                  'city', 'lat', 'lng', 'agencyInside',"au",'created_at','updated_at']


    def get_info_from_agency(list_agency):
        dict_data = {}
        try:
            qr = MapDepartment.objects.filter(agency_inside__in=tuple(list_agency)).values()
            if len(qr) > 0:
                for j in qr:
                    lat = j['lat']
                    lng = j['lng']
                    agency_inside = j['agency_inside']
                    agency = j['agency']
                    dict_data.update({
                        agency_inside:{
                            'lat': lat,
                            'lng': lng,
                            'agency': agency,

                        }
                    })

        except Exception as ex:
            print("map_serializer >> get_info_from_agency >> {}".format(ex))
        return  dict_data
