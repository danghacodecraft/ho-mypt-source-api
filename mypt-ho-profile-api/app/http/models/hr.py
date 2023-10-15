from django.db import models
from app.core.helpers.utils import *


class DepartmentFilter(models.Model):
    class Meta:
        db_table = 'department_filter_tb'

    child_depart = models.CharField(max_length=30, primary_key=True)
    branch = models.CharField(max_length=30)
    chi_nhanh = models.CharField(max_length=30)
    parent_depart = models.CharField(max_length=30)
    child_depart1 = models.CharField(max_length=30)
    dien_giai = models.CharField(max_length=3000)
    code_child_depart = models.CharField(max_length=1000)
    order = models.IntegerField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField()

    def __str__(self):
        return self.child_depart


class Department(models.Model):
    class Meta:
        db_table = 'department_tb'

    child_depart = models.CharField(max_length=30, primary_key=True)
    branch = models.CharField(max_length=30)
    chi_nhanh = models.CharField(max_length=30)
    parent_depart = models.CharField(max_length=30)
    child_depart1 = models.CharField(max_length=30, null=True)
    dien_giai = models.CharField(max_length=3000, null=True)
    code_child_depart = models.CharField(max_length=1000, null=True)
    order = models.IntegerField()

    name_child_depart = models.CharField(max_length=100, null=True)
    email_manager = models.CharField(max_length=100, null=True)
    email_deputy_other = models.CharField(max_length=500, null=True)
    email_admin = models.CharField(max_length=500, null=True)
    tinh_tp = models.CharField(max_length=100, null=True)
    doi_tac = models.CharField(max_length=45, null=True)
    loop_mail_kt = models.CharField(max_length=50, null=True)

    tech_manager_email = models.CharField(max_length=255)
    level_department = models.IntegerField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_last_updated = models.DateTimeField()

    def __str__(self):
        return self.child_depart

    def emp_info(self):
        try:
            if self.child_depart:
                queryset = Employee.objects.filter(child_depart=self.child_depart)
                return queryset
            return None
        except:
            return None

    # def emp_info(self):
    #     if self.child_depart:
    #         try:
    #             queryset = Employee.objects.filter(child_depart=self.child_depart)
    #             return queryset
    #         except:
    #             return None
    #     return None


class Employee(models.Model):
    class Meta:
        db_table = 'employees_tb'

    email = models.CharField(max_length=50, primary_key=True, verbose_name="Email") # Email TINPNC
    emp_code = models.CharField(max_length=8, verbose_name="Mã nhân viên") # MNV
    emp_name = models.CharField(max_length=45, verbose_name="Họ tên") # Ho va ten
    birthday = models.DateField(null=None, default=None, verbose_name="Ngày sinh") # Ngay sinh
    day = models.CharField(max_length=4)
    month = models.CharField(max_length=4)
    year = models.CharField(max_length=4)
    job_title = models.CharField(max_length=50, blank=True, null=True, verbose_name="Vị trí chuyên môn") # Chuyên môn
    job_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mã chức danh") # Ma chuc danh
    child_depart = models.CharField(max_length=30, verbose_name="Phòng ban", blank=True, null=True) # organizationCodePath
    mobile_phone = models.CharField(max_length=20, verbose_name="SĐT di động", blank=True, null=True) # dien thoai
    mstcn = models.CharField(max_length=50, verbose_name="Mã số thuế cá nhân", blank=True, null=True) # ma so thue ca nhan
    tax_identification_place = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nơi cấp mã số thuế")  # noi cap mst
    tax_identification_date = models.DateField(null=True, default=None, verbose_name="Ngày cấp mã số thuế")  # ngay cap mst
    dependent_info = models.CharField(max_length=50, blank=True, null=True)
    contract_code = models.CharField(max_length=30, blank=True, null=True, default=None, verbose_name="Mã hợp đồng") #Số hợp đồng
    contract_begin = models.DateField(null=True, default=None, verbose_name="Ngày bắt đầu hợp đồng") #Ngày bắt đầu hợp đồng
    contract_end = models.DateField(null=True, default=None, verbose_name="Ngày kết thúc hợp đồng") # Ngày kết thúc hợp đồng
    contract_type = models.CharField(max_length=1000, null=True, blank=True, default=None, verbose_name="Loại hợp đồng") # Loại hợp đồng
    contract_type_code = models.CharField(max_length=1000, null=True, blank=True, default=None) # Mã loại hợp đồng
    account_number = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="STK ngân hàng") # so tai khoan ngan hang
    type_salary = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=10, verbose_name="Giới tính", blank=True, null=True) # gioi tinh
    status_working = models.IntegerField(default=1, verbose_name="Trạng thái làm việc", blank=True, null=True) # Trạng thái làm việc
    cmnd = models.CharField(max_length=30, blank=True, null=True, default=None, verbose_name="CMND/CCCD") #cccd/cmnd
    ngay_cap_cmnd = models.DateField(null=True, default=None, verbose_name="Ngày cấp CMND/CCCD") # Ngày cấp cmnd/cccd
    noi_cap_cmnd = models.TextField(blank=True, null=True, default=None, verbose_name="Nơi cấp CMND/CCCD") # Nơi cấp cmnd/cccd
    date_join_company = models.DateField(null=True, default=None, verbose_name="Ngày vào công ty") #Ngày vào công ty
    date_quit_job = models.DateField(null=True, default=None, verbose_name="Ngày nghỉ việc") #Ngày nghỉ việc
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=45, blank=True, null=True)
    avatar_img = models.CharField(max_length=200, blank=True, null=True)
    id_user = models.CharField(max_length=50, blank=True, null=True)

    place_of_birth = models.CharField(max_length=200, blank=True, null=True, default=None, verbose_name="Nơi sinh") # Noi sinh
    nationality = models.CharField(max_length=45, blank=True, null=True, verbose_name="Quốc tịch") #Quốc tịch
    place_of_permanent = models.TextField(blank=True, null=True, default=None, verbose_name="Địa chỉ thường trú") # dia chi
    marital_status = models.IntegerField(blank=True, null=True, verbose_name="Tình trạng hôn nhân") #Tình trạng hôn nhân
    degree = models.TextField(blank=True, null=True, default=None, verbose_name="Trình độ") # trinh do
    workplace = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nơi làm việc") #Nơi làm việc
    level = models.CharField(max_length=45, blank=True, null=True, verbose_name="Cấp cán bộ") #Level cán bộ
    health_insurance = models.CharField(max_length=30, blank=True, null=True, verbose_name="Số thẻ BHYT") # so the BHYT
    social_insurance = models.CharField(max_length=30, blank=True, null=True, verbose_name="Số BHXH")
    social_insurance_salary_pay = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lương đóng BHXH") # Lương đóng BHXH
    place_to_join_social_insurance = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="Nơi tham gia BHXH")
    bank_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tên ngân hàng") # Tên ngân hàng

    foxpay = models.CharField(max_length=50, blank=True, null=True, default=None, verbose_name="STK Foxpay") # Số ví Foxpay


    # New: 2023/05/31
    plurality = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="Kiêm nhiệm") # kiem nhiem
    officer_title = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="Chức vụ") # chuc vu
    officer_code = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="Mã chức vụ") # ma chuc vu
    id_phone = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name="ID Phone") # ip phone
    comment = models.TextField(blank=True, null=True, default=None, verbose_name="Ghi chú") # ghi chu

    created_at =  models.DateTimeField()


