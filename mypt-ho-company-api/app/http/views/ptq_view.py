from ..threading.handle_notification import *
from ..threading.handle_setting import *
from ...configs.excel_table import *
from ...core.helpers.response import *
from ...core.helpers.utils import *
from ..validations.ptq_validate import *
from ..serializers.ptq_serializer import *
from ..paginations.custom_pagination import *
from rest_framework.viewsets import ViewSet
import json
from app.http.entities import global_data

from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings as project_settings


class PtqView(ViewSet):

    def cron_status_ptq(self, request):
        data = request.data.copy()
        datatime = datetime.now()
        # Những status không cần cập nhật trạng thái: DELETED, OK, CANCEL, PENDING
        status_pending = PtqType.objects.filter(type__in=["PENDING"]).values_list("id", flat=True)
        status_for_pending = PtqType.objects.filter(type__in=["NOTOK", "ADD"]).values_list("id", flat=True)
        queryset_pending = Ptq.objects.filter(deadline__lt=datatime.strftime(DATE_FORMAT_QUERY),
                                              recorded__in=status_for_pending).values_list("id", flat=True)

        Ptq.objects.filter(id__in=list(queryset_pending)).update(recorded=status_pending[0])

        return response_data({"query_id_pending": queryset_pending})

    def validate_request_list(self, key, data):
        if key in data and isinstance(data[key], list) and data[key] != []:
            return True
        return False
    # nếu muốn tối ưu thì thêm bảng group type
    def list_type_report(self, request):
        data = {}
        try:
            data['listInspectors'] = Ptq.objects.exclude(updated_by="").distinct().values_list('updated_by', flat=True)
            data['listThematic'] = Ptq.objects.exclude(thematic="").distinct().values_list('thematic', flat=True)
            data['listRecorded'] = PtqType.objects.exclude(id__in=[1]).distinct().values('description', "id")
            return response_data(data)
        except:
            return response_data(data)

    def show_report_ptq(self, request):
        data = request.data.copy()
        email = get_email_from_token(request)

        # check role cua user login trong tinh nang CHE_TAI_HO
        # cheTaiFeaRole = global_data.authUserSessionData["featuresRoles"].get("CHE_TAI_HO", None)
        # if cheTaiFeaRole is None:
        #     return response_data(status=5, message="You have no role on this feature!")

        # if cheTaiFeaRole != "NHAN_VIEN_KIEM_SOAT":
        #     return response_data(status=5, message="Bạn không phải là nhân viên kiểm soát!")

        # print("User nay la Nhan Vien Kiem Soat trong tinh nang CHE_TAI_HO")

        # validate = DateReportValidate(data=data)
        # if not validate.is_valid():
        #     return response_data(status=5, message=validate.errors)

        if "childDepart" in data and data["childDepart"]:
            data["fields"] = "email"
            dataApi = self.call_api_get_code(data)
            if not dataApi:
                queryset = Ptq.objects.filter(
                    created_at__date__range=(data['dateStart'], data['dateEnd']), deleted_at__isnull=True)
            else:
                queryset = Ptq.objects.filter(
                    email__in=dataApi, created_at__date__range=(data['dateStart'], data['dateEnd']),
                    deleted_at__isnull=True)
        else:
            queryset = Ptq.objects.filter(
                created_at__date__range=(data['dateStart'], data['dateEnd']), deleted_at__isnull=True)
        if "inspectors" in data and data["inspectors"] != []:
            queryset = queryset.filter(updated_by__in=data["inspectors"])
        if "controlTopics" in data and data["controlTopics"] != []:
            queryset = queryset.filter(thematic__in=data["controlTopics"])
        if "explanation" in data and data["explanation"] != []:
            queryset = queryset.filter(recorded__in=data["explanation"])
        if "contract" in data and data["contract"] != []:
            queryset = queryset.filter(contract__in=data["contract"])
        if "email" in data and data["email"] != []:
            queryset = queryset.filter(email__in=data["email"])
        show = data.pop("show", None)
        if show is not None and show == "EN":
            paginator = StandardPagination()
            if "perPage" in data and isinstance(data["perPage"], int):
                paginator.page_size = data["perPage"]
            sum = queryset.count()
            per_page = paginator.page_size
            count = sum//per_page
            if sum%per_page > 0:
                count+=1
            paginator_query = paginator.paginate_queryset(queryset, request)
            key_list = list(PTQ_TB.keys())
            key_list.append("updatedBy")
            serializer = PtqSerializer(paginator_query, many=True, fields=key_list, explanation=True)
            rule_edit = PtqType.objects.filter(deleted_at__isnull=True, type__in=["NOTOK"]).values_list("id", flat=True)
            result = serializer.data
            if result == []:
                return response_data(result)
            for item in result:
                if item["updatedBy"] == email:
                    item["isDelete"] = True
                if item["recorded"] not in rule_edit and item["isDelete"]:
                    item["isEdit"] = True
            result_data = {
                "total":sum,
                "numberPage":count,
                "result":result
            }
            return response_data(data=result_data)
        serializer = PtqSerializer(queryset, many=True, VN=PTQ_TB_EXPORT)
        return response_data({"Sheet1":serializer.data})

    def show_report(self, request):
        # check role cua user login trong tinh nang CHE_TAI_HO
        cheTaiFeaRole = global_data.authUserSessionData["featuresRoles"].get("CHE_TAI_HO", None)
        if cheTaiFeaRole is None:
            return response_data(status=5, message="You have no role on this feature!")

        if cheTaiFeaRole == "NHAN_VIEN_KIEM_SOAT":
            return response_data(status=5, message="Nhân viên kiểm soát không được thực hiện tính năng này!")

        print("User nay la role " + cheTaiFeaRole + " trong tinh nang CHE_TAI_HO")

        data = request.data
        # print(data)
        data["fields"] = "email"
        serializer = PtqValidate(data=data)
        if not serializer.is_valid():
            return response_data(status=5, message=serializer.errors)
        dataApi = self.call_api_get_code(data)
        if not dataApi:
            return response_data(status=4, message="Call API fails")
        dateCheck = data["controlMonth"].split("/")
        queryset = Ptq.objects.filter(email__in=dataApi, date_check__month=dateCheck[0], date_check__year=dateCheck[1], deleted_at__isnull=True)
        if "email" in data and data["email"] != []:
            validate = EmailListValidate(data=data)
            if validate.is_valid():
                queryset = queryset.filter(email__in=data["email"])
        if "contract" in data and data["contract"] != []:
            validate = ContractListValidate(data=data)
            if validate.is_valid():
                queryset = queryset.filter(contract__in=data["contract"])
        # if "dateCheck" in data and data["dateCheck"] != "":
        #     queryset = queryset.filter(date_check=data["dateCheck"])
        if "dateStart" in data and data["dateStart"] and "dateEnd" in data and data["dateEnd"]:
            queryset = queryset.filter(Q(date_check__gte=data["dateStart"]) & Q(date_check__lte=data["dateEnd"]))
        serializer = PtqSerializer(queryset, many=True, VN=PTQ_TB_EXPORT)
        show = data.pop("show", None)
        if show is not None and show == "EN":
            key_list = list(PTQ_TB.keys())
            serializer = PtqSerializer(queryset, many=True, fields=key_list)
            return response_data(data=serializer.data)
        return response_data({"Sheet1":serializer.data})

    def list_code(self, data, field="code"):
        arr = []
        for item in data:
            arr.append(item[field])
        while None in arr:
            arr.remove(None)
        return arr

    def call_api_info_email(self, data):
        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host = SERVICE_CONFIG['profile-api'][app_env],
                func = SERVICE_CONFIG['profile-api']['info_from_email']['func'],
                method = SERVICE_CONFIG['profile-api']['info_from_email']['method'],
                data = data
            )
            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                return False
            dataApi = dataApi['data']
            return dataApi
        except:
            return False

    def call_api_get_code(self, data):
        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host = SERVICE_CONFIG['profile-api'][app_env],
                func = SERVICE_CONFIG['profile-api']['get_code']['func'],
                method = SERVICE_CONFIG['profile-api']['get_code']['method'],
                data = data
            )
            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                return False
            dataApi = dataApi['data']
            return dataApi
        except:
            return False

    def import_report_ptq(self, request):
        data = request.data
        if "action" in data and data["action"] == "edit":
            validate = IdValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            queryset = Ptq.objects.filter(ptq_id=data["id"]).first()
            if not Ptq.objects.filter(ptq_id=data["id"]).exists():
                return response_data(status=5, message="Id chưa tồn tại. Không thể sửa")
            list_data_key = data.keys()
            data_save = {}
            for item in list_data_key:
                if data[item] != "" and data[item] != "edit":
                    data_save[item] = data[item]
            serializer = PtqSerializer(queryset, data=data_save)
            if not serializer.is_valid():
                return response_data(status=5, message=serializer.errors)
            if not serializer.save():
                return response_data(status=5, message="Không sửa được")
            return response_data(message="Sửa thành công")
        try:
            if "action" in data and data["action"] == "delete":
                validate = IdValidate(data=data)
                if not validate.is_valid():
                    return response_data(status=5, message=validate.errors)
                queryset = Ptq.objects.filter(ptq_id=data["id"]).first()
                if not Ptq.objects.filter(ptq_id=data["id"]).exists():
                    return response_data(status=5, message="Id chưa tồn tại. Không thể xoá")
                queryset.delete()
                return response_data(message="Xoá thành công")
        except:
            return response_data(status=5, message="Xoá lỗi")

        data_save = []
        if "array" not in data:
            return response_data(status=4, message="Không có dữ liệu import")

        if len(data["array"]) > 1000:
            return response_data(status=0, message="Vui lòng nhập dữ liệu không quá 1000 dòng ")

        email = get_email_from_token(request)
        EN = PTQ_IMPORT

        try:
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT

            response = call_api(
                host=SERVICE_CONFIG['profile-api'][app_env],
                func=SERVICE_CONFIG['profile-api']['get_all_employee_email_list']['func'],
                method=SERVICE_CONFIG['profile-api']['get_all_employee_email_list']['method']
            )

            dataApi = json.loads(response)
            if dataApi["statusCode"] != 1:
                list_valid_email = []
            else:
                list_valid_email = [e.lower() for e in dataApi['data']]
        except Exception as ex:
            print(f'get_all_employee_email_list: {ex}')
            list_valid_email = []

        errors_duplicate = []
        errors_format = []

        from collections import defaultdict

        dct_duplicate = defaultdict(list)

        for count, hehe in enumerate(data['array']):
            dct_duplicate[frozenset(hehe.items())].append(f"({count + 2})")

        for item in dct_duplicate:
            if len(dct_duplicate[item]) > 1:
                str_err = ', '.join(dct_duplicate[item])
                errors_duplicate.append(f'Dòng {str_err} bị trùng')

        three_days_from_today = datetime.today().date() + timedelta(days=3)

        rows = 1
        for item in data['array']:
            rows += 1
            dl = item['Hạn nhận giải trình']
            dl = datetime.strptime(dl, '%d/%m/%Y').date()

            emp_email = item['Email nhân viên']

            data_dict = self.import_vi_to_en(EN=EN, data=item, email=email)

            if dl < three_days_from_today:
                errors_format.append(f"Dòng ({rows}) hạn nhận giải trình phải lớn hơn thời điểm import tối thiểu 3 ngày")

            if emp_email.lower() not in list_valid_email:
                errors_format.append(f"Dòng ({rows}) Email NV không tồn tại trong hệ thống")

            if not data_dict['status'] and data_dict["messages"] != "EXISTS":
                errors_format.append(f"Dòng ({rows}) {data_dict['messages']}")
            if not data_dict['status'] and data_dict["messages"] == "EXISTS":
                # Trùng ks đã có
                errors_duplicate.append(f"Dòng ({rows}) bị trùng")
            if data_dict['status']:
                # Trùng ks file
                if data_dict["messages"] in data_save:
                    errors_duplicate.append(f"Dòng ({rows}) bị trùng")
                data_save.append(data_dict["messages"])

        if errors_duplicate or errors_format:
            return response_data(status=0, message={"errors_format": errors_format, "errors_duplicate": errors_duplicate})

        for item in data_save:
            self.import_report_save(item)
        return response_data(message="Import thành công", status=1, data="data_dict")

    def import_report_save(self, data):
        serializer = PtqSerializer(data=data)
        if not serializer.is_valid():
            return {"status":False, "messages":serializer.errors}
        if not serializer.save():
            return {"status":False, "messages":"Import không thành công"}
        self.send_noti_ptq(data=serializer.data)
        self.show_hide_tab(data=serializer.data)
        return {"status":True}

    def import_vi_to_en(self, **kwargs):
        EN = kwargs.pop('EN', None)
        data = kwargs.pop('data', None)
        email =  kwargs.pop('email', None)
        if EN is not None and data is not None:
            for item in list(data):
                key = item
                item = item.replace(" ", "")
                item = item.lower()
                data[item] = data.pop(key, "")
            key_list = list(EN.keys())
            value_list = list(EN.values())
            data_list = list(data.keys())
            data_dict = {}
            try:
                data_list = set(value_list) & set(data_list)
                for item in data_list:
                    index = value_list.index(item)
                    data_dict[key_list[index]] =  data[item]
            except:
                return {"status":False, "messages":"Lỗi format"}
            try:
                data_dict["dateComplete"] = format_date(data_dict["dateComplete"], "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S")
                data_dict["dateCheck"] = format_date(data_dict["dateCheck"], "%d/%m/%Y", "%Y-%m-%d")
                data_dict["deadline"] = format_date(data_dict["deadline"], "%d/%m/%Y", "%Y-%m-%d")
                data_dict["updatedBy"] = email
            except:
                return {"status":False, "messages":"Lỗi format ngày tháng"}
            date_check = format_date(data_dict["dateComplete"], "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
            data_exists = Ptq.objects.filter(deleted_at__isnull=True, contract=data_dict["contract"],
                                             date_complete__date=date_check, thematic=data_dict["thematic"])
            if data_exists.exists():
                return {"status":False, "messages":"EXISTS"}
            return {"status":True, "messages":data_dict}

        return {"status":False, "messages":"Dữ liệu import rỗng"}

    def show_hide_tab(self, data, showHide="show"):
        data_hide_show = {
            "email":data["email"],
            "tabCode": "cheTai",
            "actionType": showHide
        }
        HandleShowHideTab(data=data_hide_show, host=SERVICE_CONFIG["SETTING"],func="show_hide_tab").start()

    def send_noti_ptq(self, data):
        data_noti = {
            "email":data["email"],
            "title":"Bạn có kiểm soát mới cần xử lý",
            "body":"Bạn có 1 kiểm soát về vi phạm " + data["thematic"] + " cho hợp đồng " + data["contract"],
            "topic_type" : "PTQ",
            "notifyDataAction" : "/list-punish",
            "notifyActionType" : "go_to_screen",
            "popupDetailDataAction" : "/list-punish",
            "popupDetailActionType" : "go_to_screen"
        }
        HandleNotification(data=data_noti).start()

    def send_noti_deleted(self, data):
        data_noti = {
            "email": data.email,
            "title": "Bạn có Kiểm soát vừa được hủy bỏ",
            "body": f"Nhân viên kiểm soát vừa thực hiện hủy bỏ kiểm soát với vi phạm về {data.thematic} cho Hợp đồng {data.contract}",
            "topic_type": "PTQ",
            "notifyDataAction": "/list-punish",
            "notifyActionType": "go_to_screen",
            "popupDetailDataAction": "/list-punish",
            "popupDetailActionType": "go_to_screen"
        }
        HandleNotification(data=data_noti).start()

    def send_noti_ptq_approved(self, data):
        data_noti = {
            "email": data.email,
            "title": "Giải trình được phê duyệt",
            "body": f"Giải trình về vi phạm {data.thematic} của bạn cho Hợp đồng {data.contract} vừa được phê duyệt",
            "topic_type": "PTQ",
            "notifyDataAction": "/list-punish",
            "notifyActionType": "go_to_screen",
            "popupDetailDataAction": "/list-punish",
            "popupDetailActionType": "go_to_screen"
        }
        # print(data_noti)
        # print('noti ok')
        HandleNotification(data=data_noti).start()

    def send_noti_ptq_not_approved(self, data):
        data_noti = {
            "email": data.email,
            "title": "Giải trình bị từ chối",
            "body": f"Giải trình về vi phạm {data.thematic} của bạn cho Hợp đồng {data.contract} vừa bị từ chối",
            "topic_type": "PTQ",
            "notifyDataAction": "/list-punish",
            "notifyActionType": "go_to_screen",
            "popupDetailDataAction": "/list-punish",
            "popupDetailActionType": "go_to_screen"
        }

        # print(data_noti)
        # print('noti not ok')
        HandleNotification(data=data_noti).start()

    def get_tools(self, request):
        try:
            paginator = StandardPagination()
            paginator.page_size = 100
            data = request.data
            show = data.pop("show", None)
            key_list = list(TOOLS_TB.keys())
            validate = GetToolChildDepartValidate(data=data)
            if not validate.is_valid():
                return response_data(message=validate.errors, status=5)
            if "email" in data and data["email"] != [] and data["email"] != "":
                validate = EmailListValidate(data=data)
                if not validate.is_valid():
                    return response_data(message=validate.errors, status=5)
                queryset = Tools.objects.filter(email__in=data["email"])
                if show is not None and show == "EN":
                    result = paginator.paginate_queryset(queryset, request)
                    serializer = ToolsSerializer(result, many=True, fields=key_list)
                    return response_data(serializer.data)
                result = paginator.paginate_queryset(queryset, request)
                serializer = ToolsSerializer(result, many=True, VN=TOOLS_TB)
                return response_data(serializer.data)
            data["fields"] = "email"
            dataApi = self.call_api_get_code(data)
            if not dataApi:
                return response_data(status=4, message="Call API fails")
            queryset = Tools.objects.filter(email__in=dataApi)
            if show is not None and show == "EN":
                result = paginator.paginate_queryset(queryset, request)
                serializer = ToolsSerializer(result, many=True, fields=key_list)
                return response_data(serializer.data)
            result = paginator.paginate_queryset(queryset, request)
            serializer = ToolsSerializer(result, many=True, VN=TOOLS_TB)
            return response_data(serializer.data)
        except:
            return response_data(message="Lỗi", status=4)

    def get_contract(self, request):
        try:
            data = request.data
            paginator = StandardPagination()
            if "pageSize" in data:
                paginator.page_size = data["pageSize"]
            else:
                paginator.page_size = 1000
            queryset = Ptq.objects.all()
            if "count" in data and data["count"] != "":
                count = queryset.count()
                return response_data(data=count)
            count = queryset.count()//paginator.page_size+1
            result = paginator.paginate_queryset(queryset, request)
            serializer = PtqSerializer(result, many=True, fields=["contract"])
            return response_data(data=serializer.data, message=count)
        except:
            return response_data(status=4, message="Server error")

    def show_explanation(self, request):
        type_explanation = ['OK', 'NOT OK', 'ADD']
        # queryset = PtqType.objects.filter(type__in=type_explanation).values('id', 'description')
        # return response_data(queryset)

        data = request.GET.copy()
        email = get_email_from_token(request)
        validate = IdValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message=list(validate.errors.values())[0][0])
        if not Ptq.objects.filter(id=data["id"]).exists():
            return response_data(status=4, message="Chế tài không tồn tại")
        ptq_queryset = Ptq.objects.filter(id=data["id"])
        serializer = PtqSerializer(ptq_queryset, many=True, not_fields=["deletedAt"])
        ptq_data = serializer.data[0]
        history_queryset = PtqHistory.objects.filter(ptq_id=ptq_data["id"])
        serializer = PtqHistorySerializer(history_queryset, many=True, not_fields=["deletedAt"], image=True)
        ptq_history = serializer.data
        isImport = False
        isEdit = False
        rule = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id','description', 'type')
        rule_edit = PtqType.objects.filter(deleted_at__isnull=True, type__in=["NOTOK"]).values_list("id", flat=True)
        if ptq_queryset.filter(updated_by=email).exists():
            isImport = True
        if isImport and not ptq_data["recorded"] in rule_edit:
            isEdit = True
        result = {
            "ptq":ptq_data,
            "ptqHistory":ptq_history,
            "isEdit":isEdit,
            "isImport":isImport
        }
        return response_data(result)

    def delete_ptq_for_edit(self, data):
        validate = IdListValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message="Id error")
        validate = DeleteReasonPtqValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message=validate.errors)
        queryset = DeleteReasonPtq.objects.filter(key_reason=data["reason"], deleted_at__isnull=True).values_list("reason", flat=True)[0]
        status = PtqType.objects.filter(type="DELETED", deleted_at__isnull=True).values_list("id", flat=True)[0]
        if data["reason"] == "OTHER":
            validate = NoteValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            query_update = Ptq.objects.filter(id__in=data["id"])
            query_update.update(note=data["note"], deleted_at=datetime.now(), recorded=status)
            if query_update:
                self.send_noti_deleted(data=query_update[0])
            return response_data(queryset)
        query_update = Ptq.objects.filter(id__in=data["id"])
        query_update.update(note=queryset, deleted_at=datetime.now(), recorded=status)
        if query_update:
            self.send_noti_deleted(data=query_update[0])
        return response_data(data)

    def delete_ptq(self, request):
        data = request.data.copy()
        validate = IdListValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message="Id error")
        validate = DeleteReasonPtqValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message=validate.errors)
        queryset = DeleteReasonPtq.objects.filter(key_reason=data["reason"], deleted_at__isnull=True).values_list("reason", flat=True)[0]
        status = PtqType.objects.filter(type="DELETED", deleted_at__isnull=True).values_list("id", flat=True)[0]
        if data["reason"] == "OTHER":
            validate = NoteValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message=validate.errors)
            query_update = Ptq.objects.filter(id__in=data["id"])
            query_update.update(note=data["note"], deleted_at=datetime.now(), recorded=status)
            return response_data(queryset)
        query_update = Ptq.objects.filter(id__in=data["id"])
        query_update.update(note=queryset, deleted_at=datetime.now(), recorded=status)
        return response_data(queryset)

    def get_delete_ptq(self, request):
        queryset = DeleteReasonPtq.objects.filter(deleted_at__isnull=True).values("id", "reason", "key_reason")
        return response_data(queryset)

    def explanation(self, request):
        data = request.data.copy()
        email = get_email_from_token(request)
        if email is None:
            return response_data(status=5, message="Token không có thông tin")

        userPers = global_data.authUserSessionData["permissions"]
        print(userPers)

        # Truoc tien can check user nay co quyen hay ko. Pass het thi moi thuc hien cong viec delete & edit
        if "delete" in data and data["delete"] != {}:
            # check user nay co quyen "Xoa che tai" hay ko
            if userPers.get("ALL", None) is None and userPers.get("KIEM_SOAT_CHE_TAI_DELETE", None) is None:
                return response_data(status=5, message="Bạn không có quyền thực hiện xóa chế tài!")

        if "edit" in data and data["edit"] != {}:
            # check user nay co quyen "Edit che tai" hay ko
            if userPers.get("ALL", None) is None and userPers.get("KIEM_SOAT_CHE_TAI_EDIT", None) is None:
                return response_data(status=5, message="Bạn không có quyền chỉnh sửa chế tài!")

        # Bat dau thuc hien cong viec delete & edit
        if "delete" in data and data["delete"] != {}:
            print("da vao delete che tai!")
            data_del = data.pop("delete")
            self.delete_ptq_for_edit(data_del)

        if "edit" in data and data["edit"] != {}:
            print("da vao edit che tai!")
            data_edit = data.pop("edit")
            validate = ArrayValidate(data=data_edit)
            if not validate.is_valid():
                return response_data(status=5, message=list(validate.errors.values())[0][0])
            for item in data_edit["array"]:
                self.add_explanation(data=item, email=email)

        return response_data(None)

    def add_explanation(self, data, email):
        validate = IdValidate(data=data)
        if not validate.is_valid():
            return response_data(status=5, message=list(validate.errors.values())[0][0])
        queryset = Ptq.objects.filter(deleted_at__isnull=True, updated_by=email, id=data["id"])
        ptq_save = {}
        feedback_save = {}
        if "deadline" in data and data["deadline"] != "":
            ptq_save["deadline"] = data["deadline"]
        try:
            queryset_deadline = Ptq.objects.get(id=data["id"])
        except:
            return response_data(status=4, message="Id not isset")

        last_status = queryset_deadline.recorded
        if ptq_save != {}:
            data_save = PtqSerializer(queryset_deadline, data=ptq_save)
            data_save.is_valid()
            data_save.save()
        #
        if not queryset.exists():
            return response_data(status=5, message="Bạn không có quyền sửa vì không phải người đã import lên!")
        count_id = PtqHistory.objects.filter(ptq_id=data["id"]).count()
        query_id = PtqHistory.objects.filter(ptq_id=data["id"], times=count_id).values('id')
        try:
            explanation_id = list(query_id)[0]["id"]
        except:
            return response_data(status=5, message="Chưa có giải trình nên chưa được phản hồi")
        if "feedback" in data and data["feedback"] != "":
            feedback_save["feedback"] = data["feedback"]
            validate = StatusValidate(data=data)
            if not validate.is_valid():
                return response_data(status=5, message="Phản hồi phải kèm theo trạng thái, và trạng thái phải hợp lệ")
        feedback_save["status"] = data["status"]
        ptq_save["recorded"] = data["status"]
        if ptq_save != {}:
            data_save = PtqSerializer(queryset_deadline, data=ptq_save)
            data_save.is_valid()
            data_save.save()
        queryset = PtqHistory.objects.get(id=explanation_id)
        # print(explanation_id)
        if feedback_save != {}:
            data_save = PtqHistorySerializer(queryset, data=feedback_save)
            data_save.is_valid()
            data_save.save()
            print(data_save.data)
        if queryset_deadline.recorded != last_status:
            if queryset_deadline.recorded == 4:
                self.send_noti_ptq_approved(data=queryset_deadline)
            if queryset_deadline.recorded == 5:
                self.send_noti_ptq_not_approved(data=queryset_deadline)

        return response_data(data=data)

    def insertReportsToNewPtqTb(self, request):
        limit = request.data.get("limit", 20)
        oldPtqQs = OldPtq.objects.filter(moved=0).order_by("ptq_id")[0:limit]
        oldPtqSr = OldPtqSerializer(oldPtqQs, many=True)
        oldPtqRows = oldPtqSr.data
        if len(oldPtqRows) == 0:
            return response_data(None, 6, "No any old PTQ to move!")

        # return response_data(oldPtqRows)
        for oldPtqRow in oldPtqRows:
            print("dadeline : " + oldPtqRow["deadline"])
            deadlineObj = datetime.strptime(oldPtqRow["deadline"], '%Y-%m-%d')
            deadlineTs = int(deadlineObj.timestamp())
            print("deadline ts : " + str(deadlineObj.timestamp()))

        return response_data(None)

    def explanation_reminder(self, request):
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(1)
            query_expression = Q(recorded__in=[2,7], deadline__in=[today, tomorrow])
            ptq_queryset = Ptq.objects.filter(
                query_expression
            ).values(
                "email",
                "thematic",
                "contract",
                "deadline"
            )

            list_noti = []

            for explanation in ptq_queryset:
                try:
                    data_noti = {
                        "email": explanation['email'],
                        "title":"Bạn có 1 Kiểm soát sắp hết hạn",
                        "body": "Vi phạm về "
                                + (explanation['thematic'] or "---")
                                + " cho Hợp đồng "
                                + explanation['contract']
                                + " của bạn sắp hết hạn vào ngày "
                                + explanation['deadline'].strftime("%d-%m-%Y")
                                + ". Nhấp vào đây để xem chi tiết.",
                        "topic_type" : "PTQ",
                        "notifyDataAction" : "/list-punish",
                        "notifyActionType" : "go_to_screen",
                        "popupDetailDataAction" : "/list-punish",
                        "popupDetailActionType" : "go_to_screen"
                    }
                    list_noti.append(data_noti)
                except Exception as e:
                    print(e)

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            call_api_res = call_api(
                host=SERVICE_CONFIG["NOTIFICATION"][app_env],
                func=SERVICE_CONFIG["NOTIFICATION"]["send-multi-noti-with-diff-content-by-email"]["func"],
                method=SERVICE_CONFIG["NOTIFICATION"]["send-multi-noti-with-diff-content-by-email"]["method"],
                data=list_noti
            )

            return response_data(list_noti, 1, call_api_res)
        except Exception as e:
            print(e)
            return response_data("", 4, str(e))