from rest_framework import serializers

from ..models.kpi_info import KpiInfo


class KpiInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = KpiInfo
        fields = '__all__'
