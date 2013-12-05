# coding: UTF-8

from message import Message
from models import FutureMessage


class FutureMessageMiddleware(object):
    def process_request(self, request):
        if not request.is_ajax():
            if request.user.is_authenticated():
                f = dict(user=request.user)
            else:
                f = dict(session_key=request.session.session_key)
            msgs = FutureMessage.objects.filter(**f)
            request.alert_messages = [Message(m.mtype, m.text, m.title) for m in msgs]
            msgs.delete()

        