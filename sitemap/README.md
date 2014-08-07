# Sitemap

Generate xml sitemap. See also: [sitemaps.org](http://www.sitemaps.org/protocol.html "sitemaps.org").

I know, that there is a django.contrib.sitemap, but did you saw that? Usually contrib apps are pretty graceful, but
in this case, there are much extra entities such as Sitemap class and Generics. It is not MVC architecture, such you have to write
horrible code in urls file, using Generics... Some one like it, but I don't. So I have decided to write less powerful but more pretty
code here...

## Features

* Add content of a model to sitemap.xml by mix it with SiteMapMixin
* Model priority
* Object personal priority
* Filtering default queryset
* Extends default template

## Install and configure

    # settings.py
    INSTALLED_APPS = (
        # ...

        'bicycle.sitemap',
        
        # ...)

    # urls.py
    urlpatterns = patterns('',
        # ...

        (r'^sitemap\.xml', include('bicycle.sitemap.urls')),

        # ...
    )

    # models.py
    from bicycle.sitemap.models import SiteMapMixin


    class News(SiteMapMixin):
        # ...

        # is not required, default: 0.5
        default_priority = 0.3

        # is not required, by default returns cls.objects.all()
        @classmethod
        def get_sitemap_queryset(cls):
            return cls.objects.published()

## Custom template

You can make custom sitemap template. To add some extra static url tags there are buildin block `extra`.

Make template file with path `sitemap.xml` in one of your accessable template folders:

    {% extends "sitemap/base.xml" %}

    {% block extra %}
       <url>
          <loc>http://{{ request.META.HTTP_HOST }}/extra/</loc>
          <priority>0.8</priority>
       </url>
    {% endblock extra %}