from django.db.models import Avg
from rest_framework import pagination

from app.http.models.improved_car import ImprovedCarGroup, RateTheArticle
from app.http.views.profile_view import ProfileView


class StandardPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class ListImproveCarPagination(pagination.PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        lst_title = ImprovedCarGroup.objects.values_list('id', 'name')
        dict_title = {}
        for k, v in lst_title:
            dict_title.update({
                k: v
            })
        list_email = [item['emailCreate'].lower() for item in data]
        dict_profile = ProfileView().call_api_get_user_profile_by_list_email(data={"list_email": list_email})
        dict_keys = {
            "id": "ID",
            "avgRate": "Điểm đánh giá",
            "typeTitle": "Lĩnh vực",
            "emailCreate": "Người tạo",
            "fullName": "Tên nhân viên",
            "nameImprovedCar": "Tên bài viết",
            "currentStatus": "Thực trạng",
            "purpose": "Mục đích",
            "solution": "Giải pháp",
            "updateTime": "Thời gian cập nhật",
            "updateDate": "Ngày cập nhật",
            "branch": "Trung tâm",
            "sumLike": "Số lượt thích",
            "sumComment": "Số lượt bình luận",

            "sumRate": "Số người đánh giá",
            "statusRate": "Trạng thái đánh giá",

            # "effective": "Tính hiệu quả",
            # "creative": "Tính sáng tạo",
            # "possibility": "Tính khả thi",
            # "note": "Thông tin khác",
            # "sex": "Giới tính",
            # "avatarImg": "Ảnh đại diện",
            # "groupImprovedCar": "",
            # "memberGroup": "",
            #
            # "imgImprovedCar": "",
            # "reject": "",
            # "parentDepart": "",
        } if data else {}

        for item in data:

            item['typeTitle'] = dict_title.get(item["typeTitle"], '')

            articles = RateTheArticle.objects.filter(id_tree=item['id'], deleted_at__isnull=True)
            avg = list(articles.aggregate(Avg('rate')).values())[0]

            item['sumRate'] = articles.count()
            item["avgRate"] = avg if avg else 0.0
            item['statusRate'] = 'Đã đánh giá' if item['sumRate'] else 'Chưa nhận đánh giá'

            mail_key = item['emailCreate']
            if mail_key in dict_profile:
                item['sex'] = dict_profile[mail_key.lower()]['sex']
                item['fullName'] = dict_profile[mail_key.lower()]['fullName']
                item['avatarImg'] = dict_profile[mail_key.lower()]['avatarImg']
            else:
                item['sex'] = None
                item['full_name'] = None
                item['avatarImg'] = None
        return {
            "count": self.page.paginator.count,
            "dict_keys": dict_keys,
            "list_data": data
        }
