from django.db import models

class APILog(models.Model):
    class Meta:
        db_table = 'mypt_profile_api_log'
        
    id = models.AutoField(primary_key=True)
    url = models.TextField(blank=False, null=False)
    method = models.CharField(max_length=10, blank=False, null=False)
    data = models.JSONField(null=True, default=None)
    params = models.JSONField(null=True, default=None)
    headers = models.JSONField(null=True, default=None)
    # result = models.TextField(null=True, default=None)
    result = models.JSONField(null=True, blank=True, default=None)
    called_at = models.DateTimeField(auto_now_add=True)
