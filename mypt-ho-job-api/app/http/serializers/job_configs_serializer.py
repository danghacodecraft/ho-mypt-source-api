from ..models.job_configs import JobConfigs
from rest_framework.serializers import ModelSerializer


class JobConfigsSerializer(ModelSerializer):
    class Meta:
        model = JobConfigs
        fields = ['config_key', 'config_value']
