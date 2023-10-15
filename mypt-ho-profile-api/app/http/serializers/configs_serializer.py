from rest_framework import serializers
from ..models.configs import *
import json


class ProfileConfigSerializer(serializers.ModelSerializer):
    configKey = serializers.CharField(source='config_key')
    configValue = serializers.CharField(source='config_value')
    createdAt = serializers.DateTimeField(source='created_at')
    lastModifiedAt = serializers.DateTimeField(source='last_modified_at')

    class Meta:
        model = ProfileConfig
        fields = ['configKey', 'configValue', 'createdAt', 'lastModifiedAt']

    def validate_configValue(self, configValue):
        try:
            data = json.loads(configValue)
            return data
        except Exception as ex:
            print(str(ex))
            return configValue

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['configValue'] = self.customize_config_value(representation['configValue'])
        return representation

    def customize_config_value(self, config_value):
        # Your logic to customize the configValue field goes here
        # For example, you could add some prefix to the configValue field
        try:
            return json.loads(config_value)
        except:
            return config_value

    def get_value_by_key(self):
        data = ProfileConfig.objects.filter(config_key=self).values('config_value')
        data = list(data)

        if len(data) == 0:
            return None
        value = data[0].get('config_value', '')
        return value
