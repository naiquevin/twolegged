import re
from functools import wraps

from twolegged import validate_request, Request, InvalidRequest
from django.http import HttpResponse
from django.conf import settings


## This function will be passed as the `consumer_getter` argument to
## `validate_request`. This example assumes that the consumers key and
## secret are specified in a list of dicts in DJANGO settings. But you
## can replace this with pretty much any other method
def get_consumer(key):
    """Gets a consumer by it's key

    :param key : string
    :rtype     : dict with two fields: `key` and `secret`

    """
    try:
        return [c for c in settings.API_CONSUMERS
                if c['key'] == key][0]
    except IndexError:
        return None


## This class implements the twolegged.Request interface and will wrap
## the Django request object
class DjangoRequest(Request):

    HTTP_HEADER_REGEX = re.compile('^HTTP_')

    def __init__(self, req):
        self._req = req

    def base_url(self):
        return unicode(self._req.build_absolute_uri())

    def method(self):
        return unicode(self._req.method)

    def headers(self):
        ## From django docs:
        ##
        ## With the exception of CONTENT_LENGTH and CONTENT_TYPE, as
        ## given above, any HTTP headers in the request are converted
        ## to META keys by converting all characters to uppercase,
        ## replacing any hyphens with underscores and adding an HTTP_
        ## prefix to the name. So, for example, a header called
        ## X-Bender would be mapped to the META key HTTP_X_BENDER.
        ##
        f = lambda x: unicode(self.HTTP_HEADER_REGEX.sub('', x).title().replace('_', '-'))
        return {f(k): unicode(v)
                for k, v in self._req.META.iteritems()
                if k.startswith(('HTTP_', 'CONTENT_'))}

    def params(self):
        return self._req.GET.lists()

    def form_data(self):
        return self._req.POST.lists()

    def values(self):
        return self._req.REQUEST


def protect_api(f):
    """View decorator to protect the API endpoint at decorated view

    :param f : function
    :rtype   : function

    """
    ## allow in debug mode
    if settings.DEBUG:
        return f

    @wraps(f)
    def decorated(request, *args, **kwargs):
        try:
            if validate_request(DjangoRequest(request), consumer_getter=get_consumer):
                return f(request, *args, **kwargs)
            return HttpResponse('Unauthorized', status=401)
        except InvalidRequest as e:
            return HttpResponse('Unauthorized: {}'.format(e), status=401)
        except Exception as e:
            print e
    return decorated
