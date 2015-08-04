# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View

from oauth2client import client


def flow_arguments():
    return {
        'client_secret': getattr(settings, 'GDRIVE_OAUTH_SECRET', 'client_secrets.json'),
        'scope': getattr(settings, 'GDRIVE_OAUTH_SCOPE', 'https://www.googleapis.com/auth/drive'),
        'redirect_uri': getattr(settings, 'GDRIVE_OAUTH_REDIRECT_URI', '/gdrive/oauth/'),
    }


class OAuthMixin(object):

    def get(self, request, *args, **kwargs):

        if 'gdrive_oauth_credentials' not in request.session:
            flow = client.flow_from_clientsecrets(**flow_arguments())
            auth_uri = flow.step1_get_authorize_url()
            request.session['gdrive_oauth_redirect_back'] = request.get_full_path()
            request.session.modified = True
            return redirect(auth_uri)

        else:
            return super(OAuthMixin, self).get(self, request)


class OAuthView(View):

    def get(self, request):
        flow = client.flow_from_clientsecrets(**flow_arguments())

        if 'code' in request.GET:
            auth_code = request.GET['code']
            credentials = flow.step2_exchange(auth_code)
            request.session['gdrive_oauth_credentials'] = credentials.to_json()

            if 'gdrive_oauth_redirect_back' in request.session
                redirect_back = request.session['gdrive_oauth_redirect_back']
                del request.session['gdrive_oauth_redirect_back']
                request.session.modified = True
                return redirect(redirect_back)
            else:
                return redirect('/')

        elif 'error' in request.GET:
            request.session['gdrive_oauth_error'] = request.GET['error']
            request.session.modified = True

        else:
            auth_uri = flow.step1_get_authorize_url()
            return redirect(auth_uri)
