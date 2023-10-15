from rest_framework import serializers
from app.http.models.emails_prepare_add_pers_fea_roles import EmailsPrepareAddPersFeaRoles
from rest_framework.serializers import ModelSerializer


class EmailsPrepareAddPersFeaRolesSerializer(ModelSerializer):
    childDepart = serializers.CharField(source='child_depart')
    isProcessed = serializers.IntegerField(source='is_processed')

    class Meta:
        model = EmailsPrepareAddPersFeaRoles
        fields = ["email", "childDepart", "isProcessed"]
