import requests
import urllib.parse
from abc import ABCMeta


class VkApiMethodsBase(metaclass=ABCMeta):

    @property
    def base_url(self) -> str:
        raise NotImplemented()

    @property
    def version(self) -> str:
        raise NotImplemented()

    @property
    def __http_methods(self) -> dict:
        raise NotImplemented()


class VkApiMethods(VkApiMethodsBase):
    base_url = 'https://api.vk.com/method/'
    version = '5.131'

    CREATE_COMMENT = 'wall.createComment'
    GET_COMMENT = 'wall.getComment'
    GET_COMMENTS = 'wall.getComments'
    GET_LIKES = 'wall.getLikes'
    GET_REPOSTS = 'wall.getReposts'
    GET_CONVERSATIONS = 'messages.getConversations'
    GET_HISTORY = 'messages.getHistory'
    GET_POSTS = 'wall.get'
    GET_USERS_INFO = 'users.get'
    PUBLISH_POST = 'wall.post'
    DELETE_POST = 'wall.delete'
    SEND_MESSAGE = 'messages.send'
    GET_CALLBACK_CONFIRMATION_CODE = 'groups.getCallbackConfirmationCode'
    ADD_CALLBACK_SERVER = 'groups.addCallbackServer'
    GET_CALLBACK_SERVERS = 'groups.getCallbackServers'
    UPLOAD_PHOTO = 'photos.getWallUploadServer'
    SAVE_PHOTO = 'photos.saveWallPhoto'
    SAVE_VIDEO = 'video.save'

    __http_methods = {
        CREATE_COMMENT: 'POST',
        GET_COMMENT: 'GET',
        GET_COMMENTS: 'GET',
        GET_LIKES: 'GET',
        GET_REPOSTS: 'GET',
        GET_CONVERSATIONS: 'GET',
        GET_HISTORY: 'GET',
        GET_POSTS: 'GET',
        GET_USERS_INFO: 'GET',
        PUBLISH_POST: 'POST',
        DELETE_POST: 'POST',
        SEND_MESSAGE: 'POST',
        GET_CALLBACK_CONFIRMATION_CODE: 'GET',
        ADD_CALLBACK_SERVER: 'POST',
        GET_CALLBACK_SERVERS: 'GET',
        UPLOAD_PHOTO: 'POST',
        SAVE_PHOTO: 'POST',
        SAVE_VIDEO: 'POST',
    }

    @classmethod
    def get_http_method(cls, rpc_method) -> str:
        return cls.__http_methods.get(rpc_method)

    @classmethod
    def has_method(cls, method) -> bool:
        return method in cls.__http_methods

    @classmethod
    def get_url(cls, method, params) -> str:
        url = urllib.parse.urljoin(cls.base_url, method)
        if not url.endswith('/'):
            url += '/'
        req = requests.models.PreparedRequest()
        req.prepare_url(url, params)
        url = req.url
        return url
