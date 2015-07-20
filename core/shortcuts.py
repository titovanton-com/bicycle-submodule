# coding: UTF-8

import datetime

from django.conf import settings
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator


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
    import pytz

    if format is not None:
        return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).strftime(format)
    else:
        return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))


def tz_iso_now():
    import pytz

    return datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)).isoformat()


def localize_date(d):
    import pytz

    try:
        return pytz.timezone(settings.TIME_ZONE).localize(d)
    except ValueError:  # already localized
        return d
