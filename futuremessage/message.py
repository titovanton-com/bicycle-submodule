# coding: UTF-8

import re


class Message(object):
    def __init__(self, mtype, text, title=None):
        assert mtype in ['info', 'success', 'error']
        self.mtype = mtype
        self.text = text
        if title is not None:
            self.title = title
        else:
            case = {
                'info': 'Уведомление.',
                'success': 'Успех!',
                'error': 'Ошибка!',
            }
            self.title = case[mtype]

