from django.db import models


# Create your models here.
class Kpi(models.Model):
    class Meta:
        db_table = 'mypt_job_kpi_contract'

    id = models.IntegerField(primary_key=True, auto_created=True)
    emp_code = models.CharField(max_length=255)
    account_mbn = models.CharField(max_length=255)
    contract = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    kpi_type = models.CharField(max_length=255)
    time_complete = models.CharField(max_length=255)
    time_start_cl1 = models.CharField(max_length=255)
    time_complete_cl1 = models.CharField(max_length=255)
    time_start_cl2 = models.CharField(max_length=255)
    time_complete_ptc = models.CharField(max_length=255)
    kpi_date = models.DateField()
    created_date = models.DateTimeField(auto_now=True)
