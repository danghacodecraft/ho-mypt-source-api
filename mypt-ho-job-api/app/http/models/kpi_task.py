from django.db import models


# Create your models here.
class KpiTask(models.Model):
    class Meta:
        db_table = 'mypt_job_kpi'

    id = models.IntegerField(primary_key=True, auto_created=True)
    emp_code = models.CharField(max_length=255)
    account_mbn = models.CharField(max_length=255)
    ontime_tk = models.IntegerField()
    late_tk = models.IntegerField()
    ontime_bt = models.IntegerField()
    late_bt = models.IntegerField()
    count_cl2 = models.IntegerField()
    count_cl3 = models.IntegerField()
    count_cl7n_bt = models.IntegerField()
    count_cl7n_tk = models.IntegerField()
    count_shift_complete_sla_tk = models.IntegerField()
    count_shift_sla_tk = models.IntegerField()
    count_shift_complete_sla_bt = models.IntegerField()
    count_shift_sla_bt = models.IntegerField(null=True)
    customer_cl = models.IntegerField()
    kpi_date = models.DateField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=False)
