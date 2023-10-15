from django.db import models


class ProfileConfig(models.Model):
    class Meta:
        db_table = 'mypt_profile_config'

    config_id = models.AutoField(primary_key=True)
    config_key = models.CharField(max_length=100)
    config_value = models.TextField()
    created_at = models.DateTimeField()
    last_modified_at = models.DateTimeField()

    def __str__(self):
        return self.config_key
