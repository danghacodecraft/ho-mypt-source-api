from django.db import models


# Create your models here.
class MapDepartment(models.Model):
    class Meta:
        db_table = 'mypt_ho_profile_map_department'

    # agency ung voi cot chi_nhanh trong bang department
    id = models.BigAutoField(primary_key=True, auto_created=True)
    agency = models.CharField(max_length=50)
    agency_inside = models.CharField(max_length=50)
    parent_depart = models.CharField(max_length=50)
    parent_depart_old = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    technical_manager = models.CharField(max_length=255)
    city = models.TextField()
    lat = models.TextField()
    lng = models.TextField()
    au= models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True,null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=False)