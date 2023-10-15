from django.db import models


# Create your models here.
class FeaturesRoles(models.Model):
    class Meta:
        db_table = 'mypt_profile_features_roles'

    role_id = models.AutoField(primary_key=True)
    role_title = models.CharField(max_length=255)
    role_code = models.CharField(max_length=100)
    feature_code = models.CharField(max_length=100)
    platform = models.CharField(max_length=5)
    date_created = models.DateTimeField(auto_created=True)
    date_modified = models.DateTimeField(auto_now_add=True)
