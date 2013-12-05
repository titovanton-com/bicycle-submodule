# coding: UTF-8

from django import forms

from models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ('user', 'created', 'updated', 'published')