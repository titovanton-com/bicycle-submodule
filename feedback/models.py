# coding: UTF-8

from django.db import models
from django.contrib.auth.models import User
from bicycle.core.models import PublishedModel
from bicycle.core.models import ChronologyModel


class FeedbackBase(ChronologyModel):
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Пользователь')
    name = models.CharField(max_length=120, verbose_name=u'Имя')
    contacts = models.TextField(verbose_name=u'Контакты')
    text = models.TextField(verbose_name=u'Сообщение')

    class Meta:
        verbose_name_plural = u'Обратная связь'
        abstract = True


class Feedback(FeedbackBase):
    pass
