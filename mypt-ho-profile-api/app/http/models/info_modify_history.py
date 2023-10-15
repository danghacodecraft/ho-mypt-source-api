from django.db import models

class InformationModifyHistory(models.Model):
    class Meta:
        db_table = 'mypt_profile_employee_information_modify_history'

    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=50, null=False, blank=False)
    emp_code = models.CharField(max_length=15, null=False, blank=False)
    old_value = models.CharField(max_length=1000, null=True, blank=True, default=None)
    new_value = models.CharField(max_length=1000, null=True, blank=True, default=None)
    key_semantic = models.CharField(max_length=1000, null=True, blank=True, default=None)
    key_name = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)