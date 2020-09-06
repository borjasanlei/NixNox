from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class CustomUser(AbstractUser):
    pass


class Photometer(models.Model):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    serial_id = models.SlugField(unique=True, max_length=10)
    
    def __str__(self):
        return f'Photometer {self.serial_id}'


class Institution(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    name = models.CharField(max_length=250, default='Amateur', unique = True)

    def __str__(self):
        return f'{self.name}'