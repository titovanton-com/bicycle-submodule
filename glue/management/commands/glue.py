# coding: UTF-8


import os
import shutil
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):

    def handle(self, *args, **options):
        conf = settings.GLUE_CONFIG
        command = ['glue', conf['source'], conf['output'], '--project', '--recursive', ]
        ext = '.css'

        try:
            if conf['less']:
                command += ['--less']
                ext = '.less'
            if conf['css_url']:
                command += ['--url=%s' % conf['css_url']]
            if conf['crop']:
                command += ['--crop']
            if conf['margin']:
                command += ['--margin=%d' % conf['margin']]
        except KeyError:
            pass

        try:
            subprocess.call(command)
        except OSError:
            raise Exception('glue does not exists on your os')
        else:
            if not os.path.exists(conf['move_styles_to']):
                os.makedirs(conf['move_styles_to'])

            for basename in os.listdir(conf['output']):
                if basename.endswith(ext):
                    pathname = os.path.join(conf['output'], basename)
                    dstdir = os.path.join(conf['move_styles_to'], basename)

                    if os.path.isfile(pathname):
                        shutil.move(pathname, dstdir)

                        if conf['csscomb']:
                            try:
                                subprocess.call(['csscomb', dstdir])
                            except OSError:
                                raise Exception('csscomb does not exists on your os')
