from requests.models import RequestEncodingMixin
from oauthlib.oauth1.rfc5849.utils import (parse_authorization_header,
                                           unescape)
from oauthlib.oauth1.rfc5849.signature import (collect_parameters,
                                               normalize_parameters,
                                               normalize_base_string_uri,
                                               construct_base_string,
                                               sign_hmac_sha1)


def validate_request(request, consumer_getter):
    headers = request.headers()
    auth_header = headers.get('Authorization')
    request_values = request.values()
    if auth_header:
        authorization = dict(parse_authorization_header(auth_header))
        key = authorization['oauth_consumer_key']
        signature = unescape(authorization['oauth_signature'])
    else:
        key = request_values.get('oauth_consumer_key', None)
        signature = request_values.get('oauth_signature', None)

    if key is None or signature is None:
        raise InvalidRequest((
            "Failed to authenticate since necessary parameters were not supplied"
        ))

    consumer = consumer_getter(key)
    if consumer is None:
        raise InvalidRequest('Consumer not found')
    return build_signature(request, consumer['secret']) == unescape(signature)


def build_signature(request, consumer_secret):
    headers = request.headers()
    auth_headers = {k: v for k, v in headers.iteritems() if k == 'Authorization'}
    body = request.form_data()
    params = [(k, v) for k, v in request.params() if k != 'oauth_signature']
    qs = RequestEncodingMixin._encode_params(params)
    collected_params = collect_parameters(qs, body, auth_headers)
    normalized_params = normalize_parameters(collected_params)
    host = headers.get('Host', None)
    normalized_uri = normalize_base_string_uri(request.base_url(), host)
    base_string = construct_base_string(unicode(request.method()),
                                        normalized_uri,
                                        normalized_params)
    return sign_hmac_sha1(base_string, consumer_secret, None)


class Request(object):

    def base_url(self):
        """Base URL of the request

        :rtype : string

        """
        raise NotImplementedError

    def method(self):
        """Request method

        :rtype : unicode

        """
        raise NotImplementedError

    def headers(self):
        """Requests headers

        :rtype : dict like object

        """
        raise NotImplementedError

    def params(self):
        """GET parameters

        :rtype : dict like object

        """
        raise NotImplementedError

    def form_data(self):
        """POST data

        :rtype : dict like object

        """
        raise NotImplementedError

    def values(self):
        """Combined POST and GET data

        :rtype : dict like object

        """
        raise NotImplementedError


class InvalidRequest(Exception):
    pass
