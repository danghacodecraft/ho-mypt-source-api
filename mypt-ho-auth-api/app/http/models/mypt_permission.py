from django.db import models


# Create your models here.
class MyPTPermission(models.Model):
    class Meta:
        db_table = 'mypt_auth_permission'

    permission_id = models.AutoField(primary_key=True)
    permission_name = models.CharField(max_length=255, null=False)
    permission_code = models.CharField(max_length=100, unique=True, null=False)
    permission_group_id = models.IntegerField(null=False)
    has_depart_right = models.IntegerField(null=False, default=1)
    date_deleted = models.DateTimeField(null=True, default=None)
    date_created = models.DateTimeField(null=False, auto_now_add=True)
    date_modified = models.DateTimeField(null=False, auto_now=True)
    is_deleted = models.IntegerField(null=False, default=0)
    updated_by = models.IntegerField(null=True, default=None)
    created_by = models.IntegerField(null=True, default=None)
