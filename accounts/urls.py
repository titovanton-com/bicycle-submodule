# coding: UTF-8

from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns('bicycle.accounts.views',
    # user
    url(r'^logout/handler/$', 'logout_handler'),
)

def account_urlpatterns(AccountView):
    return patterns('',
        url(r'^(?P<todo>\w+?)/$', AccountView.as_view()),
    )
