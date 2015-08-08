# -*- coding: utf-8 -*-

import datetime
import dateutil.parser

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View

from apiclient import errors
from oauth2client import client
from oauth2client.client import OAuth2Credentials
from oauth2client.client import FlowExchangeError

from bicycle.core.shortcuts import localize_date
from bicycle.core.views import JsonResponseMixin
from bicycle.core.views import ResponseMixin

from __init__ import GDoc
from __init__ import GDrive
from __init__ import GError
from __init__ import GFactory
from __init__ import GFolder
from __init__ import GSheet


def flow_arguments():
    return client.flow_from_clientsecrets(
        getattr(settings, 'GDRIVE_OAUTH_SECRET', 'client_secret.json'),
        scope=getattr(settings, 'GDRIVE_OAUTH_SCOPE', 'https://www.googleapis.com/auth/drive'),
        redirect_uri=getattr(settings, 'GDRIVE_OAUTH_REDIRECT_URI', '/gdrive/oauth/')
    )


class OAuthMixin(object):

    def dispatch(self, request, *args, **kwargs):

        if request.method.lower() in self.http_method_names:
            oauth_uri = self.oauth(request)

            if oauth_uri:
                return redirect(oauth_uri)
            else:
                return super(OAuthMixin, self).dispatch(request, *args, **kwargs)

        else:
            return self.http_method_not_allowed(request, *args, **kwargs)

    def oauth(self, request):

        def first_step():

            try:
                flow = flow_arguments()
                request.session['gdrive_oauth_redirect_back'] = request.get_full_path()
                request.session.modified = True
                return flow.step1_get_authorize_url()
            except FlowExchangeError, error:
                raise GError(error)

        if 'gdrive_oauth_credentials' not in request.session:
            return first_step()
        else:
            credentials = OAuth2Credentials.from_json(request.session['gdrive_oauth_credentials'])

            if credentials.access_token_expired:
                del request.session['gdrive_oauth_credentials']
                request.session.modified = True
                return first_step()
            else:
                return False


class OAuthView(View):

    def get(self, request):

        try:
            flow = flow_arguments()

            if 'code' in request.GET:
                auth_code = request.GET['code']
                credentials = flow.step2_exchange(auth_code)
                request.session['gdrive_oauth_credentials'] = credentials.to_json()
                request.session.modified = True

            elif 'error' in request.GET:
                request.session['gdrive_oauth_error'] = request.GET['error']
                request.session.modified = True

            else:
                auth_uri = flow.step1_get_authorize_url()
                return redirect(auth_uri)

            if 'gdrive_oauth_redirect_back' in request.session:
                redirect_back = request.session['gdrive_oauth_redirect_back']
                del request.session['gdrive_oauth_redirect_back']
                request.session.modified = True
                return redirect(redirect_back)
            else:
                return redirect('/')

        except FlowExchangeError, error:
            raise GError(error)


class TestsView(OAuthMixin, JsonResponseMixin, View):

    def __prepare_tests(self, request):
        self.gdrive = GDrive(request)
        self.errors = []

    def __response(self):

        if not self.errors:
            self.errors = ['Tests complite successful']

        return self.json_response(self.errors)

    def __factory_test(self):
        obj = GFactory({'mimeType': u'application/vnd.google-apps.document'})
        assert isinstance(obj, GDoc), 'Factory test failed on GDoc'
        obj = GFactory({'mimeType': u'application/vnd.google-apps.spreadsheet'})
        assert isinstance(obj, GSheet), 'Factory test failed on GSheet'
        obj = GFactory({'mimeType': u'application/vnd.google-apps.folder'})
        assert isinstance(obj, GFolder), 'Factory test failed on GFolder'

    def __insert_test(self):
        file_to_insert = GSheet({'title': 'test'})
        inserted = self.gdrive.save(file_to_insert)

        msg = 'Inserted file is not instance of GSheet as expected'
        assert isinstance(inserted, GSheet), msg
        msg = 'Inserted file title and origin title are different'
        assert inserted.title == file_to_insert.title, msg

        return inserted

    def __update_test(self, file_to_update):
        file_to_update.description = 'hello world'
        updated = self.gdrive.save(file_to_update)

        msg = 'Updated file and origin file are different'
        assert file_to_update == updated, msg
        msg = 'Updated file description and origin description are different'
        assert file_to_update.description == updated.description, msg

        return updated

    def __delete_test(self, file_to_delete):
        deleted = self.gdrive.delete(file_to_delete)

        msg = 'Delete test faild.'
        assert deleted == '', msg

    def get(self, request):
        self.__prepare_tests(request)

        try:
            self.__factory_test()
            file_inserted = self.__insert_test()
            file_updated = self.__update_test(file_inserted)
            self.__delete_test(file_updated)
        except AssertionError, error:
            self.errors += [error]

        return self.__response()
