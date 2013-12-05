# coding: UTF-8

from bicycle.variables.models import Variable


def tags(request):
    yandex_verification = u'<meta content="%s" name="yandex-verification">' % \
                            Variable.objects.get(name='yandex_verification').value
    google_site_verification = u'<meta content="%s" name="google-site-verification">' % \
                            Variable.objects.get(name='google_site_verification').value
    return {
        'GOOGLE_ANALYTICS': Variable.objects.get(name='google_analytics').value,
        'LIVEINTERNET': Variable.objects.get(name='liveinternet').value,
        'PAGERANK': Variable.objects.get(name='pagerank').value,
        'YANDEX_METRICA': Variable.objects.get(name='yandex_metrica').value,
        'YANDEX_VERIFICATION': yandex_verification,
        'GOOGLE_SITE_VERIFICATION': google_site_verification,
    }