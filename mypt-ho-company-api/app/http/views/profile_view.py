import json

from rest_framework.viewsets import ViewSet

from django.conf import settings as project_settings
from app.configs.service_api_config import SERVICE_CONFIG
from app.core.helpers.utils import call_api


class ProfileView(ViewSet):
    def call_api_get_user_profile_by_list_email(self, data):
        try:

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host = SERVICE_CONFIG['profile-api'][app_env],
                func = SERVICE_CONFIG['profile-api']['get_user_profile_by_list_email']['func'],
                method = SERVICE_CONFIG['profile-api']['get_user_profile_by_list_email']['method'],
                data = data
            )
            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                return {}
            dataApi = dataApi['data']
            return dataApi
        except:
            return {}

    def call_api_get_list_email_by_list_child_depart(self, data):
        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=SERVICE_CONFIG['profile-api'][app_env],
                func=SERVICE_CONFIG['profile-api']['get_list_email_by_list_child_depart']['func'],
                method=SERVICE_CONFIG['profile-api']['get_list_email_by_list_child_depart']['method'],
                data=data
            )
            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                return []
            dataApi = dataApi['data']
            return dataApi
        except:
            return []

    def call_api_get_email_from_code_or_name(self, data):
        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=SERVICE_CONFIG['profile-api'][app_env],
                func=SERVICE_CONFIG['profile-api']['get_email_from_code_or_name']['func'],
                method=SERVICE_CONFIG['profile-api']['get_email_from_code_or_name']['method'],
                data=data
            )
            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                return []
            dataApi = dataApi['data']['emails']
            return dataApi
        except:
            return []