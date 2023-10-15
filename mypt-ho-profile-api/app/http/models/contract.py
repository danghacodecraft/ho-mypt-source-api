from django.db import models


class ContractType(models.Model):
    class Meta:
        db_table = 'mypt_profile_contract_type'
    id = models.AutoField(primary_key=True)
    contract_type = models.CharField(max_length=255)


class Contract(models.Model):
    class Meta:
        db_table = 'mypt_profile_contract'
    contract_id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=8)
    contract_code = models.CharField(max_length=45)
    contract_type = models.CharField(max_length=255)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField()
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=50)
