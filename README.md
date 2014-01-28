Twolegged
=========

**Important Note: Project under WIP!**

A framework agnostic library for implementing two-legged
authentication to secure internal APIs by verifying signed requests
using a key and a shared secret.


Why?
----

I was looking for something better than
[Security through obscurity](http://en.wikipedia.org/wiki/Security_through_obscurity)
to secure internal RESTful APIs without the need for,

1. users to grant access to the client (as the data is not tied to
   resource owners).
2. the clients to obtain temporary access tokens (as in case of
   "Client Credentials Auth Flow" of Oauth 2.0) from the server as
   both servers and clients are entirely controlled by us.

Since I was working with Flask, the first thing I tried was
[Flask-oauthlib](https://flask-oauthlib.readthedocs.org/en/latest/)
which supports three-legged OAuth 1 flow and it was quite tricky to
fit a simple two-legged flow into it. So, I wrote a couple of
functions to verify a signed request using existing libraries.


Dependencies
------------

* [oauthlib](https://github.com/idan/oauthlib)
* [requests](http://docs.python-requests.org/en/latest/)

Usage
-----

Let's first briefly understand the flow before getting to the usage:

1. The client/consumer will sign the request (HMAC-SHA1 method) with a
   key-secret pair that the server also knows. The key is included in
   the request headers whereas the secret is never sent to the other
   side.
2. The provider will identify the client from the key and use it's
   secret to verify the signed request.

We will get to point 1 later. For point 2, all that's required is a
call to the function ``twolegged.validate_request`` which abstracts
away the verfication of the request.

``validate_request`` takes two arguments:

- First, a request object that implements the interface defined by
  ``twolegged.Request`` class. The easiest way to do this is to
  subclass this class and implement
  [all the methods](https://github.com/naiquevin/twolegged/blob/master/twolegged/__init__.py#L74)
  that raise ``NotImplementedError`` to wrap the request object
  provided by whichever web framework you are using with this
  interface eg. the thread local Flask request object or the Django
  request object passed as an arg to the views. This way, the lib can
  be used with any framework.
- Second, a function (``consumer_getter``) that takes a string which
  is the ``key`` or the unique identifier of the consumer. The job of
  this function is to use the identifier to lookup a consumer from
  whichever storage your application might be using eg. relational
  database, a text file etc. and return a dict with the fields "key"
  and "secret". If a consumer with the given key is not found, it
  should return ``None``

See the example implementation for Flask in
``examples/flask_api_auth.py`` which loads the consumer info from a
file. A decorator ``protect_api`` is also included that can be applied
to the views. Similar Request object wrapper, consumer_getter function
and decorator can be implemented for Django or any other framework for
that matter.

Ok, so now that the api endpoints are protected, on the client side
(point 1), we would now need to sign requests so that the provider
accepts them. For this, we can use the
[requests-oauthlib](https://github.com/requests/requests-oauthlib)
library by specifying both the resource owner key and secret as
``None``. An example can be found in ``examples/client.py``


Todo
----

1. Add example for Django
2. Write tests


Caveat
------

This method assumes that both the client and server can permanently
store a key-secret pair at their end and so it's best suited for
communication between a backend server and a front app
server. **DONOT** use this method if your application resides on the
user's device/machine or the source code is distributed to the users
which might cause the secret to be exposed. In that case, the Client
credentials flow of OAuth 2.0 might help.


License
-------

MIT
