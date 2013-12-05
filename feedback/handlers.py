# coding: UTF-8

from django.shortcuts import redirect
from django.conf import settings
from bicycle.futuremessage.models import FutureMessage

from forms import FeedbackForm
from messages import FEEDBACK_SUCCESS


def feedback_handler(request, success=FEEDBACK_SUCCESS):
    """
    Feedback GET and POST handler

    Return FeedbackForm instance.
    """
    if request.method == 'GET':
        if request.user.is_authenticated():
            return FeedbackForm(initial={'name': request.user.get_full_name(),
                                         'user': request.user,
                                         'email': request.user.get_profile().unique_email})
        else:
            return FeedbackForm()
    elif request.method == 'POST':
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated():
                feedback.user = request.user
                FutureMessage.objects.create(user=request.user, 
                                             mtype='success',
                                             title=success[1],
                                             text=success[0])
            else:
                if request.session.session_key is None:
                    request.session['cart'] = 'is not empty now'
                    request.session.save()
                FutureMessage.objects.create(session_key=request.session.session_key, 
                                             mtype='success',
                                             title=success[1],
                                             text=success[0])
            feedback.save()
            return redirect('/feedback/')
        else:
            return form
