import json
import datetime
import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.viewsets import ViewSet
from ..models.hr import Employee
from ...core.helpers.mapping import mapping, data_mapping
from ...configs.mapping import *
from ..serializers.hr_serializer import EmployeeSerializer
from ...core.helpers.call_api import call_api
from ...configs.service_api_config import SERVICE_CONFIG
from ...core.helpers.response import response_data
from django.core.exceptions import ObjectDoesNotExist
from ..serializers.employee_qualification_serializer import EmployeeQualificationSerializer
from ..serializers.employee_certificate_serializer import EmployeeCertificateSerializer
from ..models.employee_qualification import EmployeeQualification
from ..models.employee_certificate import EmployeeCertificate
from ..validations.employee_validate import RequiredEmployeeCodeValidate

class SyncDataViewset(ViewSet):
    HRIS_TOKEN = ""

    def hris_login(self, request=None):
        try:
            env = settings.APP_ENVIRONMENT or "production"
            hris_data = SERVICE_CONFIG['HRIS']

            response = requests.request(
                hris_data["login"]["method"],
                f"{hris_data['domain'][env]}{hris_data['login']['url']}",
                data=json.dumps(hris_data["login"]["body"]),
                headers=hris_data["login"]["headers"]
            )
            token = response.json()
            cache.set(
                key="HRIS_TOKEN", 
                value=token["authorization"],
                timeout=token["expireInSeconds"] - 30*60
            )
            return response_data(token["authorization"])
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")

    def sync_employees_data(self, request):
        try:
            today = datetime.datetime.now()
            yesterday = (today - datetime.timedelta(1)).strftime("%Y-%m-%dT00:00:00Z")
            hris_payload = cache.get("HRIS_EMPLOYEE_PAYLOAD")
        
            if hris_payload is None:
                hris_payload = {
                    "lastUpdatedDate": yesterday,
                    "pageIndex": 1,
                    "pageSize": 50
                }
            elif dict.__subclasscheck__(hris_payload.__class__):
                if hris_payload.get("done", False) is True: # is True mới return, truthy vẫn tiếp tục
                    return response_data("Done")
            else:
                return response_data("Error")
            token = cache.get("HRIS_TOKEN")
            if token is None:
                token = self.hris_login().data["data"]
            env = settings.APP_ENVIRONMENT or "production"
            hris_data = SERVICE_CONFIG['HRIS']
            hris_api = hris_data["get_list_employees"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = call_api(
                hris_api["method"],
                hris_data["domain"][env] + hris_api["url"],
                headers=headers,
                data=hris_payload
            )
            if response.status_code != 200:
                return response_data(response.text)
            payload = response.json()
            dataset = payload["items"]
            errors = []
            create_count = 0
            update_count = 0
            for data in dataset:
                data = mapping(data, EMPLOYEE_HRIS_PATTERN)
                data = data_mapping(data, EMPLOYEE_HRIS_VALUE_PATTERN)
                try:
                    instance = Employee.objects.get(email=data["email"])
                    new_instance = EmployeeSerializer(instance=instance, data=data)

                    if new_instance.is_valid():
                        if new_instance.save():
                            update_count += 1

                    else:
                        errors.append(new_instance.errors)

                except ObjectDoesNotExist as obj_not_found:
                    new_instance = EmployeeSerializer(data=data)
                    if new_instance.is_valid():
                        if new_instance.save():
                            create_count += 1
                    else:
                        errors.append(new_instance.errors)

            hris_payload["pageIndex"] += 1
            
            if hris_payload["pageIndex"] > payload["totalPages"]:
                cache.set("HRIS_EMPLOYEE_PAYLOAD", {"done": True}, timeout=6*60*60)
                return response_data({
                    "hris_data": hris_payload,
                    "errors": errors,
                    "create_count": create_count,
                    "update_count": update_count,
                    "done": True
                })
            else:
                cache.set("HRIS_EMPLOYEE_PAYLOAD", hris_payload, timeout=6*60*60)
                return response_data({
                    "hris_data": hris_payload,
                    "errors": errors,
                    "create_count": create_count,
                    "update_count": update_count
                })
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
        
    def sync_employee_qualification_data(self, request=None):
        try:
            today = datetime.datetime.now()
            yesterday = (today - datetime.timedelta(1)).strftime("%Y-%m-%dT00:00:00Z")
            hris_payload = cache.get("HRIS_QUALIFICATION_PAYLOAD")
            if hris_payload is None:
                hris_payload = {
                    "lastUpdatedDate": yesterday,
                    "pageIndex": 1,
                    "pageSize": 20
                }
            elif dict.__subclasscheck__(hris_payload.__class__):
                if hris_payload.get("done", False) is True: # is True mới return, truthy vẫn tiếp tục
                    return response_data("Done")
            else:
                return response_data("Error")
            token = cache.get("HRIS_TOKEN")
            if token is None:
                token = self.hris_login().data["data"]
            env = settings.APP_ENVIRONMENT or "production"
            hris_data = SERVICE_CONFIG['HRIS']
            hris_api = hris_data["get_list_employees_qualification"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = call_api(
                hris_api["method"],
                hris_data["domain"][env] + hris_api["url"],
                headers=headers,
                data=hris_payload
            )

            payload = response.json()
            dataset = payload["items"]

            errors = []
            for data in dataset:
                data = mapping(data, EMPLOYEE_HRIS_QUALIFICATION_PATTERN)
                data = data_mapping(data, EMPLOYEE_HRIS_QUALIFICATION_VALUE_PATTERN)

                try:
                    instance = EmployeeQualification.objects.get(inside_id=data["inside_id"])
                    new_instance = EmployeeQualificationSerializer(instance=instance, data=data)

                    if new_instance.is_valid():
                        new_instance.save()
                    else:
                        errors.append(new_instance.errors)

                except ObjectDoesNotExist as obj_not_found:
                    new_instance = EmployeeQualificationSerializer(data=data)

                    if new_instance.is_valid():
                        new_instance.save()
                    else:
                        errors.append(new_instance.errors)
                    
            hris_payload["pageIndex"] += 1
            if hris_payload["pageIndex"] > payload["totalPages"]:
                cache.set("HRIS_QUALIFICATION_PAYLOAD", {"done": True}, timeout=6*60*60)
                return response_data({
                    "hris_data": hris_payload,
                    "errors": errors,
                    "done": True
                })
            else:
                cache.set("HRIS_QUALIFICATION_PAYLOAD", hris_payload, timeout=6*60*60)
            return response_data({
                "hris_data": hris_payload,
                "errors": errors
            })
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
        
    def sync_employee_certificate_data(self, request=None):
        try:
            today = datetime.datetime.now()
            yesterday = (today - datetime.timedelta(1)).strftime("%Y-%m-%dT00:00:00Z")
            hris_payload = cache.get("HRIS_CERTIFICATE_PAYLOAD")
            if hris_payload is None:
                hris_payload = {
                    "lastUpdatedDate": yesterday,
                    "pageIndex": 1,
                    "pageSize": 20
                }
            elif dict.__subclasscheck__(hris_payload.__class__):
                if hris_payload.get("done", False) is True: # is True mới return, truthy vẫn tiếp tục
                    return response_data("Done")
            else:
                return response_data("Error")
            token = cache.get("HRIS_TOKEN")
            if token is None:
                token = self.hris_login().data["data"]
            env = settings.APP_ENVIRONMENT or "production"
            hris_data = SERVICE_CONFIG['HRIS']
            hris_api = hris_data["get_list_employees_certificate"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = call_api(
                hris_api["method"],
                hris_data["domain"][env] + hris_api["url"],
                headers=headers,
                data=hris_payload
            )

            payload = response.json()
            dataset = payload["items"]
            errors = []
            for data in dataset:
                data = mapping(data, EMPLOYEE_HRIS_CERTIFICATE_PATTERN)
                data = data_mapping(data, EMPLOYEE_HRIS_CERTIFICATE_VALUE_PATTERN)

                try:
                    instance = EmployeeCertificate.objects.get(inside_id=data["inside_id"])
                    new_instance = EmployeeCertificateSerializer(instance=instance, data=data)

                    if new_instance.is_valid():
                        new_instance.save()
                    else:
                        errors.append(new_instance.errors)
                except ObjectDoesNotExist as obj_not_found:
                    new_instance = EmployeeCertificateSerializer(data=data)

                    if new_instance.is_valid():
                        new_instance.save()
                    else:
                        errors.append(new_instance.errors)
            hris_payload["pageIndex"] += 1
            if hris_payload["pageIndex"] > payload["totalPages"]:
                cache.set("HRIS_CERTIFICATE_PAYLOAD", {"done": True}, timeout=6*60*60)
                return response_data({
                    "hris_data": hris_payload,
                    "errors": errors,
                    "done": True
                })
            else:
                cache.set("HRIS_CERTIFICATE_PAYLOAD", hris_payload, timeout=6*60*60)
            return response_data({
                "hris_data": hris_payload,
                "errors": errors
            })
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
        
    def view_cache(self, request):
        """temporary API for testing"""
        try:
            data = request.data.copy()

            if "key" not in data:
                return response_data("key?", 4, "")
            return response_data(cache.get(data["key"]))
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
        
    def sync_specified_employee_data(self, request):
        try:
            data = request.data.copy()
            validate = RequiredEmployeeCodeValidate(data=data)

            if not validate.is_valid():
                return response_data(validate.errors, 4, "Invalid input data!")
            
            hris_payload = {
                "employeeCode": validate.validated_data["employee_code"],
                "lastUpdatedDate": "",
                "pageIndex": 1,
                "pageSize": 1
            }
                
            token = cache.get("HRIS_TOKEN")
            if token is None:
                token = self.hris_login().data["data"]
            env = settings.APP_ENVIRONMENT or "production"
            hris_data = SERVICE_CONFIG['HRIS']
            hris_api = hris_data["get_list_employees"]
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = call_api(
                hris_api["method"],
                hris_data["domain"][env] + hris_api["url"],
                headers=headers,
                data=hris_payload
            )
            print(response.text)
            if response.status_code != 200:
                return response_data(response.text)
            payload = response.json()
            dataset = payload["items"]

            if len(dataset) == 0:
                return response_data(
                    "Employee not found!", 
                    4, 
                    "Không tồn tại thông tin nhân viên từ HRIS!"
                )
            data = dataset[0]
            data = mapping(data, EMPLOYEE_HRIS_PATTERN)
            data = data_mapping(data, EMPLOYEE_HRIS_VALUE_PATTERN)

            try:
                instance = Employee.objects.get(emp_code=data["code"])
                new_instance = EmployeeSerializer(instance=instance, data=data)

                if new_instance.is_valid():
                    new_instance.save()
                    return response_data(None, 1, "Đồng bộ thành công!")
                else:
                    return response_data(new_instance.errors, 4, "Đồng bộ thất bại!")
            except ObjectDoesNotExist as obj_not_found:
                new_instance = EmployeeSerializer(data=data)
                if new_instance.is_valid():
                    new_instance.save()
                    return response_data(None, 1, "Đồng bộ thành công!")
                else:
                    return response_data(new_instance.errors, 4, "Đồng bộ thất bại!")

        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
        
    def sync_employees_data_all(self, request):
        try:
            errors = []
            create_count = 0
            update_count = 0

            for i in range(1, 20):
                hris_payload = {
                    "lastUpdatedDate": "",
                    "pageIndex": i,
                    "pageSize": 1000
                }
                
                token = cache.get("HRIS_TOKEN")
                if token is None:
                    token = self.hris_login().data["data"]
                env = settings.APP_ENVIRONMENT or "production"
                hris_data = SERVICE_CONFIG['HRIS']
                hris_api = hris_data["get_list_employees"]
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
                
                response = call_api(
                    hris_api["method"],
                    hris_data["domain"][env] + hris_api["url"],
                    headers=headers,
                    data=hris_payload
                )
                if response.status_code != 200:
                    return response_data(response.text)
                payload = response.json()
                dataset = payload["items"]
                
                for data in dataset:
                    data = mapping(data, EMPLOYEE_HRIS_PATTERN)
                    data = data_mapping(data, EMPLOYEE_HRIS_VALUE_PATTERN)
                    try:
                        instance = Employee.objects.get(email=data["email"])
                        new_instance = EmployeeSerializer(instance=instance, data=data)

                        if new_instance.is_valid():
                            new_instance.save()
                            create_count += 1
                        else:
                            errors.append(new_instance.errors)
                            print("HRIS Emp validate error: ", new_instance.errors)
                            for key in new_instance.errors.keys():
                                print(key, new_instance[key])
                    except ObjectDoesNotExist as obj_not_found:
                        try:
                            new_instance = EmployeeSerializer(data=data)
                            if new_instance.is_valid():
                                new_instance.save()
                                update_count += 1
                            else:
                                errors.append(new_instance.errors)
                                print("HRIS Emp validate error: ", new_instance.errors)
                                for key in new_instance.errors.keys():
                                    print(key, new_instance[key])
                        except Exception as ex:
                            print(ex)
                hris_payload["pageIndex"] += 1
                
            return response_data({
                "errors": errors,
                "create_count": create_count,
                "update_count": update_count
            })
        except Exception as e:
            print(e)
            return response_data(str(e), 4, "Internal server errors!")
     
      