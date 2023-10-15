from django.db import models


# Create your models here.
class EmailsPrepareAddPersFeaRoles(models.Model):
    class Meta:
        db_table = 'emails_prepare_add_permissions_and_fea_roles'

    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, null=False)
    child_depart = models.CharField(max_length=50, null=True)
    is_processed = models.IntegerField(null=False, default=0)
    date_created = models.DateTimeField(null=False, auto_now_add=True)
    date_modified = models.DateTimeField(null=False, auto_now=True)
