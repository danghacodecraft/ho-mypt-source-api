from django.db import models


# Create your models here.
class KpiInfo(models.Model):
    class Meta:
        db_table = 'mypt_job_kpi_info'

    id = models.IntegerField(primary_key=True, auto_created=True)
    kpi_type = models.CharField(max_length=50)
    kpi_value = models.TextField()
    title = models.CharField(max_length=50)
    description = models.TextField()
    year = models.IntegerField(10)
    target = models.FloatField()
    owner = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
