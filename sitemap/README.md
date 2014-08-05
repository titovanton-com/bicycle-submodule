# Sitemap

Generate xml sitemap. Learn standart: [www.sitemaps.org](http://www.sitemaps.org, "www.sitemaps.org").

## Install and configure

    # settings.py
    INSTALLED_APPS = (
        # ...

        'bicycle.sitemap',
        
        # ...)

    # configure example
    SITEMAP = {
        'mainapp.Product': {
            # not required, default: 0.5
            'priority': 0.5,
            # not required, default: empty dict
            'ids': {
                # an object of mainapp.Product with pk=5 has 0.8 priority
                5: 0.8,
            }
        }
    }

    # urls.py
    urlpatterns = patterns('',
        # ...

        (r'^sitemap\.xml', include('bicycle.sitemap.urls')),

        # ...
    )

## Custom template

You can make custom sitemap template. To add some extra url tags there are buildin block `extra`.

Make template file with path `sitemap.xml`:

    {% extends "sitemap/base.xml" %}

    {% block extra %}
       <url>
          <loc>http://{{ DOMAIN }}/extra/</loc>
          <priority>0.8</priority>
       </url>
    {% endblock extra %}