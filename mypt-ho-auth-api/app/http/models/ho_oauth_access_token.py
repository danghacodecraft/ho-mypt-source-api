from django.db import models

# Create your models here.
class HoOauthAccessToken(models.Model):
    class Meta:
        db_table = 'mypt_ho_auth_oauth_access_tokens'

    id = models.CharField(max_length=50, primary_key=True)
    user_id = models.IntegerField()
    client_id = models.CharField(max_length=50)
    code_verifier = models.CharField(max_length=128)
    auth_code_id = models.CharField(max_length=50)
    biometry_token_id = models.CharField(max_length=100)
    refresh_token_id = models.CharField(max_length=50)
    grant_id = models.IntegerField()
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    device_token = models.CharField(max_length=255)
    device_platform = models.CharField(max_length=50)
    revoked = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
