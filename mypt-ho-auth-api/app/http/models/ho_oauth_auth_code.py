from django.db import models

# Create your models here.
class HoOauthAuthCode(models.Model):
    class Meta:
        db_table = 'mypt_ho_auth_oauth_auth_codes'

    id = models.CharField(max_length=50, primary_key=True)
    user_id = models.IntegerField()
    client_id = models.CharField(max_length=20)
    state = models.CharField(max_length=50)
    code_challenge = models.CharField(max_length=128)
    code_verifier = models.CharField(max_length=128)
    device_id = models.CharField(max_length=255)
    grant_id = models.IntegerField()
    data_grant = models.TextField()
    revoked = models.IntegerField()
    expires_at = models.DateTimeField(null=True, default=None)
    status = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)
