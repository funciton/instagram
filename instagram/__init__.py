import re
import functools
import requests


INSTAGRAM_API = 'https://api.instagram.com/v1'


class BaseModel(object):

    @classmethod
    def parse_from_dict(cls, data):
        return cls(**data)


class Counts(BaseModel):

    def __init__(self, media, follows, followed_by):
        self.media = media
        self.follows = follows
        self.followed_by = followed_by


class User(BaseModel):

    def __init__(self, id, username, full_name, profile_picture,
                 bio, website, counts):
        if not isinstance(counts, Counts):
            raise TypeError('Counts must be an instance of Counts model')
        self.id = id
        self.username = username
        self.full_name = full_name
        self.profile_picture = profile_picture
        self.bio = bio
        self.website = website
        self.counts = counts


class Tag(BaseModel):

    def __init__(self, label, media_count=None):
        self.label = label
        # TODO getter to request media_count if not provided
        self._media_count = media_count


class Comment(BaseModel):

    def __init__(self, id, created_time, text, _from):
        self.id = id
        self.created_time = created_time
        self.text = text

        if not isinstance(_from, User):
            raise TypeError('From must be an instance of User model')
        self._from = _from


class Image(BaseModel):

    def __init__(self, type, url, width, height):
        self.type = type
        self.url = url
        self.width = width
        self.height = height


class Video(Image):
    pass


class Caption(BaseModel):

    def __init__(self, created_time, text, _from, id):
        self.created_time = created_time
        self.text = text
        self.id = id

        if not isinstance(_from, User):
            raise TypeError('From must be an instance of User model')
        self._from = _from


class Like(BaseModel):

    def __init__(self, username, profile_picture, id, full_name):
        self.username = username
        self.profile_picture = profile_picture
        self.id = id
        self.full_name = full_name


class Location(BaseModel):

    def __init__(self, id, latitude, longitude, name):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.name = name


class Media(BaseModel):

    def __init__(self, attribution, tags, type, location, comments, filter,
                 created_time, link, likes, images, users_in_photo, caption,
                 user_has_liked, id, user, videos=None):
        self.attribution = attribution

        if not isinstance(tags, list):
            raise TypeError('Tags must be a list of Tag models')
        for tag in tags:
            if not isinstance(tag, Tag):
                raise TypeError('Tag must be an instance of Tag model')
        self.tags = tags
        self.type = type

        if not isinstance(comments, list):
            raise TypeError('Comments must be a list of Comment models')
        for comment in comments:
            if not isinstance(comment, Comment):
                raise TypeError('Comment must be an instance of Comment model')
        self.comments = comments
        self.filter = filter
        self.created_time = created_time
        self.link = link

        if not isinstance(likes, list):
            raise TypeError('Likes must be a list of Like models')
        for like in likes:
            if not isinstance(like, Like):
                raise TypeError('Like must be an instance of Like model')
        self.likes = likes

        if not isinstance(images, dict):
            raise TypeError('Images must be a dict of Image models')
        for image in images:
            if not isinstance(images.get(image), Image):
                raise TypeError('Image must be an instance of Image model')
        self.images = images

        if videos is not None:
            if not isinstance(videos, dict):
                raise TypeError('Videos must be a dict of Video models')
            for video in videos:
                if not isinstance(videos.get(video), Video):
                    raise TypeError('Video must be an instance of Video model')

        if not isinstance(users_in_photo, list):
            raise TypeError('Users in photo must be a list of User models')
        for user in users_in_photo:
            if not isinstance(user, User):
                raise TypeError('User must be an instance of User model')
        self.users_in_photo = users_in_photo

        if not isinstance(caption, Caption):
            raise TypeError('Caption must be an instance of Caption model')
        self.caption = caption

        self.user_has_liked = user_has_liked
        self.id = id

        if not isinstance(user, User):
            raise TypeError('User must be an instance of User model')
        self.user = user

        if location is not None:
            if not isinstance(location, Location):
                raise TypeError(
                    'Location must be an instance of Location model'
                )


def endpoint(uri, method='GET', api_prefix=INSTAGRAM_API,
             accept_client_id=False):
    def _endpoint(ref):
        @functools.wraps(ref)
        def wrapper(**kwargs):
            if (
                accept_client_id is True and
                kwargs.get('client_id', None) is None
            ) and kwargs.get('access_token', None) is None:
                raise RuntimeError('%saccess_token required' % (
                    'client_id or ' if accept_client_id is True else ''
                ))

            _uri = '%s%s' % (
                api_prefix,
                uri % kwargs
            )
            _uri = re.sub(r'\/+', '/', _uri)
            req = requests.request(
                method,
                _uri,
                params=kwargs
            )
            if req.status_code != 200:
                raise requests.HTTPError(404)
            return ref(req)
        return wrapper
    return _endpoint


