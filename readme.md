python Instagram API (under development)
=========================================

Needed to use instagram python lib but didn't like it nor it is actively maintained (doesn't support video medias for example).

This lib is based on [python-requests](http://www.python-requests.org/en/latest/) awesome lib.

Full API is implemented but still requires extra work.

Implemented methods return models.

Method list
------------

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


*Current validation is not on the lib (yet)*


Endpoint decorator
-------------------

```python
from instagram import endpoint

@endpoint('/v1/media/popular')
def my_method(req):
    # req is a request
    print req.text  # return request body as text
    print req.json()  # return request body as json object
```


TODO
-----

- Implement param validation
- Include a tool to get access_token
- Unit tests


Help needed! Plz fork!

Credits
--------

funciton
url: [http://funciton.com](http://funciton.com)
email: info AT funciton.com
