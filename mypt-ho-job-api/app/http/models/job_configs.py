from django.db import models


# Create your models here.
class JobConfigs(models.Model):
    class Meta:
        db_table = 'mypt_job_configs'

    config_id = models.IntegerField(primary_key=True)
    config_type = models.CharField(max_length=45)
    config_key = models.CharField(max_length=100)
    config_value = models.TextField()
    config_description_vi = models.TextField()
    config_description_en = models.TextField()
    config_status = models.CharField(max_length=45)
    owner = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField(auto_now=False)
    note = models.CharField(max_length=255)
