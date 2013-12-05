# coding: utf-8

# Piggy-back on internal csrf_exempt existence handling
from django.conf.urls import url
from tastypie.resources import csrf_exempt


class ExtensionBasedFormatMixin(object):

    def prepend_urls(self):
        """
        Returns a URL scheme based on the default scheme to specify
        the response format as a file extension, e.g. /api/v1/users.json
        """
        return [
            url(r"^(?P<resource_name>%s)\.(?P<format>\w+)$" % 
                self._meta.resource_name, 
                self.wrap_view('dispatch_list'), 
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema\.(?P<format>\w+)$" % 
                self._meta.resource_name, 
                self.wrap_view('get_schema'), 
                name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<pk_list>\w[\w/;-]*)\.(?P<format>\w+)$" %
                self._meta.resource_name, 
                self.wrap_view('get_multiple'), 
                name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)\.(?P<format>\w+)$" %
                self._meta.resource_name, 
                self.wrap_view('dispatch_detail'), 
                name="api_dispatch_detail"),
        ]

    def determine_format(self, request):
        """
        Used to determine the desired format from the request.format
        attribute.
        """
        if (hasattr(request, 'format') and
                request.format in self._meta.serializer.formats):
            return self._meta.serializer.get_mime_for_format(request.format)
        return super(ExtensionBasedFormatMixin, self).determine_format(request)

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(ExtensionBasedFormatMixin, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)
        return wrapper
