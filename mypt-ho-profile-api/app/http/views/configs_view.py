import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.viewsets import ViewSet

from ..models.configs import ProfileConfig
from ..paginations.custom_pagination import *
from ..serializers.configs_serializer import ProfileConfigSerializer
from ...core.helpers.my_datetime import get_datetime_now
from ...core.helpers.response import *


class ConfigView(ViewSet):
    def list(self, request, *args, **kwargs):
        queryset = ProfileConfig.objects.all()
        serializer = ProfileConfigSerializer(queryset, many=True)
        return response_data(serializer.data)

    def create(self, request, *args, **kwargs):
        request_data = request.data
        if isinstance(request_data['configValue'], dict):
            request_data['configValue'] = json.dumps(request_data['configValue'])
        with transaction.atomic():
            data = ProfileConfig.objects.create(config_key=request_data['configKey'],
                                                config_value=request_data['configValue'],
                                                created_at=get_datetime_now())
        serializer = ProfileConfigSerializer(data, many=False)
        return response_data(serializer.data, "Đã tạo thành công!")

    def retrieve(self, request, *args, **kwargs):
        try:
            request_data = request.GET['configKey']
            queryset = ProfileConfig.objects.get(config_key=request_data)
            serializer = ProfileConfigSerializer(queryset, many=False)
        except ObjectDoesNotExist:
            return response_data(message="Dữ liệu không tồn tại")
        return response_data(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            request_data = request.data
            queryset = ProfileConfig.objects.get(config_key=request_data['configKey'])
            serializer = ProfileConfigSerializer(queryset, many=False)
            with transaction.atomic():
                queryset.delete()
        except ObjectDoesNotExist:
            return response_data(message="Dữ liệu không tồn tại")
        return response_data(serializer.data, message="Đã xóa thành công!")

    def update(self, request, *args, **kwargs):
        try:
            request_data = request.data
            queryset = ProfileConfig.objects.filter(config_key=request_data['configKey'])
            serializer = ProfileConfigSerializer(queryset, many=True)
            if isinstance(request_data['configValue'], dict):
                request_data['configValue'] = json.dumps(request_data['configValue'])
            with transaction.atomic():
                queryset.update(config_key=request_data['configKey'], config_value=request_data['configValue'],
                                last_modified_at=get_datetime_now())
        except ObjectDoesNotExist:
            return response_data(message="Dữ liệu không tồn tại")
        return response_data(None, message="Đã cập nhật thành công!")
