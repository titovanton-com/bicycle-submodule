# coding: UTF-8

from django import forms


class GetPage(forms.Form):
    page = forms.IntegerField(required=False, min_value=1)

    def clean_page(self):
        if self.cleaned_data['page'] is None:
            return 1
        else:
            return self.cleaned_data['page']