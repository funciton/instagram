python Instagram lib
=====================

This library implements Instagram endpoints (read-only for now).

It uses `python-requests <http://python-requests.org>`_ lib internally.


Usage
-----

Library contains an @endpoint decorator in case you want to create your
own handler::

    @endpoint('/media/popular')
    def my_method(req):
        # req argument is an instance of python-request
        print req.text  # return request body as text
        print req.json()  # return request body as json object


In case you prefer to use a built-in handler here is the list of them:

- user_info
- user_self_feed
- user_recent_media
- user_self_liked
- users_search
- media
- media_search
- media_popular
- geo_media_recent
- location
- location_media_recent
- location_search
- tag
- tags_media_recent
- tags_search
- media_comments
- post_media_comment
- delete_media_comment
- post_media_like
- delete_media_like


client_id, access_token or uri data should be passed as kwargs, ex::

    from instagram import user_info

    user = user_info(user_id=1574083, access_token='...')


Built-in endpoint handlers return class models. Example above will
return a User class model (check source code or instagram docs for model
properties)


Validation
----------

@endpoint decorator handles access_token validation by default. In case
client_id could be used, pass 'accept_client_id=True' to the @endpoint
decorator.

In case a kwarg is required for uri building but not specified it will
raise a KeyError exception.


Note
----

Still needs unit testing. Plz fork!
