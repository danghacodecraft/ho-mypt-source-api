from django.db import models


# Create your models here.
class StorageUuidLink(models.Model):
    class Meta:
        db_table = 'storage_uuid_data_tb'

    uuid = models.CharField(max_length=50, primary_key=True)
    link_data = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=45, null=True)
    update_time = models.DateTimeField(auto_now_add=True, null=True)
    link_local = models.CharField(max_length=200, null=True)
    folder = models.CharField(max_length=45, null=True)
    child_folder = models.CharField(max_length=45, null=True)
