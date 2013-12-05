# coding: UTF-8

from django.db import models
from django.contrib.auth.models import User


class FutureMessage(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    mtype = models.CharField(max_length=10)
    title = models.CharField(max_length=60)
    text = models.TextField()

