from rest_framework import serializers

class GetModifyHistoriesValidate(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        allow_empty=True,
        required=False,
        default=[]
    )
    emp_codes = serializers.ListField(
        child=serializers.CharField(max_length=15),
        allow_empty=True,
        required=False,
        default=[]
    )
    keys = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=False,
        required=True
    )
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)
    necessary_fields = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=False,
        required=True
    )
    