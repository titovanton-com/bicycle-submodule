# coding: UTF-8

import json

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth.models import User
from bicycle.djangomixins.views import ToDoView
from bicycle.djangomixins.views import RenderWithContextMixin
# from bicycle.djangomixins.forms import get_captcha_form
from bicycle.djangomixins.utilites import machine_word
from bicycle.djangomixins.utilites import transliterate
from bicycle.djangomixins.utilites import md5_random_string
from bicycle.djangomixins.shortcuts import send_email_rq
from bicycle.djangomixins.shortcuts import session_start
from bicycle.futuremessage.message import Message
from bicycle.futuremessage.models import FutureMessage
from bicycle.rest.forms import RestForm
from bicycle.rest.views import JsonResponseMixin

from forms import ChangePasswordForm
from forms import UserForm
from forms import PasswordForm
from forms import PasswordAndConfirmForm
from forms import BySuccessRedirectTo
from forms import LoginForm
from forms import EmailForm
from messages import PASSWORD_FAILED
from messages import PROFILE_SAVED
from messages import REGISTER_INTEGRITY_ERROR
from messages import PROFILE_FORM_FAILD
from messages import PASSWORD_SAVED
from messages import PASSWORD_CONFIRM_FAILD
from messages import LOGIN_SUCCESS
from messages import LOGIN_FAILED
from messages import LOGIN_FORM_FAILED
from messages import REGISTRATION_SUCCESS
from messages import REGISTER_FAILED
from messages import PASSWORD_RECOVERY_SUCCESS


