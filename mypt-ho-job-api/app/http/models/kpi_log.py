from django.db import models


# Create your models here.
class KpiLog(models.Model):
    class Meta:
        db_table = 'mypt_job_log_api'

    id = models.IntegerField(primary_key=True, auto_created=True)
    api_input = models.TextField()
    url = models.CharField(max_length=255)
    api_output = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=255)
    interval_process = models.FloatField()
