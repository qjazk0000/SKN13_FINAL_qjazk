# auth_app/models.py
from django.db import models
import uuid

class UserInfo(models.Model):
    user_id = models.UUIDField(primary_key=True)

    class Meta:
        db_table = 'user_info'
        managed = False
