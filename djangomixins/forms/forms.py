# coding: UTF-8

from django import forms
from django.conf import settings


class CaptchaFormNotAvailable(Exception):
    pass


def get_captcha_form():
    if not getattr(settings, 'CAPTCHA_FORM', False):
        raise CaptchaFormNotAvailable(
            'You need to set CAPTCHA_FORM in your project settings')
    if settings.CAPTCHA_FORM == 'ReCaptchaForm':
        if not getattr(settings, 'RECAPTCHA_PUBLIC_KEY', False) or\
           not getattr(settings, 'RECAPTCHA_PRIVATE_KEY', False) or\
           getattr(settings, 'RECAPTCHA_THEME', None) is None:
            raise CaptchaFormNotAvailable('You need to set RECAPTCHA_PUBLIC_KEY, '
                                          'RECAPTCHA_PRIVATE_KEY and RECAPTCHA_THEME '
                                          'in your project settings')
        try:
            from captcha.fields import ReCaptchaField
            from bicycle.djangomixins.messages import RECAPTCHA_ERRORS
        except ImportError:
            raise CaptchaFormNotAvailable(
                'Unable to import the ReCaptchaField or RECAPTCHA_ERRORS')
        try:
            choices = ('red', 'white', 'blackglass', 'clean')
            theme = choices[settings.RECAPTCHA_THEME]
        except IndexError:
            raise CaptchaFormNotAvailable('RECAPTCHA_THEME must be int and is'
                                          'an index of the following tuple'
                                          '(\'red\', \'white\', \'blackglass\', \'clean\')')
        class ReCaptchaForm(forms.Form):
            captcha = ReCaptchaField(public_key=settings.RECAPTCHA_PUBLIC_KEY,
                                     private_key=settings.RECAPTCHA_PRIVATE_KEY,
                                     error_messages=RECAPTCHA_ERRORS,
                                     attrs={'theme': theme})
        return ReCaptchaForm
    elif settings.CAPTCHA_FORM == 'SuperCaptchaForm':
        try:
            import supercaptcha
        except ImportError:
            raise CaptchaFormNotAvailable('Unable to import the supercaptcha')
        class SuperCaptchaForm(forms.Form):
            captcha = supercaptcha.CaptchaField()
        return SuperCaptchaForm
