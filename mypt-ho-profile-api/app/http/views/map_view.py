from ...core.helpers.global_variable import *
from ...core.helpers.call_api import *
from ...core.helpers.utils import *
from ...core.helpers.response import *
from rest_framework.viewsets import ViewSet
# from ..serializers.info_block_serializer import *
from ..serializers.map_department_serializer import *
from ..serializers.hr_serializer import *
from collections import Counter, OrderedDict

class MapView(ViewSet):
    def api_get_map_coordinate(self, request):
        fname = "api_get_map_coordinate"
        try:
            time_log = get_str_datetime_now_import_db()
            # query = InfoBlock.objects.all().values_list('agency_inside', flat=True)
            # if len(query) == 0:
            #     return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)
            # list_data = list(query)
            # data_block = dict(Counter(list_data))
            data_api = call_api_count_block_according_to_agency(time_log, fname)
            data_block = data_api.get("dict_count", {})

            # query_manager = InfoBlock.objects.all().exclude(manager_email='').values_list('agency_inside', flat=True)
            query_manager = Employee.objects.filter(job_title='CB Quản lý thuê bao').values_list('child_depart', flat=True)
            list_email = list(query_manager)
            data_email = dict(Counter(list_email))
            dict_data_email = {}



            # query_block = InfoBlock.objects.all().values_list('block_name', flat=True)
            # dict_emp_on_block = call_api_get_emp_on_block(list(query_block), get_str_date_now_import_db() )
            query_emp = Employee.objects.filter(job_title='CB Kỹ thuật TKBT').values_list('child_depart', flat=True)
            list_emp = list(query_emp)
            data_emp = dict(Counter(list_emp))

            dict_data = {}


            # query_agency = InfoBlock.objects.all().values('agency_inside', 'block_name')
            query_agency = Department.objects.all().values('child_depart', 'chi_nhanh')

            print(444)

            for i in query_agency:
                child_depart = i['child_depart']
                chi_nhanh = i['chi_nhanh']

                number_emp = data_emp.get(child_depart, 0)
                number_exist = dict_data.get(chi_nhanh, 0)
                number_exist = number_exist + number_emp
                dict_data.update({
                    chi_nhanh: number_exist
                })

                number_manager = data_email.get(child_depart, 0)
                number_manager_exist = dict_data_email.get(chi_nhanh, 0)
                number_manager_exist = number_manager_exist  + number_manager
                dict_data_email.update({
                    chi_nhanh: number_manager_exist
                })





            # for i in query_agency:
            #     agency = i['agency_inside']
            #     block_name = i['block_name']
            #     number_emp = dict_emp_on_block.get(block_name, 0)
            #
            #     number_exist = dict_data.get(agency, 0)
            #     number_exist = number_exist + number_emp
            #     dict_data.update({
            #         agency: number_exist
            #     })

            query_detail = MapDepartment.objects.all().values()

            list_detail = []
            for j in query_detail:
                agency_hris = j['agency']
                agency_inside = j['agency_inside']
                dict_tmp = j.copy()
                number_emp_ = dict_data.get(agency_hris, 0)

                number_block = data_block.get(agency_inside, 0)

                number_email = dict_data_email.get(agency_hris, 0)

                dict_tmp.update({
                    "numberEmp": number_emp_,
                    "numberBlock": number_block,
                    "numberManager": number_email
                })
                list_detail.append(dict_tmp)

            return response_data(data=list_detail, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)





        except Exception as ex:
            return response_data(data=str(ex), message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)


    def api_get_detail_info_emp(self, request):
        fname = "get_detail_info_emp"
        data_input = request.data
        emp_code = data_input.get("empCode", '')
        email = data_input.get("email", '')
        name = data_input.get("name", "")
        agency_inside_input = data_input.get("agencyInside")
        job_title_input = data_input.get("jobTitle")
        try:

            time_log = get_str_datetime_now_import_db()

            queryset = None
            # query_child_depart = None
            list_child_depart = []
            if not is_null_or_empty(email):
                queryset = Employee.objects.filter(email=email)
                queryset_child_depart = Employee.objects.filter(email=email).values_list('child_depart', flat=True)
                list_child_depart = list(queryset_child_depart)
            elif not is_null_or_empty(name):
                # queryset = Employee.objects.filter(emp_name__in=tuple(list_name)).values('emp_code', 'emp_name', 'email', 'child_depart')
                queryset = Employee.objects.filter(emp_name__icontains=name)
                queryset_child_depart = Employee.objects.filter(emp_name__icontains=name).values_list('child_depart', flat=True)
                list_child_depart = list(queryset_child_depart)
            elif not is_null_or_empty(emp_code):
                queryset = Employee.objects.filter(emp_code= emp_code)
                queryset_child_depart = Employee.objects.filter(emp_code=emp_code).values_list('child_depart', flat=True)
                list_child_depart = list(queryset_child_depart)
            elif not is_null_or_empty(agency_inside_input) and not is_null_or_empty(job_title_input):
                query_agency = MapDepartment.objects.filter(agency_inside=agency_inside_input).values_list('agency', flat=True)
                qr_child_depart = Department.objects.filter(chi_nhanh__in=list(query_agency)).values_list('child_depart', flat=True)
                queryset = Employee.objects.filter(job_title=job_title_input, child_depart__in=list(qr_child_depart))

                queryset_child_depart = Employee.objects.filter(job_title=job_title_input, child_depart__in=list(qr_child_depart)).values_list('child_depart',
                                                                                               flat=True)
                list_child_depart = list(queryset_child_depart)

            else:
                return response_data(data={}, message=MESSAGE_API_NO_INPUT, status=STATUS_CODE_INVALID_INPUT)

            queryset = queryset.values('emp_code', 'emp_name','email', 'child_depart', 'job_title')
            list_emp_code = []
            for i in queryset:
                list_emp_code.append(i['emp_code'])

            if len(queryset) == 0:
                return response_data(data={}, message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


            list_data = []
            dict_info_child_depart = DepartmentSerializer.get_parent_depart_from_child_depart(list_child_depart)
            dict_info_block = call_api_info_block_from_emp_code(list_emp_code, get_str_datetime_now_import_db())


            for i in queryset:
                dict_info = {}
                emp_code_rs = i['emp_code']
                dict_info['empCode'] = emp_code_rs
                dict_info['empName'] = i['emp_name']
                dict_info['email'] = i['email']
                dict_info['jobTitle'] = i['job_title']
                # dict_child_depart = dict_info_child_depart.get(i['child_depart'], {})
                child_depart_item = i['child_depart']
                # dict_info_child_depart = DepartmentSerializer.get_parent_depart_from_child_depart([child_depart_item])
                dict_child_depart = dict_info_child_depart.get(i['child_depart'], {})
                dict_info['childDepart'] = i['child_depart']
                agency = dict_child_depart.get('department', '')
                dict_info['agency'] = agency
                dict_info['parentDepart'] = dict_child_depart.get('parentDepart', '')
                dict_info['company'] = dict_child_depart.get('branch', '')
                dict_info['dict_child_depart'] = dict_child_depart
                dict_info['dict_info_child_depart'] = dict_info_child_depart

                dict_detail_block = dict_info_block.get(emp_code_rs, {})
                block_name = dict_detail_block.get('block_name', '')
                # qr_agency_inside = InfoBlock.objects.filter(block_name=block_name).values_list('agency_inside', flat=True)
                # list_agency_inside_rs = list(qr_agency_inside)
                agency_inside_rs = ''
                lat = ""
                long = ""

                data_api = call_api_count_block_according_to_agency(time_now=time_log, fname=fname)
                list_agency_inside_rs = data_api.get("list_data", [])
                if len(list_agency_inside_rs) > 0 :
                    agency_inside_rs = list_agency_inside_rs[0]
                    qr_coordinate = MapDepartment.objects.filter(agency_inside=agency_inside_rs).values('lat', 'long')
                    if len(qr_coordinate) > 0:
                        lat = qr_coordinate[0]['lat']
                        long = qr_coordinate[0]['long']

                dict_info['agencyInside'] = agency_inside_rs
                dict_info['lat'] = lat
                dict_info['long'] = long


                list_data.append(dict_info)
            return response_data(data=list_data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)






        except Exception as ex:
            print("{} >> {} >> Error/Loi: {}".format(get_str_datetime_now_import_db(), fname, ex))
            return response_data(data={}, message=MESSAGE_API_ERROR_LOGIC, status=STATUS_CODE_ERROR_LOGIC)