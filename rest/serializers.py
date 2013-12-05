# coding: utf-8

import re
import json

from tastypie.serializers import Serializer


class CamelCaseJSONSerializer(Serializer):
    formats = ['json']
    content_types = {
        'json': 'application/json',
    }

    def to_json(self, data, options=None):
        # Changes underscore_separated names to camelCase names to go from python
        # convention to javacsript convention
        data = self.to_simple(data, options)

        def underscoreToCamel(match):
            return match.group()[0] + match.group()[2].upper()

        def camelize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z]_[a-z]", underscoreToCamel, key)
                    new_dict[new_key] = camelize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = camelize(data[i])
                return data
            return data
        camelized_data = camelize(data)
        return json.dumps(camelized_data, sort_keys=True)

    def from_json(self, content):
        # Changes camelCase names to underscore_separated names to go from
        # javascript convention to python convention
        data = json.loads(content)

        def camelToUnderscore(match):
            return match.group()[0] + "_" + match.group()[1].lower()

        def underscorize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z][A-Z]", camelToUnderscore, key)
                    new_dict[new_key] = underscorize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = underscorize(data[i])
                return data
            return data
        underscored_data = underscorize(data)
        return underscored_data


def serialize_queryset(resource_class, queryset, is_search_queryset=False):
    # hand me a queryset, i give you dehydrated resources
    resource = resource_class()
    dd = {}

    # make meta
    dd['meta'] = {}
    dd['meta']['limit'] = 1000
    dd['meta']['next'] = None
    dd['meta']['offset'] = 0
    dd['meta']['previous'] = None
    dd['meta']['total_count'] = len(queryset)

    # objects
    dd['objects'] = []
    for obj in queryset:
        if is_search_queryset:
            bundle = resource.build_bundle(obj=obj.object)
        else:
            bundle = resource.build_bundle(obj=obj)
        dehydrated_obj = resource.full_dehydrate(bundle)
        dd['objects'].append(dehydrated_obj)

    # return dict
    return dd