def _parse_medias(data):
    medias = []
    for media in data:
        tags = []
        for tag in media.get('tags'):
            tag = Tag.parse_from_dict(tag)
        comments = []
        for comment in media.get('comments'):
            comment = Comment.parse_from_dict(comment)
        likes = []
        for like in likes:
            like = Like.parse_from_dict(like)
        images = {}
        for image in media.get('images'):
            images.update({
                image: Image.parse_from_dict(
                    {'type': image}.update(media.get('images').get(image)))
            })
        videos = {}
        if media.get('videos', None) is not None:
            for video in media.get('videos'):
                videos.update({
                    video: Video.parse_from_dict(
                        {'type': video}.update(media.get('videos').get(video)))
                })
        if media.get('location', None) is not None:
            media.update({
                'location': Location.parse_from_dict(media.get('location'))
            })
        caption = Caption.parse_from_dict(media.get('caption'))
        user = User.parse_from_dict(media.get('user'))
        media.update({
            'tags': tags,
            'comments': comments,
            'likes': likes,
            'images': images,
            'caption': caption,
            'user': user
        })
        medias.append(Media.parse_from_dict(media))
    return medias


@endpoint('/users/%(user_id)s')
def user_info(req):
    data = req.json().get('data')
    data.update({
        'counts': Counts.parse_from_dict(data.get('counts'))
    })
    user = User.parse_from_dict(data)
    return user


@endpoint('/users/self/feed')
def user_self_feed(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/users/%(user_id)s/media/recent', accept_client_id=True)
def user_recent_media(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/users/self/media/liked')
def user_self_liked(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/users/search')
def users_search(req):
    data = req.json().get('data')
    users = []
    for user in data:
        users.append(User.parse_from_dict(data.get(user)))
    return users


@endpoint('/media/%(media_id)s')
def media(req):
    data = req.json().get('data')
    return _parse_medias([data])[0]


@endpoint('/media/search')
def media_search(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/media/popular')
def media_popular(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/geographies/%(geo_id)s/media/recent', accept_client_id=True)
def geo_media_recent(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/locations/%(location_id)s')
def location(req):
    data = req.json().get('data')
    return Location.parse_from_dict(data)


@endpoint('/locations/%(location_id)s/media/recent')
def location_media_recent(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/locations/search')
def location_search(req):
    data = req.json().get('data')
    locations = []
    for location in data:
        locations.append(Location.parse_from_dict(location))
    return locations


@endpoint('/tags/%(tag_name)s')
def tag(req):
    data = req.json().get('data')
    return Tag.parse_from_dict(data)


@endpoint('/tags/%(tag_name)s/media/recent')
def tags_media_recent(req):
    data = req.json().get('data')
    return _parse_medias(data)


@endpoint('/tags/search')
def tags_search(req):
    data = req.json().get('data')
    tags = []
    for tag in data:
        tags.append(Tag.parse_from_dict(tag))
    return tags


@endpoint('/media/%(media_id)s/comments')
def media_comments(req):
    data = req.json().get('data')
    comments = []
    for comment in data:
        comments.append(Comment.parse_from_dict(data.get(comment)))
    return comments


@endpoint('/media/%(media_id)s/comments', method='POST')
def post_media_comment(req):
    data = req.json()
    return True if data.get('meta').get('code') == 200 else False


@endpoint('/media(%(media_id)s/comments/%(comment_id)s', method='DELETE')
def delete_media_comment(req):
    data = req.json()
    return True if data.get('meta').get('code') == 200 else False


@endpoint('/media/%(media_id)s/likes')
def media_likes(req):
    data = req.json().get('data')
    likes = []
    for like in data:
        likes.append(Like.parse_from_dict(data.get(like)))
    return likes


@endpoint('/media/%(media_id)s/likes', method='POST')
def post_media_like(req):
    data = req.json()
    return True if data.get('meta').get('code') == 200 else False


@endpoint('/media(%(media_id)s/likes', method='DELETE')
def delete_media_like(req):
    data = req.json()
    return True if data.get('meta').get('code') == 200 else False
