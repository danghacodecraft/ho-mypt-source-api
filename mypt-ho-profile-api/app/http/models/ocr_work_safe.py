
from django.db import models
from app.core.helpers.global_variable import *


class OcrWorkSafe(models.Model):
    class Meta:
        db_table = "mypt_ho_profile_ocr_work_safe"

    atld_id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=30)
    nhom_dao_tao = models.CharField(max_length=100)
    cap_the_chung_chi = models.CharField(max_length=100)
    ngay_cap_the_ATLD = models.DateField()
    ngay_het_han_ATLD = models.DateField()
    ngay_bat_dau_dao_tao = models.DateField()
    ngay_ket_thuc_dao_tao = models.DateField()
    tinh_trang_the_chung_chi = models.CharField(max_length=100)
    hinh_anh_the_chung_nhan = models.CharField(max_length=500)
    update_time_atld = models.DateTimeField()
    update_by = models.CharField(max_length=50)
    active = models.IntegerField()
    number_card = models.CharField(max_length=500)
    created_time = models.DateTimeField()
    created_by = models.CharField(max_length=255)
    confirm = models.IntegerField()
    status_file = models.IntegerField()
    job_title = models.CharField(max_length=255)


