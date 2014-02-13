# -*- coding: utf-8 -*-

from django.views.generic import CreateView

from forms import FeedbackForm


class FeedbackCreateView(CreateView):
    form_class = FeedbackForm
    template_name = 'feedback/form.html'
