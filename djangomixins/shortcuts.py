# coding: UTF-8

from django.conf import settings
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage


def get_page(query_set, limit, current_page):
    pager = Paginator(query_set, limit)
    try:
        page = pager.page(current_page)
    except EmptyPage:
        page = pager.page(1)
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
    msg.send()


def send_email_rq(subject, from_email, to, tpl='email.html', context={}):
    """
        Sending HTML E-Mail via Django-rq

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

    func = 'bicycle.djangomixins.shortcuts._send_email_job'
    django_rq.enqueue(func, subject, from_email, json.dumps(to), tpl, json.dumps(context))


def session_start(request):
    if getattr(request.session, 'session_key', None) is None:
        request.session['session start'] = True
        request.session.save()
    return request.session.session_key


def false_icon():
    return u'<img alt="False" src="%sadmin/img/icon-no.gif">' % settings.STATIC_URL


def true_icon():
    return u'<img alt="True" src="%sadmin/img/icon-yes.gif">' % settings.STATIC_URL