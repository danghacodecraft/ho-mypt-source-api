import threading
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.helper import *
from django.conf import settings as project_settings

class HandleShowHideTab(threading.Thread):
    
    def __init__(self, data={}, host={}, func=""):
        self.data = data
        self.host = host
        self.func = func
        threading.Thread.__init__(self)
        
    def run(self):
        return self.showHideTab()
    
    def showHideTab(self):
        data = self.data
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        host = self.host.pop(app_env, "")
        func = self.host[self.func]["func"]
        method = self.host[self.func]["method"]
        result = call_api(
            host=host,
            func=func,
            method=method,
            data=data
        )
        print(result)
        return result