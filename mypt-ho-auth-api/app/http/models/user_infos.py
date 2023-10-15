from django.db import models

# Create your models here.
class UserInfos(models.Model):
    class Meta:
        db_table = 'mypt_auth_user_infos'

    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    device_token = models.CharField(max_length=255)
    device_platform = models.CharField(max_length=100)
    device_info = models.CharField(max_length=1000)
    date_login = models.DateTimeField(null=True, default=None)
    ho_date_login = models.DateTimeField(null=True, default=None)
    date_latest_refresh_token = models.DateTimeField(null=True, default=None)
    ho_date_latest_refresh_token = models.DateTimeField(null=True, default=None)
    app_version = models.CharField(max_length=50)
    app_language = models.CharField(max_length=5, default="vi")
    notification_gateway_id = models.IntegerField()
    unread_notify = models.IntegerField(default=1)
    notification_id_updated_at = models.DateTimeField(null=True, default=None)
    configs = models.TextField()
    is_deleted = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(null=True, default=None)