class EmployeeRank(models.Model):
    class Meta:
        db_table = 'mypt_profile_employee_rank_pnc_tb'

    id = models.AutoField(primary_key=True)
    emp_code = models.CharField(max_length=20)
    emp_name = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    thang = models.IntegerField()
    nam = models.IntegerField()
    emp_rank_info = models.CharField(max_length=10000)
    bac_nghe = models.FloatField()
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=50)
    parent_depart = models.CharField(max_length=45)
    child_depart = models.CharField(max_length=45)


class SafeCard(models.Model):
    class Meta:
        db_table = "tool_ATLD_tb"

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
    job_title = models.CharField(max_length=255)
    
    child_depart = models.CharField(max_length=30)
    emp_name = models.CharField(max_length=255)
    date_join_company = models.DateField()
    sex = models.CharField(max_length=10)
    birthday = models.DateField()
    cmnd = models.CharField(max_length=30)
    date_quit_job = models.DateField(max_length=50)
    parent_depart = models.CharField(max_length=50)
    agency = models.CharField(max_length=50)

    def emp_info(self):
        if self.emp_code:
            try:
                queryset = Employee.objects.get(emp_code=self.emp_code)
                return queryset
            except:
                return None
        return None

    def department(self):
        if self.emp_code:
            try:
                queryset = Employee.objects.filter(emp_code=self.emp_code).values_list("child_depart", flat=True)
                deparment = Department.objects.get(child_depart=queryset[0])
                return deparment
            except:
                return None
        return None

    def get_list_hinh_anh_the_chung_nhan(self):
        if not is_null_or_empty(self.hinh_anh_the_chung_nhan):
            str_list_img = self.hinh_anh_the_chung_nhan
            list_img = eval(str_list_img)
            return list_img
        else:
            return []


class TypeGroupTrainingWorkSafe(models.Model):
    class Meta:
        db_table = "mypt_ho_profile_type_group_train_work_safe"

    id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=455)
    train_group = models.CharField(max_length=45)
    type_card = models.CharField(max_length=455)


class HistoriesDeleteCard(models.Model):
    class Meta:
        db_table = "mypt_ho_profile_histories_delete_work_safe_card"

    id = models.AutoField(primary_key=True)
    card_id = models.IntegerField()
    update_at = models.DateTimeField()
    update_by = models.CharField(max_length=255)
    info_card = models.TextField()

