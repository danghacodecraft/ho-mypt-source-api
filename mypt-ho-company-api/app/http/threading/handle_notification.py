import threading
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.helper import *
from django.conf import settings as project_settings

class HandleNotification(threading.Thread):
    
    def __init__(self, data={}, ptq=False):
        self.data = data
        self.ptq = ptq
        threading.Thread.__init__(self)
        
    def run(self):
        if self.ptq:
            for item in self.data:
                self.call_notification()
            print("DONE")
            return "DONE"
        return self.call_notification()
        
    def call_notification(self):
        # data=self.structure_noti_ptq()
        print("data")
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        result = call_api(
            host=SERVICE_CONFIG["NOTIFICATION"][app_env],
            func=SERVICE_CONFIG["NOTIFICATION"]["send_noti"]["func"],
            method=SERVICE_CONFIG["NOTIFICATION"]["send_noti"]["method"],
            data=self.data
        )
        print(result)
        return result
    
    def structure_noti_ptq(self):
        structure = {
            "email":self.data.pop("email", ""),
            "title":self.data.pop("title", ""),
            "body":self.data.pop("body", ""),
            "topic_type":self.data.pop("topic_type", ""),
            "dataAction":self.data.pop("dataAction", ""),
            "actionType":self.data.pop("actionType", "")
        }
        return structure