class LoginRegisterMixin(RenderWithContextMixin, ToDoView):

    # path
    logout_destination = '/'
    password_change_destination = '/accounts/user-room/#password-nofollow'
    profile_change_destination = '/accounts/user-room/#profile-nofollow'

    # forms
    _forms = {} # forms instances
    login_form = LoginForm
    user_form = UserForm
    profile_form = None
    password_and_confirm_form = PasswordAndConfirmForm
    captcha_form = None # get_captcha_form()
    email_form = EmailForm
    change_password_form = ChangePasswordForm
    password_form = PasswordForm
    by_success_redirect_to = BySuccessRedirectTo

    # models
    user_profile_model = None

    # messages
    password_confirm_faild_message = PASSWORD_CONFIRM_FAILD
    password_saved_message = PASSWORD_SAVED
    password_failed_message = PASSWORD_FAILED
    profile_saved_message = PROFILE_SAVED
    register_integrity_error = REGISTER_INTEGRITY_ERROR
    login_success = LOGIN_SUCCESS
    login_failed = LOGIN_FAILED
    login_form_failed = LOGIN_FORM_FAILED
    registration_success = REGISTRATION_SUCCESS
    register_failed = REGISTER_FAILED
    password_recovery_success = PASSWORD_RECOVERY_SUCCESS

    # email
    from_email = 'example@titovanton.com'
    pwd_recovery_tpl = 'account/mail/password_recovery.html'
    pwd_recovery_subject = u'Восстановление пароля'

    class UserAlreadyExists(Exception):
        pass

    def dispatch(self, request, *args, **kwargs):
        redirect_path = False
        if not request.user.is_authenticated() and not request.is_ajax():
            if request.method == 'POST' and request.POST.get('login', False):
                redirect_path = self._post_login_form(request)
            elif request.method == 'POST' and request.POST.get('register', False):
                redirect_path = self._post_register_form(request)
            elif request.method == 'POST' and request.POST.get('password_recover', False):
                redirect_path = self._post_password_recovery_form(request)
            else:
                self._get_login_form(request)
                self._get_register_forms(request)
                self._get_password_recovery_form(request)
            if redirect_path:
                return self.login_register_redirect(request, redirect_path, *args, **kwargs)
        return super(LoginRegisterMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(self._forms)
        return super(LoginRegisterMixin, self).get_context_data(**kwargs)

    def get_logout(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            auth.logout(request)
        return redirect(self.logout_destination)

    def hook_login_success_message(self, user):
        FutureMessage.objects.create(user=user,
                                     mtype='success',
                                     title=self.login_success[1],
                                     text=self.login_success[0])

    def hook_login_success(self, request, user, profile):
        pass

    def hook_login_failed_message(self, request):
        self._forms['login_form_error'] = True
        request.alert_messages += [Message('error', self.login_failed)]

    def hook_login_failed(self, request):
        pass

    def hook_login_form_failed_message(self, request):
        self._forms['login_form_error'] = True
        request.alert_messages += [Message('error', self.login_form_failed)]

    def hook_login_form_failed(self, request):
        pass

    def hook_register_success_message(self, user):
        FutureMessage.objects.create(user=user,
                                     mtype='success',
                                     title=self.registration_success[1],
                                     text=self.registration_success[0])

    def hook_register_success(self, request, user, profile):
        pass

    def hook_register_failed_message(self, request, error):
        request.alert_messages += [Message('error', self.register_integrity_error % error)]
        request.register_form_error = True

    def hook_register_failed(self, request):
        pass

    def hook_register_form_failed_message(self, request):
        request.register_form_error = True
        request.alert_messages += [Message('error', self.register_failed)]

    def hook_register_form_failed(self, request):
        pass

    def _get_login_form(self, request):
        success_form = self.by_success_redirect_to(request.GET)
        success = request.path
        if success_form.is_valid():
            success = success_form.cleaned_data['success']
        self._forms['login_form'] = self.login_form(initial={'success': success})

    def _get_register_forms(self, request):
        self._forms['user_form'] = self.user_form()
        self._forms['profile_form'] = self.profile_form()
        self._forms['password_and_confirm_form'] = self.password_and_confirm_form()
        self._forms['captcha_form'] = self.captcha_form()

    def _get_password_recovery_form(self, request):
        self._forms['password_recover_form'] = self.email_form()

    def _post_login_form(self, request, *args, **kwargs):
        form = self.login_form(request.POST)
        self._forms['login_form'] = form
        if form.is_valid():
            unique_email = form.cleaned_data['unique_email']
            password = form.cleaned_data['password']
            try:
                profile = self.user_profile_model.objects.get(unique_email=unique_email)
                user = auth.authenticate(username=profile.user.username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    self.hook_login_success_message(user)
                    self.hook_login_success(request, user, profile)
                    return form.cleaned_data['success']
                else:
                    raise self.user_profile_model.DoesNotExist()
            except self.user_profile_model.DoesNotExist:
                self.hook_login_failed_message(request)
                self.hook_login_failed(request)
        else:
            self.hook_login_form_failed_message(request)
            self.hook_login_form_failed(request)
        self._get_register_forms(request)
        return False

    def _post_register_form(self, request, *args, **kwargs):
        self._forms['user_form'] = self.user_form(request.POST)
        self._forms['profile_form'] = self.profile_form(request.POST)
        self._forms['password_and_confirm_form'] = self.password_and_confirm_form(request.POST)
        self._forms['captcha_form'] = self.captcha_form(request.POST)
        if self._forms['user_form'].is_valid() and self._forms['profile_form'].is_valid() and \
           self._forms['password_and_confirm_form'].is_valid() and self._forms['captcha_form'].is_valid():
            try:
                username = self._forms['user_form'].cleaned_data['username']
                if username:
                    username = machine_word(transliterate(username))
                    if User.objects.get(username=username):
                        raise UserAlreadyExists(u'Логин')
                else:
                    username = machine_word(self._forms['profile_form'].cleaned_data['unique_email'])
                    if self.user_profile_model.objects.get(unique_email=unique_email):
                        raise UserAlreadyExists(u'Email')
                user = User.objects.create_user(
                    username=username,
                    email=self._forms['profile_form'].cleaned_data['unique_email'],
                    password=self._forms['password_and_confirm_form'].cleaned_data['password'])
                user.first_name = self._forms['user_form'].cleaned_data['first_name']
                user.last_name = self._forms['user_form'].cleaned_data['last_name']
                user.save()
                profile = self._forms['profile_form'].save(commit=False)
                profile.user = user
                profile.save()
                l_user = auth.authenticate(
                    username=user.username,
                    password=self._forms['password_and_confirm_form'].cleaned_data['password'])
                auth.login(request, l_user)
                self.hook_register_success_message(l_user)
                self.hook_register_success(request, l_user, profile)
                return request.path
            except UserAlreadyExists, error:
                self.hook_register_failed_message(request, error)
                self.hook_register_failed(request)
        else:
            self.hook_register_form_failed_message(request)
            self.hook_register_form_failed(request)
        self._get_login_form(request)
        return False

    def _post_password_recovery_form(self, request, *args, **kwargs):
        form = self.email_form(request.POST)
        self._forms['password_recover_form'] = form
        if form.is_valid():
            new_password = md5_random_string()[0:4]
            subject = self.pwd_recovery_subject
            from_email = self.from_email
            email = form.cleaned_data['unique_email']
            to = [email]
            tpl = self.pwd_recovery_tpl
            context = {
                'new_password': new_password,
                'email': email,
                'STATIC_URL': settings.STATIC_URL,
                'HTTP_HOST': request.META['HTTP_HOST'],
            }
            # it'll wark, becouse form is valid
            user = self.user_profile_model.objects.get(unique_email=email).user
            user.set_password(new_password)
            user.save()
            send_email_rq(subject, from_email, to, tpl, context)
            FutureMessage.objects.create(session_key=session_start(request),
                                         mtype='success',
                                         title=self.password_recovery_success[1],
                                         text=self.password_recovery_success[0])
            return request.path
        else:
            self._forms['password_recover_form_error'] = True
            return False

    def login_register_redirect(self, request, redirect_path=None, *args, **kwargs):
        if redirect_path is None:
            redirect_path = request.path
        return self.redirect(redirect_path)


class UserRoomViewBase(RenderWithContextMixin, ToDoView):

    def __get_password_change_form(self, request, *args, **kwargs):
        return self.change_password_form()

    def __post_password_change_form(self, request, *args, **kwargs):
        if request.POST.get('pwd_form', False):
            form = self.change_password_form(data=request.POST)
            if form.is_valid():
                request.user.set_password(form.cleaned_data['password'])
                request.user.save()
                FutureMessage.objects.create(user=request.user,
                                             mtype='success',
                                             title='',
                                             text=self.password_saved_message)
                return redirect(self.password_change_destination)
            else:
                request.alert_messages += [Message('error', self.password_confirm_faild_message)]
                form.error = True
                return form
        else:
            return self.__get_password_change(request, *args, **kwargs)

    def __get_profile_change_form(self, request, *args, **kwargs):
        user_initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        }
        return {
            'user_form': self.user_form(initial=user_initial),
            'profile_form': self.profile_form(instance=request.user.get_profile()),
            'password_form': self.password_form(),
            'error': False
        }

    def __post_profile_change_form(self, request, *args, **kwargs):
        if request.POST.get('profile_form', False):
            user_form = self.user_form(data=request.POST)
            profile_form = self.profile_form(
                data=request.POST, instance=request.user.get_profile())
            password_form = self.password_form(data=request.POST)
            forms = {
                'user_form': user_form,
                'profile_form': profile_form,
                'password_form': password_form,
                'error': False
            }
            if not password_form.is_valid() or\
               not request.user.check_password(password_form.cleaned_data['password']):
                forms['error'] = True
                request.alert_messages += [Message('error', self.password_failed_message)]
                return forms
            if user_form.is_valid() and profile_form.is_valid():
                try:
                    if User.objects.get(username=user_form.cleaned_data['username']):
                        raise UserAlreadyExists(u'Логин')
                    if self.user_profile_model.objects.get(
                        unique_email=profile_form.cleaned_data['unique_email']):
                        raise UserAlreadyExists(u'Email')
                    profile_form.save()
                    request.user.first_name = user_form.cleaned_data['first_name']
                    request.user.last_name = user_form.cleaned_data['last_name']
                    request.user.email = profile_form.cleaned_data['unique_email']
                    request.user.save()
                    FutureMessage.objects.create(user=request.user,
                                                 mtype='success',
                                                 title='',
                                                 text=self.profile_saved_message)
                    return redirect(self.profile_change_destination)
                except UserAlreadyExists, e:
                    request.alert_messages += [Message('error',
                                                       self.register_integrity_error % e)]
                    forms['error'] = True
                    return forms


class RestAccountViewMixin(JsonResponseMixin, ToDoView):
    user_profile_model = None
    
    def post_login(self, request,   *args, **kwargs):
        if not request.user.is_authenticated():
            form = RestForm(request.POST)
            if form.is_valid():
                try:
                    data = form.cleaned_data['data']
                    input_data = json.loads(data)
                except ValueError:
                    return self.response('JSON VALUE ERROR')
                try:
                    unique_email = input_data['unique_email']
                    password = input_data['password']
                except KeyError:
                    return self.response('DATA KEY ERROR')
                try:
                    profile = self.user_profile_model.objects.get(unique_email=unique_email)
                    user = auth.authenticate(username=profile.user.username, password=password)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                        return self.response('OK')
                    else:
                        return self.response('FAIL')
                except self.user_profile_model.DoesNotExist:
                    return self.response('USER DOES !EXIST')
            return self.response('IS !VALID')
        else:
            return self.response('U HAVE LOGGED IN')

    def get_logout(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            auth.logout(request)
            return self.response('OK')
        else:
            return self.response('U R !LOGGED IN')