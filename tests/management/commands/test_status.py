# coding: UTF-8

import json
import requests

from django.core.management.base import BaseCommand
from django.utils.encoding import force_str
from django.utils.termcolors import make_style


success = make_style(fg='green')
error = make_style(fg='red')
notice = make_style(fg='yellow')


def test_status(urls_list):
    ok_count = 0
    not_ok_count = {}
    is_permanent_redirect_count = []
    is_redirect_count = []

    for method, url, params in urls_list:

        if method.upper().startswith('AJAX/'):
            tyype = method.upper().replace('AJAX/', '')
            headers = {'X-Requested-With': 'XMLHttpRequest'}
        else:
            tyype = method.upper()
            headers = {}

        if tyype == 'GET':
            m = requests.get
        elif tyype == 'POST':
            m = requests.post
        elif tyype == 'PUT':
            m = requests.put
        elif tyype == 'DELETE':
            m = requests.delete
        elif tyype == 'HEAD':
            m = requests.head
        elif tyype == 'OPTIONS':
            m = requests.options
        else:
            continue

        r = m(url, params=params, headers=headers)
        print method, url, params
        output = u'OK: %s, status_code: %s, is_permanent_redirect: %s, is_redirect: %s'
        print output % (
            r.ok and success('True') or error('False'),
            r.status_code == 200 and success('200') or error(r.status_code),
            r.is_permanent_redirect and notice('True') or 'False',
            r.is_redirect and notice('True') or 'False',
        )

        if r.ok:
            ok_count += 1
        elif not_ok_count.get(r.status_code, False):
            not_ok_count[r.status_code] += [u'%s %s %s' % (method, url, params)]
        else:
            not_ok_count[r.status_code] = [u'%s %s %s' % (method, url, params)]

    total_count = len(urls_list)

    print u"""
        Summary:
        --------
            total:  %s requests
            OK:     %s requests
            not OK: %s requests
    """ % (notice(force_str(total_count)),
           success(force_str(ok_count)),
           error(force_str(total_count - ok_count)))

    if len(urls_list) > ok_count:
        print u"""        Errors detail:
        --------------"""

        for code in not_ok_count:
            for r in not_ok_count[code]:
                print u"            %s: %s" % (error(code), r)

        print ""


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ Test list of tuples(type, url, params) for HTTP status
            ------------------------------------------------------

        Outpute:
        ::
            HTTP OK, status_code, is_permanent_redirect, is_redirect

        Usage:
        ::
            # tests/test_status.py

            urls_list = [
                ('GET', 'http://example.com/a/', {'q': 'fee'}),
                ('POST', 'http://example.com/form/', {'email': 'exmpl@exm.com', 'name': 'Ivan'}),
                ('AJAX/GET', 'http://example.com/ajax/', {'q': 'foo'}),
            ]
        """

        try:
            from tests.test_status import urls_list
        except ImportError:
            print error('ImportError: from tests.test_status import urls_list')
        else:
            test_status(urls_list)
