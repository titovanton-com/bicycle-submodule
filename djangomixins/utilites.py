# coding: UTF-8

import re
import os
import hashlib

from django.conf import settings
from django.utils.timezone import now
# from django.db import models


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
    capital_letters = {u'А': u'A',
                       u'Б': u'B',
                       u'В': u'V',
                       u'Г': u'G',
                       u'Д': u'D',
                       u'Е': u'E',
                       u'Ё': u'E',
                       u'З': u'Z',
                       u'И': u'I',
                       u'Й': u'Y',
                       u'К': u'K',
                       u'Л': u'L',
                       u'М': u'M',
                       u'Н': u'N',
                       u'О': u'O',
                       u'П': u'P',
                       u'Р': u'R',
                       u'С': u'S',
                       u'Т': u'T',
                       u'У': u'U',
                       u'Ф': u'F',
                       u'Х': u'H',
                       u'Ъ': u'',
                       u'Ы': u'Y',
                       u'Ь': u'',
                       u'Э': u'E', }
    capital_letters_transliterated_to_multiple_letters = {u'Ж': u'Zh',
                                                          u'Ц': u'Ts',
                                                          u'Ч': u'Ch',
                                                          u'Ш': u'Sh',
                                                          u'Щ': u'Sch',
                                                          u'Ю': u'Yu',
                                                          u'Я': u'Ya', }
    lower_case_letters = {u'а': u'a',
                          u'б': u'b',
                          u'в': u'v',
                          u'г': u'g',
                          u'д': u'd',
                          u'е': u'e',
                          u'ё': u'e',
                          u'ж': u'zh',
                          u'з': u'z',
                          u'и': u'i',
                          u'й': u'y',
                          u'к': u'k',
                          u'л': u'l',
                          u'м': u'm',
                          u'н': u'n',
                          u'о': u'o',
                          u'п': u'p',
                          u'р': u'r',
                          u'с': u's',
                          u'т': u't',
                          u'у': u'u',
                          u'ф': u'f',
                          u'х': u'h',
                          u'ц': u'ts',
                          u'ч': u'ch',
                          u'ш': u'sh',
                          u'щ': u'sch',
                          u'ъ': u'',
                          u'ы': u'y',
                          u'ь': u'',
                          u'э': u'e',
                          u'ю': u'yu',
                          u'я': u'ya', }
    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = re.sub(ur"%s([а-я])" % cyrillic_string, ur'%s\1' % latin_string, string)
    for dictionary in (capital_letters, lower_case_letters):
        for cyrillic_string, latin_string in dictionary.iteritems():
            string = string.replace(cyrillic_string, latin_string)
    for cyrillic_string, latin_string in capital_letters_transliterated_to_multiple_letters.iteritems():
        string = string.replace(cyrillic_string, latin_string.upper())
    return string


def valid_file_name(word):
    word = transliterate(word).lower().strip()
    patrn = r'[^a-zA-Z0-9_.()-]'
    repl = '-'
    return re.sub(patrn, repl, word)


def valid_alias(word):
    return machine_word(transliterate(word))


def upload_file(instance, filename):
    return os.path.join(u'%s' % instance.__class__.__name__.lower(),
                        valid_file_name(filename))


def upload_logo(instance, filename):
    return os.path.join(u'%s_logo' % instance.__class__.__name__.lower(),
                        valid_file_name(filename))


def md5_random_string():
    return hashlib.md5(now().isoformat()).hexdigest()
