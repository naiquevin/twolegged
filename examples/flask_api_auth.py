"""Module that handles API authentication (simple 2 legged auth) in
Flask

"""

from functools import wraps

from flask import request
from werkzeug.exceptions import Unauthorized

import app
from twolegged import validate_request, InvalidRequest, Request


## for the sake of a simple example, the consumer credentials will
## be loaded from a file
def load_consumers():
    with open(app.config['AUTH_API_CONSUMERS_FILE']) as f:
        lines = (map(unicode, x.strip().split(':')) for x in f)
        return [{u'key': key, u'secret': secret} for key, secret in lines]


## consumer credentials are loaded and kept in memory
_consumers = load_consumers()


## This function will be passed as the `consumer_getter` argument to
## `validate_request`
def get_consumer(key):
    """Gets a consumer by it's key

    :param key : string
    :rtype     : dict with two fields: `key` and `secret`

    """
    try:
        return [c for c in _consumers if c['key'] == key][0]
    except IndexError:
        return None


## This class implements the twolegged.Request interface and will wrap
## the Flask request object
class FlaskRequest(Request):
    """Class to wrap the Flask request object in another object with an
    interface that the twolegged auth functions recognize

    """

    def __init__(self, req):
        self._req = req

    def base_url(self):
        ## Flask provides the base_url as an attribute of the request,
        ## so we can just return that
        return self._req.base_url

    def method(self):
        return unicode(self._req.method)

    def headers(self):
        return self._req.headers

    def params(self):
        return self._req.args.lists()

    def form_data(self):
        return self._req.form.lists()

    def values(self):
        return self._req.values


def protect_api(f):
    """View decorator to protect the API endpoint at decorated view

    :param f : function
    :rtype   : function

    """
    # allow in debug mode
    if app.config['DEBUG']:
        return f

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            if validate_request(FlaskRequest(request), consumer_getter=get_consumer):
                return f(*args, **kwargs)
            raise Unauthorized('Invalid request')
        except InvalidRequest as e:
            raise Unauthorized(e)
    return decorated
