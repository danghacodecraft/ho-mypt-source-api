from django.db import models


# Create your models here.
class UserProfile(models.Model):
    class Meta:
        db_table = 'mypt_profile_user_profile'

    profile_id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    email = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    avatar_img = models.CharField(max_length=255)
    birthday = models.DateField()
    sex = models.CharField(max_length=10)
    mobile_phone = models.CharField(max_length=20)
    place_of_birth = models.CharField(max_length=200, blank=True, null=True)
    nationality = models.CharField(max_length=45, blank=True, null=True)
    marital_status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
