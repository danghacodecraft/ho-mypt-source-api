
from kafka import KafkaProducer
import json
from app.core.helpers.global_variable import *
from ...core.helpers.response import *
from rest_framework.viewsets import ViewSet

class KafkaView(ViewSet):


    def api_send(self, request):
        try:
            producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
            message_ = request.data
            message2 = json.dumps(message_)
            message3 = message2.encode('utf-8')
            message = message3
            future = producer.send(TOPIC_KAFKA, message)
            result = future.get()
            print(result)
        except Exception as ex:
            print("error")
            print(ex)
        return response_data(data={}, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)