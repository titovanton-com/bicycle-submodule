# coding: UTF-8

def update_index():
    import sys
    import codecs
    from haystack.management.commands import update_index
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    update_index.Command().handle()