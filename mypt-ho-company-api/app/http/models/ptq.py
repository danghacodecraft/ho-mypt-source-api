from django.db.models import *
from django.db import models

from ...core.helpers.helper import *
from ...configs.service_api_config import *
from django.conf import settings as project_settings

class Tools(Model):
	class Meta:
			db_table='SCM_tb'
	SCM_id = AutoField(primary_key=True)
	email = CharField(max_length=200)
	stock_name = CharField(max_length=200)
	item_code =CharField(max_length=100)
	item_name = CharField(max_length=200)
	unit_name =CharField(max_length=100)
	size_name =CharField(max_length=100)
	quantity_now = IntegerField()
	quantity_hold = IntegerField()
	start_date = DateField()
	expire_date = DateField()
	zone_name = CharField(max_length=200)
	DateofControl = CharField(max_length=100)
	CommentCDCD = CharField(max_length=500)
	update_by = CharField(max_length=45)
	update_time = DateTimeField()
	usage_status = IntegerField()
	tinh_trang = IntegerField()
	id_history = CharField(max_length=5000)
	id_repair = CharField(max_length=5000)
	t_check = DateField()
 
	def get_name_code(self):	
		try:
			if self.email:
				app_env = "base_http_" + project_settings.APP_ENVIRONMENT
				response = call_api(
					host = SERVICE_CONFIG['profile-api'][app_env],
					func = SERVICE_CONFIG['profile-api']['info_from_email']['func'],
					method = SERVICE_CONFIG['profile-api']['info_from_email']['method'],
					data = {"email":[self.email], "fields":["code","name"]}
				)
				dataApi = json.loads(response)
				if dataApi["statusCode"] != 1:
					return [dataApi["message"]]
				dataApi = dataApi['data'][0]
				return dataApi
		except:
			return None

	def get_name(self):
		try:
			dataApi = self.get_name_code()
			if dataApi:
				return dataApi["name"]
			return None
		except:
			return None

	def get_code(self):
		try:
			dataApi = self.get_name_code()
			if dataApi:
				return dataApi["code"]
			return None
		except:
			return None

class Ptq(models.Model):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.type_ptq = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id','description')
    class Meta:
        db_table = 'mypt_company_control'
    id = models.AutoField(primary_key=True) # 
    region = models.CharField(max_length=50)
    partner = models.CharField(max_length=50)
    block_name = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=50)
    contract = models.CharField(max_length=50)
    error_type = models.CharField(max_length=50)
    date_complete = models.DateTimeField()
    error_main = models.CharField(max_length=50)
    error_group = models.CharField(max_length=50)
    error_description = models.CharField(max_length=50)
    error_detail = models.CharField(max_length=50)
    punishment = models.IntegerField()
    account_mbn = models.CharField(max_length=50)
    date_check = models.DateField()
    email = models.CharField(max_length=50)
    error_number = models.IntegerField()
    deadline = models.DateField()
    recorded = models.IntegerField(max_length=50, default="2")
    note = models.TextField()
    thematic = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    
    def get_type(self):
        try:
            if self.recorded:
                return self.type_ptq.get(id=self.recorded)["description"]
        except:
            return ""
        
    def explanation(self):
        try:
            explanation = PtqHistory.objects.filter(ptq_id=self.id).values("ptq_id").annotate(total=Max('times'))
            times = explanation[0]["total"]
            return PtqHistory.objects.filter(ptq_id=self.id, times=times).values_list("content", flat=True)[0]
        except:
            return ""

class OldPtq(models.Model):
    class Meta:
        db_table = 'ptq_tb'

    ptq_id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=50)
    partner = models.CharField(max_length=50)
    block_name = models.CharField(max_length=50)
    emp_name = models.CharField(max_length=50)
    MBN_account_name = models.CharField(max_length=50)
    emp_code = models.CharField(max_length=50)
    contract = models.CharField(max_length=20)
    error_type = models.CharField(max_length=100)
    date_complete = models.DateTimeField()
    date_check = models.DateField()
    duration_check = models.CharField(max_length=50)
    month_check = models.CharField(max_length=2)
    year_check = models.CharField(max_length=4)

    error_main = models.CharField(max_length=100)
    error_group = models.CharField(max_length=100)
    error_description = models.CharField(max_length=500)
    error_detail = models.CharField(max_length=500)
    punishment = models.CharField(max_length=50)
    error_number = models.IntegerField()
    deadline = models.DateField()
    explanation = models.CharField(max_length=10000)
    recorded = models.CharField(max_length=50)
    note = models.CharField(max_length=5000)
    uuid = models.CharField(max_length=50)
    update_time = models.DateTimeField()
    update_by = models.CharField(max_length=50)
    thematic = models.CharField(max_length=5000)

    moved = models.IntegerField()
    
class PtqHistory(models.Model):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.type_ptq = PtqType.objects.filter(type__isnull=False, deleted_at__isnull=True).values('id','description')
    class Meta:
        db_table = 'mypt_company_control_history'
    id = models.AutoField(primary_key=True) # 
    image = models.TextField()
    content = models.TextField()
    ptq_id = models.IntegerField()
    times = models.IntegerField()
    feedback = models.TextField()
    status = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    
    def get_type(self):
        try:
            if self.status:
                return self.type_ptq.get(id=self.status)["description"]
        except:
            return ""
    
    def list_img(self):
        if self.image:
            list_image = list(self.image.split(";"))
            try:
                list_image.remove("")
                return list_image
            except:
                return list_image
        return []
    
class PtqType(models.Model):
    class Meta:
        db_table = 'mypt_company_control_type'
    id = models.AutoField(primary_key=True) # 
    type = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()
    
class DeleteReasonPtq(models.Model):
    class Meta:
        db_table = 'mypt_company_delete_control_reason'
    id = models.AutoField(primary_key=True)
    reason = models.TextField()
    key_reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField()