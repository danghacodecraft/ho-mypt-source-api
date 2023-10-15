from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict

class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'perPage'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(data)


class EmployeeRankPagination(pagination.PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return OrderedDict(
            count=self.page.paginator.count,
            dict_keys={},
            list_data=data
        )
