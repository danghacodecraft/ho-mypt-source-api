from rest_framework.pagination import PageNumberPagination

from app.core.helpers.response import response_data


class WorkingSchedulePagination(PageNumberPagination):
    def get_paginated_response(self, data):
        dict_keys = {}
        if data:
            for key_item in data[0].keys():
                dict_keys.update({
                    key_item: key_item.strip()
                })
        return response_data(
            data={
                'count': self.page.paginator.count,

                'dict_keys': dict_keys,
                'list_data': data
            })
