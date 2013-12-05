# coding: UTF-8

from django import forms
from django.contrib.auth.models import User

from messages import PASSWORD_CONFIRM_FAILD
from messages import USER_DOES_NOT_EXIST


class PasswordForm(forms.Form):
    password = forms.CharField(max_length=128, label=u'Пароль', 
                               widget=forms.PasswordInput(render_value=False))


class EmailForm(forms.Form):
    user_profile_model = None
    user_does_not_exist = USER_DOES_NOT_EXIST
    unique_email = forms.EmailField(label=u'Email')

    def clean_unique_email(self):
        email = self.cleaned_data['unique_email']
        try:
            profile = self.user_profile_model.objects.get(unique_email=email)
        except:
            raise forms.ValidationError(self.user_does_not_exist)
        return email


class LoginForm(forms.Form):
    success = forms.CharField(widget=forms.HiddenInput())
    unique_email = forms.EmailField(label=u'Email')
    password = forms.CharField(max_length=128, label=u'Пароль', 
                               widget=forms.PasswordInput(render_value=False))


class UserForm(forms.Form):
    first_name = forms.CharField(max_length=128, label=u'Имя')
    last_name = forms.CharField(max_length=128, label=u'Фамилия')
    username = forms.CharField(max_length=128, label=u'Псевдоним', required=False)


class PasswordAndConfirmForm(PasswordForm):
    password_confirm_faild = PASSWORD_CONFIRM_FAILD
    confirm = forms.CharField(max_length=128, label=u'Пароль еще раз', 
                              widget=forms.PasswordInput(render_value=False))

    def clean_confirm(self):
        if self.cleaned_data['confirm'] != self.cleaned_data['password']:
            raise forms.ValidationError(self.password_confirm_faild)
        return self.cleaned_data['confirm']


class ChangePasswordForm(PasswordAndConfirmForm):
    old_password = forms.CharField(max_length=128, label=u'Старый пароль', 
                                   widget=forms.PasswordInput(render_value=False))


class HideUserField(forms.Form):
    model_instance = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())


class BySuccessRedirectTo(forms.Form):
    """
    If some action has succeeded, then we need to redirect to some path.
    We get it from GET URL parameter.
    """
    success = forms.CharField()