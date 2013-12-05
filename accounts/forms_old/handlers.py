# coding: UTF-8

import re

from django.shortcuts import redirect
from django.contrib import auth
from django.db import connection
from django.db import IntegrityError
from bicycle.futuremessage.message import Message
from bicycle.futuremessage.models import FutureMessage
from bicycle.accounts.messages import PASSWORD_FAILED
from bicycle.accounts.messages import PROFILE_SAVED
from bicycle.accounts.messages import REGISTER_INTEGRITY_ERROR
from bicycle.accounts.messages import PROFILE_FORM_FAILD
from bicycle.accounts.messages import PASSWORD_SAVED
from bicycle.accounts.messages import PASSWORD_CONFIRM_FAILD
from bicycle.accounts import accounts

from forms import UserForm
from forms import PasswordForm
from forms import ChangePasswordForm


def profile_change_handler(request):
    """
    Profile GET and POST forms handler.

    Return dict of forms and error if there are.
    If POST was successfull, then handler will return redirect 
    to the /accounts/user-room/#profile-nofollow.
    GET result example:
    forms = {
        'user_form': UserForm(initial=user_initial),
        'profile_form': accounts.Forms.profile(instance=request.user.get_profile()),
        'password_form': PasswordForm(),
        'error': False
    }
    """
    if not request.user.is_authenticated():
        return redirect('/')
    if request.method == 'POST' and request.POST.get('profile_form', False):
        user_form = UserForm(data=request.POST)
        profile_form = accounts.Forms.profile(data=request.POST, instance=request.user.get_profile())
        password_form = PasswordForm(data=request.POST)
        forms = {
            'user_form': user_form,
            'profile_form': profile_form,
            'password_form': password_form,
            'error': False
        }
        if not password_form.is_valid() or\
           not request.user.check_password(password_form.cleaned_data['password']):
            forms['error'] = True
            request.alert_messages += [Message('error', PASSWORD_FAILED)]
            return forms
        if user_form.is_valid() and profile_form.is_valid():
            try:
                profile_form.save()
                request.user.first_name = user_form.cleaned_data['first_name']
                request.user.last_name = user_form.cleaned_data['last_name']
                request.user.email = profile_form.cleaned_data['unique_email']
                request.user.save()
                FutureMessage.objects.create(user=request.user, 
                                             mtype='success',
                                             title='',
                                             text=PROFILE_SAVED)
                return redirect('/accounts/user-room/#profile-nofollow')
            except IntegrityError, e:
                connection._rollback()
                connection._rollback()
                matches = re.search(r'\((.+?)\)=.+?\salready\sexists', e.message)
                key = matches.group(1)
                if key == 'username':
                    key = 'Email'
                request.alert_messages += [Message('error', REGISTER_INTEGRITY_ERROR % key)]
                forms['error'] = True
                return forms
        else:
            request.alert_messages += [Message('error', PROFILE_FORM_FAILD)]
            forms['error'] = True
            return forms
    else:
        user_initial = {
            'first_name':request.user.first_name,
            'last_name':request.user.last_name
        }
        return {
            'user_form': UserForm(initial=user_initial),
            'profile_form': accounts.Forms.profile(instance=request.user.get_profile()),
            'password_form': PasswordForm(),
            'error': False
        }


def password_change_handler(request):
    """
    User password GET and POST forms handler.

    Return form and form.error is True if there are an errors.
    If POST was successfull, then handler will return redirect 
    to the /accounts/user-room/#password-nofollow.
    """
    if not request.user.is_authenticated():
        return redirect('/')
    if request.method == 'POST' and request.POST.get('pwd_form', False):
        form = ChangePasswordForm(data=request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            FutureMessage.objects.create(user=request.user, 
                                         mtype='success',
                                         title='',
                                         text=PASSWORD_SAVED)
            return redirect('/accounts/user-room/#password-nofollow')
        else:
            request.alert_messages += [Message('error', PASSWORD_CONFIRM_FAILD)]
            form.error = True
            return form
    else:
        return ChangePasswordForm()


