import threading
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.helper import *
from django.conf import settings as project_settings

class HandlePermission(threading.Thread):
    
    def __init__(self, data={}, ptq=False):
        self.data = data
        self.ptq = ptq
        threading.Thread.__init__(self)
        
    def run(self):
        data = self.data_permission()
        result = self.call_api_permission(data)
        return result
        
    
    def data_permission(self):
        data = {
            "empEmail": self.data["email"],
            "empName": self.data["name"],
            "jobTitle": self.data["jobTitle"],
            "contractType": self.data["contractType"],
            "childDepart": self.data["childDepart"]
        }
        return data
    
    def call_api_permission(self, data={}):
        app_env = project_settings.APP_ENVIRONMENT
        result = call_api(
            host=SERVICE_CONFIG["HO-AUTH"][app_env],
            func=SERVICE_CONFIG["HO-AUTH"]["permissions-to-tech-emp"]["func"],
            method=SERVICE_CONFIG["HO-AUTH"]["permissions-to-tech-emp"]["method"],
            data=data
        )
        return result