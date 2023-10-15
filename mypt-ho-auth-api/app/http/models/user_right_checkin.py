from django.db import models


# Create your models here.
class UserRightCheckin(models.Model):
    class Meta:
        db_table = 'user_right_checkin_tb'

    email = models.CharField(primary_key=True, max_length=50)
    per_id = models.CharField(max_length=200, null=True, default=None)
    team_name = models.CharField(max_length=100, null=True, default=None)
    child_depart_right = models.CharField(max_length=1000, null=True, default=None)
    super_admin = models.CharField(max_length=100, null=True, default=None)




