# -*- coding: utf-8 -*-

import json
import inspect
from importlib import import_module
from itertools import chain

import requests
from django.conf import settings

from fields import BaseField
from fields import StringField


__all__ = ['SearchSchema', 'TitleSchemaMixin']

INDEX_PATTERN = {
    'settings': {
        'analysis': {
            'analyzer': {
                'my_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'standard',
                    'filter': ['lowercase', 'russian_morphology', 
                        'english_morphology', 'my_stopwords']
                }
            },
            'filter': {
                'my_stopwords': {
                    'type': 'stop',
                    'stopwords': u'а,без,более,бы,был,была,были,было,'\
                        u'быть,в,вам,вас,весь,во,вот,все,всего,всех,вы,'\
                        u'где,да,даже,для,до,его,ее,если,есть,еще,же,за,'\
                        u'здесь,и,из,или,им,их,к,как,ко,когда,кто,ли,'\
                        u'либо,мне,может,мы,на,надо,наш,не,него,нее,нет,'\
                        u'ни,них,но,ну,о,об,однако,он,она,они,оно,от,'\
                        u'очень,по,под,при,с,со,так,также,такой,там,те,'\
                        u'тем,то,того,тоже,той,только,том,ты,у,уже,хотя,'\
                        u'чего,чей,чем,что,чтобы,чье,чья,эта,эти,это,я,'\
                        u'a,an,and,are,as,at,be,but,by,for,if,in,into,'\
                        u'is,it,no,not,of,on,or,such,that,the,their,'\
                        u'then,there,these,they,this,to,was,will,with'
                }
            }
        }
    },
    'mappings': {}
}


class SearchSchemaBase(object):

    @classmethod
    def get_mappings(cls):
        properties = {key: value.data for key, value in cls.get_fields()}
        mappings = {
            cls.get_type(): {
                '_all': {'analyzer': 'my_analyzer'},
                'properties': properties
            }
        }
        return mappings

    @classmethod
    def get_fields(cls):
        return (tupl for tupl in inspect.getmembers(cls) if isinstance(tupl[1], BaseField))

    @classmethod
    def get_index(cls):
        return settings.INDEX_NAME

    @classmethod
    def get_host(cls):
        return settings.SEARCH_HOST

    @classmethod
    def get_type(cls):
        return '%s_%s' % (cls.model._meta.app_label, cls.model.__name__.lower())

    @classmethod
    def index_exists(cls, index_name):
        """Delete if already exists"""
        url = 'http://%s/%s/' % (cls.get_host(), index_name)
        exists = requests.head(url).status_code
        if exists == 200:
            url = 'http://%s/%s/?pretty' % (cls.get_host(), index_name)
            response = requests.delete(url)
            r = response.json()
            acknowledged = r.get('acknowledged', False)
            if acknowledged:
                print 'DELETE http://%s/%s/' % (cls.get_host(), index_name), response.text
            else:
                error = r.get('error', 'unknown error')
                raise Exception(error)

    @classmethod
    def create(cls, schemas):
        indeces = {}
        for obj in schemas:
            index_name = obj.get_index()
            if index_name not in indeces:
                cls.index_exists(index_name)
                indeces[index_name] = getattr(settings, 'INDEX_PATTERN', INDEX_PATTERN).copy()
            from pprint import pprint
            pprint (obj.get_mappings())
            indeces[index_name]['mappings'].update(obj.get_mappings())
        for index_name in indeces:
            url = 'http://%s/%s/?pretty' % (cls.get_host(), index_name)
            response = requests.put(url, data=json.dumps(indeces[index_name]))
            r = response.json()
            acknowledged = r.get('acknowledged', False)
            if acknowledged:
                print 'PUT http://%s/%s/' % (cls.get_host(), index_name), response.text
            else:
                error = r.get('error', 'unknown error')
                raise Exception(error)

    @classmethod
    def bulk(cls, schemas):
        data = ''
        _index_pattern = '{"index": {"_index": "%s", "_type": "%s", "_id": "%s"}}\n'
        for obj in schemas:
            for item in obj.model.get_bulk_qs():
                data += _index_pattern % (obj.get_index(),obj.get_type(), item.pk)
                properties = {}
                for name, field in obj.get_fields():
                    v = getattr(item, name)
                    properties[name] = getattr(item, '%s_to_index' % name, lambda: v)()
                data += json.dumps(properties) + '\n'
        url = 'http://%s/_bulk?pretty' % cls.get_host()
        response = requests.put(url, data=data)
        print 'PUT ' + url, response.text

    @classmethod
    def put(cls, obj):
        data = {}
        for name, field in cls.get_fields():
            v = getattr(obj, name)
            data[name] = getattr(obj, '%s_to_index' % name, lambda: v)()
        url = 'http://%s/%s/%s/%s' % (cls.get_host(), cls.get_index(), cls.get_type(), obj.pk)
        response = requests.put(url, data=json.dumps(data))

    @classmethod
    def exists(cls, pk):
        url = 'http://%s/%s/%s/%s' % (cls.get_host(), cls.get_index(), cls.get_type(), pk)
        return requests.head(url).status_code == 200

    @classmethod
    def delete(cls, obj):
        url = 'http://%s/%s/%s/%s' % (cls.get_host(), cls.get_index(), cls.get_type(), obj.pk)
        response = requests.delete(url)


class QueryStringMixin(object):
    # TODO: provide query_sting with several types and indeces
    @classmethod
    def get_query_pattern(cls, query):
        return {
            'query': {
                'query_string': {
                    'query': query
                }, 
                'analyze_wildcard': True,
                '_source': False
            }
        }

    # TODO: pagination
    @classmethod
    def query_string(cls, query):
        url = u'http://%s/%s/%s/_search' % (cls.get_host(), cls.get_index(), cls.get_type())
        data = cls.get_query_pattern(query)
        response = requests.post(url, data=json.dumps(data))
        hits = response.json()["hits"]["hits"]
        ids = {hit['_id']: hit['_score'] for hit in hits}
        qs = cls.model.objects.filter(pk__in=ids.keys())
        objects = sorted(chain(qs), reverse=True, key=lambda obj: ids[str(obj.pk)])
        return objects


class SearchSchema(SearchSchemaBase, QueryStringMixin):
    pass


class TitleSchemaMixin(SearchSchema):
    title = StringField(boost=4)
