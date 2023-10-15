from django.db import models


class Employee(models.Model):
    class Meta:
        db_table = 'employees_tb'

    email = models.CharField(max_length=255, primary_key=True)
    user_id = models.PositiveBigIntegerField(default=0)
    emp_code = models.CharField(max_length=8, null=True)
    emp_name = models.CharField(max_length=50, null=True)
    birthday = models.DateField(null=True)
    day = models.CharField(max_length=4, null=True)
    month = models.CharField(max_length=4, null=True)
    year = models.CharField(max_length=8, null=True)
    job_title = models.CharField(max_length=50, null=True)
    child_depart = models.CharField(max_length=30, null=True)
    mobile_phone = models.CharField(max_length=20, null=True)
    mstcn = models.CharField(max_length=50, default=None)
    dependent_info = models.CharField(max_length=50, null=True)
    contract_type = models.CharField(max_length=50, null=True)
    contract_begin = models.DateField(null=True)
    contract_end = models.DateField(null=True)
    account_number = models.CharField(max_length=30, null=True)
    type_salary = models.CharField(max_length=50, null=True)
    sex = models.CharField(max_length=10, null=True)
    status_working = models.IntegerField(null=True)
    cmnd = models.CharField(max_length=30, null=True)
    date_join_company = models.DateField(null=True)
    date_quit_job = models.DateField(null=True)
    update_time = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=45, null=True)
    avatar_img = models.CharField(max_length=200, null=True)
    id_user = models.CharField(max_length=50, null=True)
