from django.db import models

# Create your models here.
class FeaturesRolesEmails(models.Model):
    class Meta:
        db_table = 'mypt_profile_features_roles_emails'

    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    role_id = models.IntegerField(null=False)
    role_code = models.CharField(max_length=100)
    feature_code = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_created=True, auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
