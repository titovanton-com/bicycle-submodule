# coding: UTF-8

from django.db import models
from django.contrib.auth.models import User


class UserProfileBase(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=u'Пользователь',
                             related_name='user_profile')
    unique_email = models.EmailField(unique=True, verbose_name=u'Электронная почта')

    def __unicode__(self):
        return '%s' % self.user

    class Meta:
        abstract = True