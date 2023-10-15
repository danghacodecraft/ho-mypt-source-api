from rest_framework import viewsets
from ..models.info_modify_history import InformationModifyHistory
from ..serializers.info_modify_history_serializer import InformationModifyHistorySerializer
from ..validations.get_modify_histories_validate import GetModifyHistoriesValidate
from ...core.helpers.response import *
from django.db.models import Q

class UltilityView(viewsets.ViewSet):
    def get_modify_histories(self, request):
        try:
            data = request.data.copy()
            validate = GetModifyHistoriesValidate(data=data)
            if not validate.is_valid():
                return response_data(validate.errors, 4, "Validate error")
            
            instances = InformationModifyHistory.objects.filter(
                Q(
                    key_name__in=validate.validated_data['keys'],
                    created_at__date__range=[
                        validate.validated_data['from_date'], 
                        validate.validated_data['to_date']
                    ]
                )
                & (
                    Q(email__in=validate.validated_data['emails'])
                    | Q(emp_code__in=validate.validated_data['emp_codes'])
                )
            )
            return response_data(
                InformationModifyHistorySerializer(
                    instances, 
                    many=True, 
                    fields=validate.validated_data['necessary_fields']
                ).data, 
                1, 
                "Success"
            )
        except Exception as e:
            return response_data({}, 4, str(e))