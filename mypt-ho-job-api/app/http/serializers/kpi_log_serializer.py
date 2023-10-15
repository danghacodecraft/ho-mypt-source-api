from app.http.models.kpi_log import *
from rest_framework import serializers


class KpiLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = KpiLog
        fields = '__all__'
