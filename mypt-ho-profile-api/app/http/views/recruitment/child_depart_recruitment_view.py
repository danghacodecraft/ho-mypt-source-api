from ....core.helpers.response import *
from ....core.helpers.global_variable import *
from ...serializers.hr_serializer import *
from rest_framework.viewsets import ViewSet

class ChildDepartRecruitmentView(ViewSet):
    def child_depart_recruitment(self, request):
        fname = "child_depart_recruitment"

        # lay tu input
        data_input = request.data
        branch = data_input.get('branch')
        try:
            queryset = Department.objects.filter(branch=branch)
            serializer = DepartmentSerializer(queryset, many=True, fields=['childDepart'])
            list_data = serializer.data
            if len(list_data) > 0:
                data_output = []
                for i in list_data:
                    child_depart = i.get('childDepart', '')
                    data_output.append(child_depart)
                return response_data(data=data_output, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)


            else:
                return response_data(data=[], message=MESSAGE_API_NO_DATA, status=STATUS_CODE_NO_DATA)


        except Exception as ex:
            print("{}-------------".format(fname))
            print(ex)
            return response_data(data={}, status=STATUS_CODE_ERROR_LOGIC, message=MESSAGE_API_FAILED)
