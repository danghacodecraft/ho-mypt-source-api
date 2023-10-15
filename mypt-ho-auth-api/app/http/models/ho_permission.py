from django.db import models

# Create your models here.
class HoPermission(models.Model):
    class Meta:
            db_table = 'mypt_ho_auth_permission'

    permission_id = models.IntegerField(primary_key=True)
    permission_name = models.CharField(max_length=255)
    permission_code = models.CharField(max_length=100)
    permission_group_id = models.IntegerField()
    has_depart_right = models.IntegerField()
    date_deleted = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField()
    updated_by = models.IntegerField()
    created_by = models.IntegerField()
