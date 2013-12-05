# coding: UTF-8

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.conf import settings

from bicycle.variables.models import Variable


class Command(BaseCommand):
    help = u'''
        Sync model Variables with tuple named "site_variables"
        in variables.py modules of your all INSTALLED_APPS.
    '''
    def handle(self, *args, **options):
        for app_label in settings.INSTALLED_APPS:
            try:
                _temp = __import__('%s.variables' % app_label, 
                                   globals(), locals(), ['site_variables'], -1)
                site_variables = _temp.site_variables
                print u'-----------------------------'
                print (u'*** %s ***\n' % app_label).upper()
                for obj in site_variables:
                    if not Variable.objects.filter(name=obj.name):
                        obj.save()
                        print u'{0:31s} - saved.'.format(obj.name)
                    else:
                        print u'{0:31s} - already exists.'.format(obj.name)
                print u'\n-----------------------------'
            except ImportError:
                print u'In %s no variables found...' % app_label

