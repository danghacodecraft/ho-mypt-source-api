from django.db import models

class EmployeeCertificate(models.Model):
    class Meta:
        db_table = "mypt_profile_employee_certificates"

    id = models.AutoField(primary_key=True)
    inside_id = models.IntegerField(null=False, blank=False, default=None)
    email = models.CharField(max_length=255, blank=False, null=False)
    emp_code = models.CharField(max_length=10, blank=False, null=False)
    skill_name = models.TextField(blank=True, null=True, default=None)
    training_organization = models.TextField(blank=True, null=True, default=None)
    note = models.TextField(blank=True, null=True, default=None)
    rate = models.CharField(max_length=100, null=True, blank=True, default=None)
    issued_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)
