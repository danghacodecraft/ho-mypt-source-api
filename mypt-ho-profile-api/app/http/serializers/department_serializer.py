from rest_framework import serializers
from ..models.hr import Department


class DepartmentSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Department
        # fields = ['child_depart', 'parent_depart', 'branch', 'chi_nhanh']
        fields = '__all__'
