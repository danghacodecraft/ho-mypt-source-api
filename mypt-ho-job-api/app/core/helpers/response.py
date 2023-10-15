from rest_framework.response import Response
from math import ceil


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


def validate_error(message={}, type=False):
    error_message = ''
    if isinstance(message, list):
        for index, item in enumerate(message):
            if item != {}:
                if type:
                    error_message += message_errors(item)
                else:
                    error_message += 'Dòng {}: {}'.format(str(index), message_errors(item))
        return error_message
    return message_errors(message)


def message_errors(data={}):
    data = dict(data)
    error_message = ''
    for key, value in data.items():
        error_message += str(key) + ' ' + str(list(value)[0]) + '<br/>'
    return str(error_message)


def response_paginator(sum, per_page, data, count=0):
    result = {
        'max_page': ceil(sum / per_page),
        'list_data': data,
        'count': count
    }
    return response_data(data=result)
