# -*- coding: utf-8 -*-

import datetime
import hashlib
import os
import random
import re

try:
    import pytz
except ImportError:
    pass

try:
    import requests
except ImportError:
    pass

try:
    import dateutil.parser
except ImportError:
    pass


from django.conf import settings
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now


class TemplateNotAvailable(Exception):
    pass


def get_template(app_name):
    if not getattr(settings, '%s_TEMPLATE' % app_name, False):
        raise TemplateNotAvailable(
            u'You need to set %s_TEMPLATE in your project settings' % app_name)
    return getattr(settings, '%s_TEMPLATE' % app_name)


class ClassNotAvailable(Exception):
    pass


def get_class(variable, module_name):
    if not getattr(settings, variable, False):
        raise ClassNotAvailable(
            'You need to set %s in your settings' % variable)
    try:
        app_label, class_name = getattr(settings, variable).split('.')
    except ValueError:
        raise ClassNotAvailable(
            'app_label and class_name should be separated by a dot in '
            'the %s setting' % variable)
    try:
        _temp = __import__('%s.%s' % (app_label, module_name), fromlist=[class_name])
        return getattr(_temp, class_name)
    except ImportError:
        raise ClassNotAvailable(
            'Unable to load class, check '
            '%s in your project settings' % variable)


def machine_word(word):
    word = word.lower().strip()
    patrn = r'[^a-zA-Z0-9-]'
    repl = '-'
    return re.sub(patrn, repl, word)


def transliterate(string):
    capital_letters = {u'А': u'A', u'Б': u'B', u'В': u'V', u'Г': u'G', u'Д': u'D',
                       u'Е': u'E', u'Ё': u'E', u'З': u'Z', u'И': u'I', u'Й': u'Y',
                       u'К': u'K', u'Л': u'L', u'М': u'M', u'Н': u'N', u'О': u'O',
                       u'П': u'P', u'Р': u'R', u'С': u'S', u'Т': u'T', u'У': u'U',
                       u'Ф': u'F', u'Х': u'H', u'Ъ': u'', u'Ы': u'Y', u'Ь': u'',
                       u'Э': u'E', }
    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh', u'Ц': u'Ts',
                                                          u'Ч': u'Ch', u'Ш': u'Sh',
                                                          u'Щ': u'Sch', u'Ю': u'Yu',
                                                          u'Я': u'Ya', }
    lower_case_letters = {u'а': u'a', u'б': u'b', u'в': u'v', u'г': u'g', u'д': u'd',
                          u'е': u'e', u'ё': u'e', u'ж': u'zh', u'з': u'z', u'и': u'i',
                          u'й': u'y', u'к': u'k', u'л': u'l', u'м': u'm', u'н': u'n',
                          u'о': u'o', u'п': u'p', u'р': u'r', u'с': u's', u'т': u't',
                          u'у': u'u', u'ф': u'f', u'х': u'h', u'ц': u'ts', u'ч': u'ch',
                          u'ш': u'sh', u'щ': u'sch', u'ъ': u'', u'ы': u'y', u'ь': u'',
                          u'э': u'e', u'ю': u'yu', u'я': u'ya', }

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = re.sub(ur"%s([а-я])" % cyrillic_string, ur'%s\1' % latin_string, string)

    for dictionary in (capital_letters, lower_case_letters):
        for cyrillic_string, latin_string in dictionary.iteritems():
            string = string.replace(cyrillic_string, latin_string)

    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = string.replace(cyrillic_string, latin_string.upper())

    return string


def md5_random_string():
    return hashlib.md5(now().isoformat()).hexdigest()


def valid_file_name(word):
    word = transliterate(word).lower().strip()
    patrn = r'[^a-zA-Z0-9_.()-]'
    repl = '-'
    fingerprint = md5_random_string()  # 32

    return u'%s-%s' % (fingerprint, re.sub(patrn, repl, word)[-20:])


def valid_slug(word):
    return machine_word(transliterate(word))


@deconstructible
class UploadToDir(object):

    def __init__(self, suffix=None):
        self.suffix = suffix

    def __call__(self, instance, filename):
        root_dir = instance.__class__.__name__.lower()

        if self.suffix is not None:
            root_dir += '_' + self.suffix

        file_name = valid_file_name(filename)

        return os.path.join(root_dir, file_name[0:2], file_name[2:4], file_name)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def random_datetime(start, end=None):
    """
    Rendom datetime object based on 2 dates

    :param start: start date
    :type start: string with valide format, for example ISO 8601

    :param end: end date, defaults to None
    :type end: string with valide format, for example ISO 8601

    - Gets 2 dates and returns a random datetime object with time zone based on settings.py
    - If end is None then now is used
    - Required: pytz, dateutil
    """

    tz = pytz.timezone(settings.TIME_ZONE)
    sdt = dateutil.parser.parse(start)

    if end is None:
        edt = datetime.datetime.now(tz)
    else:
        edt = dateutil.parser.parse(end)

    delta = edt - sdt
    random_seconds = int(round(delta.total_seconds() * random.random()))

    random_date = sdt + datetime.timedelta(0, random_seconds)

    try:
        return tz.localize(random_date)
    except ValueError:
        return random_date


def download_file(url, save_to=''):
    file_name = url.split('/')[-1]
    local_filename = os.path.join(save_to, file_name)

    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)

    with open(local_filename, 'wb') as f:

        for chunk in r.iter_content(chunk_size=1024):

            # filter out keep-alive new chunks
            if chunk:
                f.write(chunk)

    return file_name, local_filename


def get_page(query_set, request, limit=12):
    pager = Paginator(query_set, limit)

    try:
        page = pager.page(request.GET.get('page', 1))
    except PageNotAnInteger:
        page = pager.page(1)
    except EmptyPage:
        page = pager.page(pager.num_pages)
    return page


def _send_email_job(subject, from_email, to, tpl, context):
    import json

    from django.template import loader
    from django.template import Context
    from django.core.mail import EmailMultiAlternatives

    t = loader.get_template(tpl)
    c = Context(json.loads(context))
    content = t.render(c)
    msg = EmailMultiAlternatives(subject, content, from_email, json.loads(to))
    msg.content_subtype = "html"
    # needs to be more stable: return 1 as success, but no errors handling
    msg.send()


def send_email_rq(subject, from_email, to, tpl='email.html', context={}):
    """Sending HTML E-Mail via Django-rq

        Required:
            redis-server
            django-rq

        Argumets:
            subject - email subject string
            from_email - sender email addres
            to - list or tuple of recipients emails
            tpl - template path
            context - context dict
    """

    import json

    import django_rq

    func = 'bicycle.core.shortcuts._send_email_job'
    django_rq.enqueue(func, subject, from_email, json.dumps(to), tpl, json.dumps(context))


def session_start(request):
    if getattr(request.session, 'session_key', None) is None:
        request.session['session start'] = True
        request.session.save()
    return request.session.session_key


def tz_now(format=None):

    if format is not None:
        return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime(format)
    else:
        return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))


def tz_iso_now():
    return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).isoformat()


def localize_date(d):
    try:
        return pytz.timezone(settings.TIME_ZONE).localize(d)
    except ValueError:  # already localized
        return d
