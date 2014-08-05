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
            'priority': 0.5,
            'ids': {
                # an object of mainapp.Product with pk=5 has 0.8 priority
                5: 0.8,
            }
        }
    }