import json

from dateutil import rrule
from django.db.models import Q

from ..models.kpi import Kpi
from ..models.job_configs import JobConfigs
from ..models.kpi_info import KpiInfo
from ..models.kpi_log import KpiLog
from ..models.kpi_task import KpiTask
from ..serializers.job_configs_serializer import JobConfigsSerializer
from ..serializers.kpi_info_serializer import KpiInfoSerializer
from ..serializers.kpi_serializer import KpiSerializer
from ..serializers.kpi_task_serializer import KpiTaskSerializer
from ...core.helpers.global_variable import *
from ...core.helpers.my_datetime import *
from ...core.helpers.response import *
from ...core.helpers.helper import *
import redis
from django.conf import settings as project_settings
from app.configs import app_settings
from rest_framework.viewsets import ViewSet
import ast
from datetime import datetime, timedelta
import xlsxwriter
import os
import pandas as pd
from django.db import transaction

from ...core.helpers.utils import get_client_ip, get_current_datetime


def save_log_kpi_from_isc(**kwargs):
    api_input = kwargs.pop('api_input', None)
    url = kwargs.pop('url', None)
    ip_address = kwargs.pop('ip_address', None)
    api_output = kwargs.pop('api_output', None)
    try:
        dataSave = KpiLog(api_input=api_input, url=url, ip_address=ip_address, api_output=api_output)
        dataSave.save()
    except Exception as ex:
        print("Log kpi")
        print(str(ex))
        return False
    return True


def import_kpi_contract(**kwargs):
    empCode = kwargs.pop('empCode', None)
    account = kwargs.pop('account', None)
    status = kwargs.pop('status', None)
    contract = kwargs.pop('contract', None)
    timeComplete = kwargs.pop('timeComplete', None)
    timeStartCl1 = kwargs.pop('timeStartCl1', None)
    timeCompleteCl1 = kwargs.pop('timeCompleteCl1', None)
    timeStartCl2 = kwargs.pop('timeStartCl2', None)
    timeCompletePtc = kwargs.pop('timeCompletePtc', None)
    contract_tye = kwargs.pop('type', None)
    date = kwargs.pop('date', None)

    info_kpi = {
        "empCode": empCode,
        "accountMbn": account,
        "status": status,
        "contract": contract,
        "timeComplete": timeComplete,
        "timeStartCl1": timeStartCl1,
        "timeCompleteCl1": timeCompleteCl1,
        "timeStartCl2": timeStartCl2,
        "timeCompletePtc": timeCompletePtc,
        "kpiType": contract_tye,
        "kpiDate": date
    }

    serializer = KpiSerializer(data=info_kpi)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return True


