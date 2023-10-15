from django.db import models

class EmployeeQualification(models.Model):
    class Meta:
        db_table = "mypt_profile_employee_qualifications"

    id = models.AutoField(primary_key=True)
    inside_id = models.IntegerField(null=False, blank=False, default=None)
    email = models.CharField(max_length=255, blank=False, null=False)
    emp_code = models.CharField(max_length=10, blank=False, null=False)
    organization_name = models.TextField(blank=True, null=True, default=None)
    field_of_study = models.TextField(blank=True, null=True, default=None)
    type_of_training = models.CharField(max_length=255, blank=True, null=True, default=None)
    graduated_year = models.IntegerField(null=False, blank=False)
    ranked_academic = models.CharField(max_length=100, null=True, blank=False, default=None)
    note = models.TextField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)
