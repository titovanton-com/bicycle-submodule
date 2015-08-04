# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View

from oauth2client import client


def flow_arguments():
    return client.flow_from_clientsecrets(
        getattr(settings, 'GDRIVE_OAUTH_SECRETS', 'client_secrets.json'),
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

        if 'gdrive_oauth_credentials' not in request.session:
            flow = flow_arguments()
            request.session['gdrive_oauth_redirect_back'] = request.get_full_path()
            request.session.modified = True
            return flow.step1_get_authorize_url()
        else:
            return False


class OAuthView(View):

    def get(self, request):
        flow = flow_arguments()

        if 'code' in request.GET:
            auth_code = request.GET['code']
            credentials = flow.step2_exchange(auth_code)
            request.session['gdrive_oauth_credentials'] = credentials.to_json()

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
