from ..models.kpi_task import *
from rest_framework.serializers import ModelSerializer

class KpiTaskSerializer(ModelSerializer):
    class Meta:
        model = KpiTask
        fields = ['emp_code',
                  'account_mbn',
                  'ontime_tk',
                  'late_tk',
                  'ontime_bt',
                  'late_bt',
                  'count_cl2',
                  'count_cl3',
                  'count_cl7n_bt',
                  'count_cl7n_tk',
                  'count_shift_complete_sla_tk',
                  'count_shift_sla_tk',
                  'count_shift_complete_sla_bt',
                  'count_shift_sla_bt',
                  'customer_cl',
                  'kpi_date']
