from django.db import models

# Create your models here.
class OauthGrants(models.Model):
    class Meta:
        db_table = 'mypt_auth_oauth_grants'

    id = models.AutoField(primary_key=True)
    grant = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, default=None)

    def findGrantIdByGrantType(self, grantType):
        grants = {
            "authorization_code": 1,
            "implicit_grant": 2,
            "user_password_credentials_grant": 3,
            "client_credentials_grant": 4,
            "refresh_token": 5,
            "fpt_adfs": 9,
            "account_credentials_grant": 10
        }
        if grants.get(grantType, None) is not None:
            print("tim duoc grant id tu grant type : " + grantType)
            return int(grants.get(grantType))
        else:
            return 0
