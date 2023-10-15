from rest_framework.response import Response


def response_data(data="", status=1, message="Success"):
    result = {
        'statusCode': status,
        'message': message,
        'data': data
    }
    return Response(result)


def response_datas(data="", status=1, message="Success", number=0):
    result = {
        'statusCode': status,
        'message': message,
        'data': {
            'numberPage': number,
            'listData': data
        }
    }
    return Response(result)
