from django.db import models


class Department(models.Model):
    class Meta:
        db_table = 'department_tb'

    child_depart = models.CharField(max_length=30, primary_key=True)
    branch = models.CharField(max_length=30, null=True, default=None)
    parent_depart = models.CharField(max_length=30, null=True, default=None)
    child_depart1 = models.CharField(max_length=30, null=True, default=None)
    dien_giai = models.CharField(max_length=3000, null=True, default=None)
    code_child_depart = models.CharField(max_length=1000, null=True, default=None)

