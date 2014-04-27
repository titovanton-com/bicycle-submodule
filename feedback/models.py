# coding: UTF-8

from django.db import models
from django.contrib.auth.models import User
from bicycle.core.models import PublishedMixin
from bicycle.core.models import ChronologyMixin


class FeedbackBase(PublishedMixin, ChronologyMixin):
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=u'Пользователь')
    name = models.CharField(max_length=120, verbose_name=u'Имя')
    email = models.EmailField(verbose_name=u'Почтовый адрес')
    text = models.TextField(verbose_name=u'Сообщение')

    class Meta:
        verbose_name_plural = u'Обратная связь'
        abstract = True


class Feedback(FeedbackBase):
    pass
