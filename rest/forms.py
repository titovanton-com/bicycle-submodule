# -*- coding: utf-8 -*-

from django import forms


class RestForm(forms.Form):
    data = forms.CharField()
