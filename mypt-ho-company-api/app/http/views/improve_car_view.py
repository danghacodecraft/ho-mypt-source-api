import ast
from datetime import datetime
from pyexpat.errors import messages

from ..threading.handle_notification import *
from ..threading.handle_setting import *
from ...configs.excel_table import *
from ...configs.service_api_config import *
from ...core.helpers.response import *
from ...core.helpers.helper import *
from ...core.helpers.utils import *
from ..models.ptq import *
from ..validations.ptq_validate import *
from ..serializers.ptq_serializer import *
from ..serializers.improved_car_serializer import *
from ..paginations.custom_pagination import *
import redis
from rest_framework.viewsets import ViewSet
import json
from app.http.entities import global_data
from django.db.models.aggregates import Max

from datetime import date
from datetime import timedelta

from ...core.helpers import auth_session_handler as authSessionHandler


class ImprovecarView(ViewSet):

    def export_car(self, request):

        fname = "export_car"
        # data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
        # branch = data_token.get("branch")

        data_input = request.data

        if ("code" in data_input and data_input['code']) or ("email" in data_input and data_input['email']) or \
                ("name" in data_input and data_input['name']):
            serializer = ImproveCarSearchDateSerializer(data=data_input)

            data_token = authSessionHandler.get_user_token(request)

            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                              port=project_settings.REDIS_PORT_CENTRALIZED,
                                              db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                              decode_responses=True, charset="utf-8")
            allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")

            if allDepartsWithLevelsStr is None:
                # print("Khong co Redis allDepartsWithLevels")
                allDepartsWithLevels = None
            else:
                # print("Lay departs tu redis allDepartsWithLevels ne !")
                allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)
                # print(allDepartsWithLevels)

            permissions = data_token['permissions']
            list_email_child_depart_rights = []
            if 'ALL' not in permissions:
                xct_show = permissions['SHOW_EXPORT_XE_CAI_TIEN']
                branch_rights = xct_show['branch_rights']
                child_depart_rights = xct_show['child_depart_rights']
                all_depart = allDepartsWithLevels['allDeparts'] if allDepartsWithLevels else None
                tin = branch_rights['TIN']
                pnc = branch_rights['PNC']
                list_child_depart = []
                if 'ALL' not in tin and 'ALL' not in pnc:
                    all_keys = child_depart_rights.keys()
                    for key_item in all_keys:
                        list_child_depart.extend(child_depart_rights[key_item])
                else:

                    if 'ALL' in tin:
                        if all_depart is not None:
                            for _, v in all_depart['ALLTIN'].items():
                                list_child_depart.extend(
                                    v
                                )
                    else:
                        tin_keys = child_depart_rights.keys()
                        for key_item in tin_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                    if 'ALL' in pnc:
                        if all_depart is not None:
                            for _, v in all_depart['ALLPNC'].items():
                                list_child_depart.extend(
                                    v
                                )
                    else:
                        pnc_keys = child_depart_rights.keys()
                        for key_item in pnc_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                list_email_child_depart_rights = ProfileView().call_api_get_list_email_by_list_child_depart(
                    data={"list_child_depart": list_child_depart})

            if not serializer.is_valid():
                return response_data(status=5, message=list(serializer.errors.values())[0][0])

            start_date = serializer.validated_data['startDate']
            end_date = serializer.validated_data['endDate']

            serializer = ListChildDepartSerializer(data=data_input)

            if not serializer.is_valid():
                return response_data(status=5, message=list(serializer.errors.values())[0][0])

            from_datetime = datetime.combine(start_date, datetime.min.time())
            to_datetime = datetime.combine(end_date, datetime.max.time())

            try:

                dict_title = ImprovedCarGroupSerializer.get_all_values(fname)
                if list_email_child_depart_rights:
                    if "email" in data_input and data_input['email']:
                        queryset = ImprovedCar.objects.filter(
                            Q(update_time__gte=from_datetime, update_time__lte=to_datetime,
                              email_create=data_input['email']) & Q(email_create__in=list_email_child_depart_rights)
                        ).order_by('-update_time')

                    if ("code" in data_input and data_input['code']) or ("name" in data_input and data_input['name']):
                        email_create = ProfileView().call_api_get_email_from_code_or_name(data={
                            'code': data_input['code'] if 'code' in data_input else '',
                            'name': data_input['name'].strip() if (
                                    'name' in data_input and data_input['name']) else ''})

                        queryset = ImprovedCar.objects.filter(
                            Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                            & Q(email_create__in=email_create)
                            & Q(email_create__in=list_email_child_depart_rights)
                        ).order_by('-update_time')
                else:
                    if "email" in data_input and data_input['email']:
                        queryset = ImprovedCar.objects.filter(
                            update_time__gte=from_datetime, update_time__lte=to_datetime,
                            email_create=data_input['email']
                        ).order_by('-update_time')

                    if ("code" in data_input and data_input['code']) or ("name" in data_input and data_input['name']):
                        email_create = ProfileView().call_api_get_email_from_code_or_name(data={
                            'code': data_input['code'] if 'code' in data_input else '',
                            'name': data_input['name'].strip() if (
                                    'name' in data_input and data_input['name']) else ''})

                        queryset = ImprovedCar.objects.filter(
                            Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                            & Q(email_create__in=email_create)
                            # & Q(email_create__in=list_email)
                        ).order_by('-update_time')

                        # queryset.filter(email_create__in=email_create)

                serializer = ImprovedCarSerializer(queryset, many=True)

                list_data = serializer.data
                if len(list_data) > 0:
                    list_sheet_1 = []
                    list_sheet_2 = []
                    for i in list_data:

                        queryset_detail = RateTheArticle.objects.filter(id_tree=i["id"], )
                        avg_rate = list(queryset_detail.aggregate(Avg('rate')).values())[0] if queryset_detail else 0.0

                        sum_rate = queryset_detail.count()
                        list_sheet_1.append({
                            "ID": i["id"],
                            "Lĩnh vực cải tiến": dict_title.get(i["typeTitle"], ''),
                            "Người tạo": i["emailCreate"],
                            "Tên bài viết": i["nameImprovedCar"],
                            # "Thành viên nhóm": i["memberGroup"],
                            "Thực trạng": i["currentStatus"],
                            "Mục đích cải tiến": i["purpose"],
                            "Giải pháp": i["solution"],
                            "Tính hiệu quả": i["effective"],
                            "Tính sáng tạo": i["creative"],
                            "Tính khả thi": i["possibility"],
                            "Thông tin khác": i["note"],
                            "Thời gian cập nhật": i['updateTime'],
                            "Ngày cập nhật": i['updateDate'],
                            "Trung tâm": i["branch"],
                            "Số lượt thích": i["sumLike"],
                            "Số lượt bình luận": i["sumComment"],
                            "Số người đánh giá": sum_rate,
                            "Trạng thái đánh giá": "Đã đánh giá" if sum_rate else "Chưa nhận đánh giá",
                            "Điểm đánh giá": avg_rate
                        })

                        serializer_detail = RateTheArticleSerializer(queryset_detail, many=True)
                        list_data_detail = serializer_detail.data
                        if len(list_data_detail) > 0:
                            for j in list_data_detail:
                                list_sheet_2.append({
                                    "Lĩnh vực cải tiến": dict_title.get(i["typeTitle"], ''),
                                    "Tên bài viết": i['nameImprovedCar'],
                                    "Người đánh giá": j["email"],
                                    "Số sao": j['rate'],
                                    "Đánh giá tính hiệu quả": j['effective'],
                                    "Đánh giá tính sáng tạo": j['creative'],
                                    "Đánh giá tính khả thi": j['possibility'],
                                    "Nội dung góp ý": j['content']

                                })

                    data_output = {
                        "sheet1": list_sheet_1,
                        "sheet2": list_sheet_2
                    }

                    return response_data(data=data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
                else:
                    return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

            except Exception as ex:
                return response_data(data={"error": str(ex)}, status=STATUS_CODE_ERROR_LOGIC,
                                     message=MESSAGE_API_ERROR_LOGIC)

        serializer = ImproveCarSearchDateSerializer(data=data_input)

        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])

        start_date = serializer.validated_data['startDate']
        end_date = serializer.validated_data['endDate']

        serializer = ListChildDepartSerializer(data=data_input)

        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])

        list_child_depart = serializer.validated_data['listChildDepart']
        list_type_title = serializer.validated_data['listTypeTitle']

        list_email = ProfileView().call_api_get_list_email_by_list_child_depart(
            data={"list_child_depart": list_child_depart})

        from_datetime = datetime.combine(start_date, datetime.min.time())
        to_datetime = datetime.combine(end_date, datetime.max.time())

        try:

            dict_title = ImprovedCarGroupSerializer.get_all_values(fname)

            if list_type_title:
                queryset = ImprovedCar.objects.filter(
                    update_time__gte=from_datetime, update_time__lte=to_datetime,
                    email_create__in=list_email, type_title__in=list_type_title).order_by('-update_time')
            else:
                queryset = ImprovedCar.objects.filter(
                    update_time__gte=from_datetime, update_time__lte=to_datetime, email_create__in=list_email
                ).order_by('-update_time')

            serializer = ImprovedCarSerializer(queryset, many=True)
            list_data = serializer.data
            if len(list_data) > 0:
                list_sheet_1 = []
                list_sheet_2 = []
                for i in list_data:
                    queryset_detail = RateTheArticle.objects.filter(id_tree=i["id"])
                    sum_rate = queryset_detail.count()
                    avg_rate = list(queryset_detail.aggregate(Avg('rate')).values())[0] if queryset_detail else 0.0
                    list_sheet_1.append({
                        "ID": i["id"],
                        "Lĩnh vực cải tiến": dict_title.get(i["typeTitle"], ''),
                        "Người tạo": i["emailCreate"],
                        "Tên bài viết": i["nameImprovedCar"],
                        # "Thành viên nhóm": i["memberGroup"],
                        "Thực trạng": i["currentStatus"],
                        "Mục đích cải tiến": i["purpose"],
                        "Giải pháp": i["solution"],
                        "Tính hiệu quả": i["effective"],
                        "Tính sáng tạo": i["creative"],
                        "Tính khả thi": i["possibility"],
                        "Thông tin khác": i["note"],
                        "Thời gian cập nhật": i['updateTime'],
                        "Ngày cập nhật": i['updateDate'],
                        "Trung tâm": i["branch"],
                        "Số lượt thích": i["sumLike"],
                        "Số lượt bình luận": i["sumComment"],
                        "Số người đánh giá": sum_rate,
                        "Trạng thái đánh giá": "Đã đánh giá" if sum_rate else "Chưa nhận đánh giá",
                        "Điểm đánh giá": avg_rate
                    })

                    serializer_detail = RateTheArticleSerializer(queryset_detail, many=True)
                    list_data_detail = serializer_detail.data
                    if len(list_data_detail) > 0:
                        for j in list_data_detail:
                            list_sheet_2.append({
                                "Lĩnh vực cải tiến": dict_title.get(i["typeTitle"], ''),
                                "Tên bài viết": i['nameImprovedCar'],
                                "Người đánh giá": j["email"],
                                "Số sao": j['rate'],
                                "Đánh giá tính hiệu quả": j['effective'],
                                "Đánh giá tính sáng tạo": j['creative'],
                                "Đánh giá tính khả thi": j['possibility'],
                                "Nội dung góp ý": j['content']

                            })

                data_output = {
                    "sheet1": list_sheet_1,
                    "sheet2": list_sheet_2
                }
                return response_data(data=data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

            else:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)

        except Exception as ex:
            return response_data(data={"error": str(ex)}, status=STATUS_CODE_ERROR_LOGIC,
                                 message=MESSAGE_API_ERROR_LOGIC)

    def get_list_improved_car(self, request):
        data = request.data
        params = request.query_params
        serializer = ImproveCarSearchDateSerializer(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])
        from_date = serializer.validated_data['startDate']
        to_date = serializer.validated_data['endDate']

        from_datetime = datetime.combine(from_date, datetime.min.time())
        to_datetime = datetime.combine(to_date, datetime.max.time())

        if ("code" in data and data['code']) or ("email" in data and data['email']) \
                or ("name" in data and data['name']):
            data_token = authSessionHandler.get_user_token(request)
            permissions = data_token['permissions']

            redisInstance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED,
                                              port=project_settings.REDIS_PORT_CENTRALIZED,
                                              db=project_settings.REDIS_DATABASE_CENTRALIZED,
                                              password=project_settings.REDIS_PASSWORD_CENTRALIZED,
                                              decode_responses=True, charset="utf-8")
            allDepartsWithLevelsStr = redisInstance.get("allDepartsWithLevels")

            if allDepartsWithLevelsStr is None:
                # print("Khong co Redis allDepartsWithLevels")
                allDepartsWithLevels = None
            else:
                # print("Lay departs tu redis allDepartsWithLevels ne !")
                allDepartsWithLevels = ast.literal_eval(allDepartsWithLevelsStr)
                # print(allDepartsWithLevels)

            list_email_child_depart_rights = []

            if 'ALL' not in permissions:
                xct_show = permissions['SHOW_EXPORT_XE_CAI_TIEN']
                branch_rights = xct_show['branch_rights']
                child_depart_rights = xct_show['child_depart_rights']
                all_depart = allDepartsWithLevels['allDeparts'] if allDepartsWithLevels else None
                tin = branch_rights['TIN']
                pnc = branch_rights['PNC']
                list_child_depart = []
                if 'ALL' not in tin and 'ALL' not in pnc:
                    all_keys = child_depart_rights.keys()
                    for key_item in all_keys:
                        list_child_depart.extend(child_depart_rights[key_item])
                else:
                    if 'ALL' in tin:
                        if all_depart:
                            for _, v in all_depart['ALLTIN'].items():
                                list_child_depart.extend(
                                    v
                                )
                    else:
                        tin_keys = child_depart_rights.keys()
                        for key_item in tin_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                    if 'ALL' in pnc:
                        if all_depart:
                            for _, v in all_depart['ALLPNC'].items():
                                list_child_depart.extend(
                                    v
                                )
                    else:
                        pnc_keys = child_depart_rights.keys()
                        for key_item in pnc_keys:
                            list_child_depart.extend(child_depart_rights[key_item])
                list_email_child_depart_rights = ProfileView().call_api_get_list_email_by_list_child_depart(
                    data={"list_child_depart": list_child_depart})

            if list_email_child_depart_rights:
                if "email" in data and data['email']:
                    improve_cars = ImprovedCar.objects.filter(
                        Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                        & Q(email_create=data['email'])
                        & Q(email_create__in=list_email_child_depart_rights)
                    ).order_by('-update_time')

                elif ("code" in data and data['code']) or ("name" in data and data['name']):
                    email_create = ProfileView().call_api_get_email_from_code_or_name(data={
                        'code': data['code'] if 'code' in data else '',
                        'name': data['name'].strip() if ("name" in data and data['name']) else ''})

                    improve_cars = ImprovedCar.objects.filter(
                        Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                        & Q(email_create__in=email_create)
                        & Q(email_create__in=list_email_child_depart_rights)
                    ).order_by('-update_time')
                else:
                    improve_cars = ImprovedCar.objects.none()
            else:

                if "email" in data and data['email']:
                    improve_cars = ImprovedCar.objects.filter(
                        Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                        & Q(email_create=data['email'])
                        # & Q(email_create__in=list_email)
                    ).order_by('-update_time')

                elif ("code" in data and data['code']) or ("name" in data and data['name']):
                    email_create = ProfileView().call_api_get_email_from_code_or_name(data={
                        'code': data['code'] if 'code' in data else '',
                        'name': data['name'].strip() if ("name" in data and data['name']) else ''})

                    improve_cars = ImprovedCar.objects.filter(
                        Q(update_time__gte=from_datetime, update_time__lte=to_datetime)
                        & Q(email_create__in=email_create)
                        # & Q(email_create__in=list_email)
                    ).order_by('-update_time')
                else:
                    improve_cars = ImprovedCar.objects.none()

            paginator = ListImproveCarPagination()
            if 'page_size' in params:
                paginator.page_size = params['page_size']
            result_page = paginator.paginate_queryset(improve_cars, request)
            serializer = ImprovedCarSerializer(result_page, many=True)

            return response_data(paginator.get_paginated_response(serializer.data))

        serializer = ListChildDepartSerializer(data=data)

        if not serializer.is_valid():
            return response_data(status=5, message=list(serializer.errors.values())[0][0])

        list_child_depart = serializer.validated_data['listChildDepart']
        list_type_title = serializer.validated_data['listTypeTitle']

        list_email = ProfileView().call_api_get_list_email_by_list_child_depart(
            data={"list_child_depart": list_child_depart})

        if list_type_title:
            improve_cars = ImprovedCar.objects.filter(
                update_time__gte=from_datetime, update_time__lte=to_datetime,
                email_create__in=list_email, type_title__in=list_type_title
            ).order_by('-update_time')
        else:
            improve_cars = ImprovedCar.objects.filter(
                update_time__gte=from_datetime, update_time__lte=to_datetime, email_create__in=list_email
            ).order_by('-update_time')
        paginator = ListImproveCarPagination()
        if 'page_size' in params:
            paginator.page_size = params['page_size']
        result_page = paginator.paginate_queryset(improve_cars, request)
        serializer = ImprovedCarSerializer(result_page, many=True)

        return response_data(paginator.get_paginated_response(serializer.data))

    def get_detail_improved_car(self, request):
        data = request.data.copy()
        serializer_id = ImproveCarIdSerializer(data=data)
        if not serializer_id.is_valid():
            return response_data(status=5, message=serializer_id.errors)
        validate_input = serializer_id.validated_data
        id_tree = validate_input['id']
        status = None
        if 'status' in validate_input:
            status = validate_input['status']

        if status == 'ALL':
            comments = ImprovedCarComment.objects.filter(id_tree=id_tree)
        elif status == 'DELETED':
            comments = ImprovedCarComment.objects.filter(id_tree=id_tree, deleted_at__isnull=True)
        else:
            comments = ImprovedCarComment.objects.filter(id_tree=id_tree, deleted_at__isnull=False)
        cmt_serializers = ImprovedCarCommentSerializer(comments, many=True)
        lst_cmt_email = [cmt['email'].lower() for cmt in cmt_serializers.data]
        profile_cmt = ProfileView().call_api_get_user_profile_by_list_email(data={'list_email': lst_cmt_email})

        for item in cmt_serializers.data:
            email_key = item['email'].lower()
            if email_key in profile_cmt:
                item['fullName'] = profile_cmt[email_key]['fullName']
                item['sex'] = profile_cmt[email_key]['sex']
                item['avatarImg'] = profile_cmt[email_key]['avatarImg']
            else:
                item['fullName'] = None
                item['sex'] = None
                item['avatarImg'] = None

        likes = ImprovedCarLike.objects.filter(id_tree=id_tree, state_like=1)

        like_serializers = ImprovedCarCommentSerializer(likes, many=True)

        lst_like_email = [like['email'].lower() for like in like_serializers.data]
        profile_like = ProfileView().call_api_get_user_profile_by_list_email(data={'list_email': lst_like_email})
        for item in like_serializers.data:
            email_key = item['email'].lower()
            if email_key in profile_like:
                item['fullName'] = profile_like[email_key]['fullName']
                item['sex'] = profile_like[email_key]['sex']
                item['avatarImg'] = profile_like[email_key]['avatarImg']
            else:
                item['fullName'] = None
                item['sex'] = None
                item['avatarImg'] = None

        queryset_rate = RateTheArticle.objects.filter(id_tree=id_tree)
        serializer_rate = RateTheArticleSerializer(queryset_rate, many=True)
        list_data_rate = serializer_rate.data

        data = {
            "list_comment": cmt_serializers.data,
            "list_like": like_serializers.data,
            "list_rate": list_data_rate
        }
        return response_data(data=data, status=1)

    def get_likes_by_id_tree(self, request):
        data = request.data.copy()
        serializer_id = ImproveCarIdSerializer(data=data)
        if not serializer_id.is_valid():
            return response_data(status=0, message=serializer_id.errors)

        id_tree = serializer_id.validated_data['id']

        likes = ImprovedCarLike.objects.filter(id_tree=id_tree, deleted_at__isnull=True)

        serializers = ImprovedCarCommentSerializer(likes, many=True)

        return response_data(data=serializers.data, status=1)

    def delete_improved_car_comment(self, request):
        data = request.data.copy()
        today = date.today()
        serializer_id = ImproveCarIdSerializer(data=data)
        if not serializer_id.is_valid():
            return response_data(status=0, message=serializer_id.errors)
        comment_id = serializer_id.validated_data['id']
        if not ImprovedCarComment.objects.filter(id=comment_id, deleted_at__isnull=True).exists():
            return response_data(status=6, message='Bình luận không tồn tại hoặc đã bị xóa')
        ImprovedCarComment.objects.filter(id=comment_id).update(deleted_at=today.year)
        return response_data(status=1, message='Xóa bình luận thành công')

    def all_improve_car_type_title(self, request):
        titles = ImprovedCarGroup.objects.all().values_list('id', 'name')

        return response_data(data=[{'id': title[0], 'name': title[1]} for title in titles])
