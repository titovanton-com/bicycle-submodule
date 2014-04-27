# coding: UTF-8

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from bicycle.core.utilites import md5_random_string
from bicycle.core.shortcuts import send_email_rq


class UserProfileBase(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name=u'Пользователь',
                             related_name='user_profile')
    unique_email = models.EmailField(unique=True, verbose_name=u'Электронная почта')

    def __unicode__(self):
        return '%s' % self.user

    class Meta:
        abstract = True
        verbose_name_plural = u'Профили пользователей'


class InvitationBase(models.Model):
    STATUS_CHOICES = (
        (u'new', u'Новый'),
        (u'invitation has been sent', u'Приглашение выслано'),
        (u'has followed the link', u'Перешел по ссылке'),
        (u'signed up', u'Зарегистрировался'),
    )

    unique_email = models.EmailField(unique=True, verbose_name=u'Электронная почта')
    code = models.TextField(max_length=32, verbose_name=u'Код')
    status = models.CharField(max_length=120, choices=STATUS_CHOICES,
                              verbose_name=u'Статус', default=STATUS_CHOICES[0][0])

    def save(self):
        if not self.code:
            self.code = md5_random_string()
        super(InvitationBase, self).save()

    def send_email_setup(self, request):
        setup = {
            'mail_template': u'accounts/invitation_mail.html',
            'from_email': u'no-replay@example.com',
            'subject': u'Приглашение зарегистрироваться',
        }
        cntxt = {
            'STATIC_URL': settings.STATIC_URL,
            'HTTP_HOST': request.META['HTTP_HOST'],
            'SUBJECT': setup['subject'],
            'CODE': self.code,
            'EMAIL': self.unique_email,
        }
        return cntxt, setup

    def send_email(self, request):
        cntxt, setup = self.send_email_setup(request)
        send_email_rq(setup['subject'], setup['from_email'], (self.unique_email,),
                      setup['mail_template'], cntxt)
        self.status = self.STATUS_CHOICES[1][0]
        self.save()

    def __unicode__(self):
        return '%s' % self.unique_email

    class Meta:
        abstract = True
        verbose_name_plural = u'Приглашения для регистрации'
