from rest_framework.response import Response
from rest_framework import status

def response_data(data, statusCode=1, message="Success"):
    result = {
        'statusCode': statusCode,
        'message': message,
        'data': data
    }
    return Response(result, status.HTTP_200_OK)