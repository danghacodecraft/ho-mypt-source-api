from django.db import models

# Create your models here.
class HoPermissionWithRoute(models.Model):
    class Meta:
        db_table = 'mypt_ho_auth_permission_with_route'

    link_id = models.IntegerField(primary_key=True)
    service_name = models.CharField(max_length=100)
    api_route = models.CharField(max_length=100)
    permission_codes = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
