from django.db import models


# Create your models here
class MyPTUserPermission(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.PositiveBigIntegerField(null=False)
    permission_id = models.PositiveIntegerField(null=False)
    permission_code = models.CharField(max_length=100, null=True)
    child_depart = models.CharField(max_length=5000, null=True)
    date_created = models.DateTimeField(null=False, auto_now_add=True)
    date_modified = models.DateTimeField(null=True, auto_now=True)
    updated_by = models.PositiveBigIntegerField(null=True, default=None)
    created_by = models.PositiveBigIntegerField(null=True, default=None)

    class Meta:
        db_table = 'mypt_auth_user_permission'
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'permission_id'], name='unique_userId_permissionId_combination_mypt_user_permission'
            )
        ]