class KpiView(ViewSet):
    def add_info_kpi(self, request):
        """
        kpi_ontime: Đúng hẹn (TK + BT)
        kpi_sla: Tỷ lệ triển khai bảo trì được tích hẹn và hoàn tất trong ngày
        kpi_2cl: Số Checklist lặp (>=2/30 ngày)
        kpi_3cl: Số Checklist lặp (>3/30 ngày)
        kpi_csat_cldv: CSAT Chất lượng dịch vụ
        kpi_csat_nvkt: CSAT Nhân viên kỹ thuật
        kpi_clps_7n: Tổng số lượng checklist 7 ngày (TK + BT)
        """
        try:
            getData = request.data

            dataInputText = str(getData)
            urlText = request.get_full_path()
            ipText = get_client_ip(request)
            save_log_kpi_from_isc(api_input=dataInputText, url=urlText, ip_address=ipText)

            if getData is not None:
                for data in getData:
                    info_kpi = {
                        "emp_code": data['emp_code'],
                        "account_mbn": data['emp_id'],
                        "ontime_tk": 0,
                        "late_tk": 0,
                        "ontime_bt": 0,
                        "late_bt": 0,
                        "count_cl2": 0,
                        "count_cl3": 0,
                        "count_cl7n_bt": 0,
                        "count_cl7n_tk": 0,
                        "count_shift_complete_sla_tk": 0,
                        "count_shift_sla_tk": 0,
                        "count_shift_complete_sla_bt": 0,
                        "count_shift_sla_bt": 0,
                        "customer_cl": data['count_customer_cl'],
                        "kpi_date": data['kpi_date']
                    }
                    kpi_type = ""
                    status = ""

                    # kpi_tk - status: late
                    if 'kpi_tk' in data.keys():
                        kpi_type = 'kpi_tk'
                        info_kpi['ontime_tk'] = data[kpi_type]['count_ontime']
                        info_kpi['late_tk'] = data[kpi_type]['count_late']
                        if 'list_contract_late' in data[kpi_type]:
                            list_contract = data[kpi_type]['list_contract_late']
                            status = "late"
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    status=status,
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                        # kpi_tk - status: ontime
                        if 'list_contract_ontime' in data[kpi_type]:
                            list_contract = data[kpi_type]['list_contract_ontime']
                            status = "ontime"
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    status=status,
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # kpi_bt - status: late
                    if 'kpi_bt' in data.keys():
                        kpi_type = 'kpi_bt'
                        info_kpi['ontime_bt'] = data[kpi_type]['count_ontime']
                        info_kpi['late_bt'] = data[kpi_type]['count_late']
                        if 'list_contract_late' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract_late']
                            status = "late"
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    status=status,
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                        # kpi_bt - status: ontime
                        if 'list_contract_ontime' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract_ontime']
                            status = "ontime"
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    status=status,
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # kpi_2cl
                    if 'kh2cl' in data.keys():
                        kpi_type = 'kh2cl'
                        info_kpi['count_cl2'] = data[kpi_type]['count_cl']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete_cl0'],
                                                    timeStartCl1=contract['time_start_cl1'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # kpi_3cl
                    if 'kh3cl' in data.keys():
                        kpi_type = 'kh3cl'
                        info_kpi['count_cl3'] = data[kpi_type]['count_cl']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeCompleteCl1=contract['time_complete_cl1'],
                                                    timeStartCl2=contract['time_start_cl2'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # cl_7n_bt
                    if 'cl_7n_bt' in data.keys():
                        kpi_type = 'cl_7n_bt'
                        info_kpi['count_cl7n_bt'] = data[kpi_type]['count_cl']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete_cl0'],
                                                    timeStartCl1=contract['time_start_cl1'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # cl_7n_tk
                    if 'cl_7n_tk' in data.keys():
                        kpi_type = 'cl_7n_tk'
                        info_kpi['count_cl7n_tk'] = data[kpi_type]['count_cl']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeStartCl1=contract['time_start_cl'],
                                                    timeCompletePtc=contract['time_complete_ptc'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # sla_tk
                    if 'sla_tk' in data.keys():
                        kpi_type = 'sla_tk'
                        info_kpi['count_shift_complete_sla_tk'] = data[kpi_type]['count_shift_complete']
                        info_kpi['count_shift_sla_tk'] = data[kpi_type]['count_shift']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    timeStartCl1=contract['time_start_cl1'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # sla_bt
                    if 'sla_bt' in data.keys():
                        kpi_type = 'sla_bt'
                        info_kpi['count_shift_complete_sla_bt'] = data[kpi_type]['count_shift_complete']
                        info_kpi['count_shift_sla_bt'] = data[kpi_type]['count_shift']
                        if 'list_contract' in data[kpi_type].keys():
                            list_contract = data[kpi_type]['list_contract']
                            for contract in list_contract:
                                import_kpi_contract(empCode=info_kpi['emp_code'],
                                                    account=info_kpi['account_mbn'],
                                                    contract=contract['contract'],
                                                    timeComplete=contract['time_complete'],
                                                    timeStartCl1=contract['time_start_cl1'],
                                                    type=kpi_type,
                                                    date=info_kpi['kpi_date'])

                    # save kpi_task.py
                    serializer = KpiTaskSerializer(data=info_kpi)
                    if serializer.is_valid():
                        serializer.save()
                return response_data(data=info_kpi)
            else:
                return response_data(data=None, message="Data null")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.add_info_kpi.__name__, ex))
            KpiLog.objects.filter(api_input=dataInputText).update(api_output=str(ex))
            return response_data(message=str(ex), data=None)

    def update_info_kpi(self, request):
        try:
            getData = request.data

            dataInputText = str(getData)
            urlText = request.get_full_path()
            ipText = get_client_ip(request)
            save_log_kpi_from_isc(api_input=dataInputText, url=urlText, ip_address=ipText)

            if getData is not None:
                for data in getData:
                    code = data['emp_code']
                    account = data['emp_id']
                    kpiDate = data['kpi_date']
                    customerCL = data['count_customer_cl']
                    dataKpi = KpiTask.objects.filter((Q(emp_code=code) | Q(account_mbn=account)), kpi_date=kpiDate)
                    if dataKpi:
                        Kpi.objects.filter((Q(emp_code=code) | Q(account_mbn=account)), kpi_date=kpiDate).delete()
                        info_kpi = {
                            "emp_code": code,
                            "account_mbn": account,
                            "ontime_tk": 0,
                            "late_tk": 0,
                            "ontime_bt": 0,
                            "late_bt": 0,
                            "count_cl2": 0,
                            "count_cl3": 0,
                            "count_cl7n_bt": 0,
                            "count_cl7n_tk": 0,
                            "count_shift_complete_sla_tk": 0,
                            "count_shift_sla_tk": 0,
                            "count_shift_complete_sla_bt": 0,
                            "count_shift_sla_bt": 0,
                            "customer_cl": customerCL,
                            "kpi_date": kpiDate
                        }
                        kpi_type = ""
                        status = ""

                        # kpi_tk - status: late
                        if 'kpi_tk' in data.keys():
                            kpi_type = 'kpi_tk'
                            info_kpi['ontime_tk'] = data[kpi_type]['count_ontime']
                            info_kpi['late_tk'] = data[kpi_type]['count_late']
                            if 'list_contract_late' in data[kpi_type]:
                                list_contract = data[kpi_type]['list_contract_late']
                                status = "late"
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        status=status,
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                            # kpi_tk - status: ontime
                            if 'list_contract_ontime' in data[kpi_type]:
                                list_contract = data[kpi_type]['list_contract_ontime']
                                status = "ontime"
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        status=status,
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # kpi_bt - status: late
                        if 'kpi_bt' in data.keys():
                            kpi_type = 'kpi_bt'
                            info_kpi['ontime_bt'] = data[kpi_type]['count_ontime']
                            info_kpi['late_bt'] = data[kpi_type]['count_late']
                            if 'list_contract_late' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract_late']
                                status = "late"
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        status=status,
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                            # kpi_bt - status: ontime
                            if 'list_contract_ontime' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract_ontime']
                                status = "ontime"
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        status=status,
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # kpi_2cl
                        if 'kh2cl' in data.keys():
                            kpi_type = 'kh2cl'
                            info_kpi['count_cl2'] = data[kpi_type]['count_cl']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete_cl0'],
                                                        timeStartCl1=contract['time_start_cl1'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # kpi_3cl
                        if 'kh3cl' in data.keys():
                            kpi_type = 'kh3cl'
                            info_kpi['count_cl3'] = data[kpi_type]['count_cl']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeCompleteCl1=contract['time_complete_cl1'],
                                                        timeStartCl2=contract['time_start_cl2'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # cl_7n_bt
                        if 'cl_7n_bt' in data.keys():
                            kpi_type = 'cl_7n_bt'
                            info_kpi['count_cl7n_bt'] = data[kpi_type]['count_cl']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete_cl0'],
                                                        timeStartCl1=contract['time_start_cl1'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # cl_7n_tk
                        if 'cl_7n_tk' in data.keys():
                            kpi_type = 'cl_7n_tk'
                            info_kpi['count_cl7n_tk'] = data[kpi_type]['count_cl']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeStartCl1=contract['time_start_cl'],
                                                        timeCompletePtc=contract['time_complete_ptc'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # sla_tk
                        if 'sla_tk' in data.keys():
                            kpi_type = 'sla_tk'
                            info_kpi['count_shift_complete_sla_tk'] = data[kpi_type]['count_shift_complete']
                            info_kpi['count_shift_sla_tk'] = data[kpi_type]['count_shift']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        timeStartCl1=contract['time_start_cl1'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                        # sla_bt
                        if 'sla_bt' in data.keys():
                            kpi_type = 'sla_bt'
                            info_kpi['count_shift_complete_sla_bt'] = data[kpi_type]['count_shift_complete']
                            info_kpi['count_shift_sla_bt'] = data[kpi_type]['count_shift']
                            if 'list_contract' in data[kpi_type].keys():
                                list_contract = data[kpi_type]['list_contract']
                                for contract in list_contract:
                                    import_kpi_contract(empCode=info_kpi['emp_code'],
                                                        account=info_kpi['account_mbn'],
                                                        contract=contract['contract'],
                                                        timeComplete=contract['time_complete'],
                                                        timeStartCl1=contract['time_start_cl1'],
                                                        type=kpi_type,
                                                        date=info_kpi['kpi_date'])

                    # save kpi_task.py
                    dataKpi.update(ontime_tk=info_kpi['ontime_tk'],
                                   late_tk=info_kpi['late_tk'],
                                   ontimebt=info_kpi['ontime_bt'],
                                   late_bt=info_kpi['late_bt'],
                                   count_cl2=info_kpi['count_cl2'],
                                   count_cl3=info_kpi['count_cl3'],
                                   count_cl7n_bt=info_kpi['count_cl7n_bt'],
                                   count_cl7n_tk=info_kpi['count_cl7n_tk'],
                                   count_shift_complete_sla_tk=info_kpi['count_shift_complete_sla_tk'],
                                   count_shift_complete_sla_bt=info_kpi['count_shift_complete_sla_bt'],
                                   count_shift_sla_tk=info_kpi['count_shift_sla_tk'],
                                   count_shift_sla_bt=info_kpi['count_shift_sla_bt'],
                                   customer_cl=customerCL,
                                   updated_date=get_current_datetime())
            else:
                return response_data(data=None, message="Data null")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_info_kpi.__name__, ex))
            KpiLog.objects.filter(api_input=dataInputText).update(api_output=str(ex))
            return response_data(data=None, status=0, message=MESSAGE_API_FAILED)
        return response_data(data=getData, message="Update thành công")

    def get_all_fake_data_by_email(self, request):
        try:
            queryset = JobConfigs.objects.filter(config_key='KPI_EMPLOYEES_FAKE_INFO').first()
            dataJson = json.loads(queryset.config_value)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_all_fake_data_by_email.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(dataJson)

    def update_all_fake_data_by_email(self, request):
        try:
            getData = request.data
            JobConfigs.objects.filter(config_key='KPI_EMPLOYEES_FAKE_INFO').update(config_value=json.dumps(getData))

            redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                               , port=project_settings.REDIS_PORT_CENTRALIZED
                                               , db=project_settings.REDIS_INFO_KPI_DATABASE_CENTRALIZED,
                                               password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                               , decode_responses=True, charset="utf-8")

            secondTimeOut = getSecondFromNowToLastOfDay()
            redis_instance.set('fakeAccountInfo', json.dumps(getData), secondTimeOut)

        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_all_fake_data_by_email.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return response_data(data=None, message="Cập nhật thành công")

    def get_info_value_kpi_by_type(self, request):
        try:
            result = {}
            getData = request.GET
            queryset = KpiInfo.objects.filter(kpi_type=getData['type']).first()
            result['id'] = queryset.id
            result['kpi_type'] = queryset.kpi_type
            result['kpi_value'] = json.loads(queryset.kpi_value)
            result['title'] = queryset.title
            result['description'] = queryset.description
            result['year'] = queryset.year
            result['target'] = queryset.target
            result['owner'] = queryset.owner
            result['date_created'] = queryset.date_created
            data = json.dumps(result['kpi_value'])

            # KpiInfo.objects.filter(kpi_type=getData['type']).update(kpi_value=data)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_info_value_kpi_by_type.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(result)

    # API gọi nội bộ dùng để xử lý thông tin emp_code = 0 thành file excel
    def get_accountMBN_code_by_zero(self, request):
        try:
            result = {}
            queryset = KpiTask.objects.filter(emp_code='0').values_list('account_mbn', flat=True).distinct()
            result['count'] = len(queryset)
            result['data'] = queryset

            path = "C:/Users/" + os.getlogin() + "/Downloads"
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)

            workbook = xlsxwriter.Workbook(path + "/" + 'get_accountMBN_code_by_zero.xlsx')
            worksheet = workbook.add_worksheet()

            # Start from the first cell.
            # Rows and columns are zero indexed.
            row = 1
            column = 1

            content = queryset

            worksheet.write(0, 0, "code")
            worksheet.write(0, 1, "account")
            # iterating through content list
            for item in content:
                # write operation perform
                worksheet.write(row, column, item)

                # incrementing the value of row by one
                # with each iterations.
                row += 1

            workbook.close()
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_accountMBN_code_by_zero.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return response_data(data=result)

    def convert_xlsx_to_json(self, request):
        try:
            result = {}
            getData = request.FILES['file_xlsx']
            dataExcel = pd.read_excel(getData)
            data = dataExcel.to_dict(orient='records')
            result = data

            data_string = json.dumps(data, sort_keys=True, indent=4)

            path = "C:/Users/" + os.getlogin() + "/Downloads"
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)

            # write file json
            myJsonFile = open(path + "/" + "info.json", "w")
            myJsonFile.write(data_string)
            myJsonFile.close()
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.convert_xlsx_to_json.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(result)

    # update lại emp_code theo accountMBN
    def update_code_by_accountMBN(self, request):
        try:
            result = {}
            getData = request.data
            with transaction.atomic():
                for data in getData:
                    if data['code'] != 8:
                        data['code'] = str(data['code']).zfill(8)
                        KpiTask.objects.filter(account_mbn=data['account']).update(emp_code=data['code'])
                        Kpi.objects.filter(account_mbn=data['account']).update(emp_code=data['code'])
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_code_by_accountMBN.__name__, ex))
            return response_data(data=None, status=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED + ": " + str(ex))
        return Response(result)
