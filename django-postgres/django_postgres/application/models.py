from django.db import models
from uuid import uuid4


class User(models.Model):
    id = models.UUIDField(verbose_name="User ID", auto_created=True, primary_key=True, default=uuid4)
    name = models.CharField(verbose_name='User Name', max_length=50, blank=False, null=False)
    email = models.EmailField(verbose_name='User Email', blank=False, null=False)
    password = models.CharField(verbose_name='Password', max_length=50, blank=False, null=False)
    website = models.CharField(verbose_name="User Website", max_length=50)

    def __str__(self):
        return self.name
