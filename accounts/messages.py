# coding: UTF-8

from django.utils.translation import ugettext_lazy as _

PASSWORD_CONFIRM_FAILD = u'Вы ввели неверное подтверждение пароля'
REGISTER_FAILED = u'Вы неверно заполнили форму регистрации!'
LOGIN_FAILED = u'Неверный имя пользователя или пароль!'
PASSWORD_FAILED = u'Неверный пароль!'
LOGIN_FORM_FAILED = u'Вы неверно заполнили форму авторизации!'
REGISTER_INTEGRITY_ERROR = u'Поле %s - уникальное. Если Вы видите это сообщение, значит \
                             пользователь с таким значением этого поля уже есть.'
REGISTRATION_SUCCESS = (u'Теперь Вы можете воспользоваться дополнительными возможностями'
                        u' <a href="/accounts/user-room/">Личного Кабинета</a>',
                        u'Ваша учётная запись создана!')
LOGIN_SUCCESS = (u'Вы можете воспользоваться дополнительными возможностями '
                 u'<a href="/accounts/user-room/">Личного Кабинета</a>',
                 u'Добро пожаловать на сайт!',)
PROFILE_SAVED = u'Профиль сохранен.'
PROFILE_FORM_FAILD = u'Вы не верно заполнили форму!'
PASSWORD_SAVED = u'Пароль изменен.'
USER_DOES_NOT_EXIST = u'Такой пользователь не зарегистрирован в системе!'
PASSWORD_RECOVERY_SUCCESS = (u'На Ваш почтовый ящик было отправлено письмо с новым паролем.',
                             u'Проверьте Вашу электронную почту!')