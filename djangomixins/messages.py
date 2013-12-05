# coding: UTF-8

from django.utils.translation import ugettext_lazy as _


FORM_FAILED = u"Вы неверно заполнили форму!"
FORM_ALL_REQUIRED = u"Проверьте правильность заполнения формы. Все поля обязательны."
RECAPTCHA_ERRORS = {
    'required': _(u'Введите пожалуйста текст с картинки!'),
    'captcha_invalid': _(u'Вы допустили ошибку, попробуйте еще раз.'),
}
PHONE_ERROR_MESSAGES = {
    'required': _(u'Это поле обязательно для заполнения.'),
    'invalid': _(u'Введите корректное значение. Если телефон домашний - \
        укажите код города в скобках. <strong>Например: +7(495)888-44-33</strong>'),
}