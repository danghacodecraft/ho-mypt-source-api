from rest_framework import serializers

from ..models.info_modify_history import InformationModifyHistory

class InformationModifyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationModifyHistory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        exists = set(self.fields.keys())
        fields = set(kwargs.pop("fields", []) or exists)
        exclude = kwargs.pop("exclude", [])
        
        super().__init__(*args, **kwargs)
            
        for field in exclude + list(exists - fields):
            self.fields.pop(field, None)
        