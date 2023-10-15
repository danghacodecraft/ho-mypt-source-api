from app.http.models.user_infos import UserInfos
from rest_framework import serializers


class UserInfosSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfos
        # fields = ['id', 'user_id', 'device_id', 'device_name', 'device_token']
        fields = '__all__'
        # extra_kwargs = {
        #     "id": {"required": True},
        #     "user_id": {"required": True}
        # }


class UserInfosSerializerForMyPT(serializers.HyperlinkedModelSerializer):
    userId = serializers.IntegerField(source='user_id')

    class Meta:
        model = UserInfos
        fields = ['userId', 'email']