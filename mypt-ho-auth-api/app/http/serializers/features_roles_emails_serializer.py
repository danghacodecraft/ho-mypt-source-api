from rest_framework import serializers
from app.http.models.features_roles_emails import FeaturesRolesEmails
from rest_framework.serializers import ModelSerializer


class FeaturesRolesEmailsSerializer(ModelSerializer):

    class Meta:
        model = FeaturesRolesEmails
        fields = '__all__'
