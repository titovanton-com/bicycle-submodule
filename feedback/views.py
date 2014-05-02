# -*- coding: utf-8 -*-

from django.shortcuts import redirect
from django.views.generic.edit import CreateView

from forms import FeedbackForm


class FeedbackCreateView(CreateView):
    form_class = FeedbackForm
    thanks = False
    template_name = 'feedback/form.html'
    success_url = '/feedback/thanks/'
    success_message = u'<p><strong>Спасибо!</strong></p>\
                        <p>Ваше письмо мчится к нам со скоростью света! \
                        Мы свяжемся с Вами в ближайшее время...</p>'


    def get_context_data(self, **kwargs):
        context = super(FeedbackCreateView, self).get_context_data(**kwargs)
        if getattr(self, 'thanks', False):
            context['success_message'] = self.success_message
        return context
