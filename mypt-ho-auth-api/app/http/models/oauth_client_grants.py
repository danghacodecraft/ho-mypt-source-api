from django.db import models

# Create your models here.
class OauthClientGrants(models.Model):
    class Meta:
        db_table = 'mypt_auth_oauth_client_grants'

    id = models.AutoField(primary_key=True)
    client_id = models.CharField(max_length=50)
    grant_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)
