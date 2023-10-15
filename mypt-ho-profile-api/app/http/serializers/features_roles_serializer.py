from app.http.models.features_roles import FeaturesRoles
from rest_framework.serializers import ModelSerializer

class FeaturesRolesSerializer(ModelSerializer):

    class Meta:
        model = FeaturesRoles
        fields = '__all__'
