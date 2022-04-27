import random

import requests
from dataclasses import dataclass
from json import JSONDecodeError

from .methods import VkApiMethods
from ..required_params import check_params


@dataclass
class VkApiResponse:
    """Типизация возращаемых значений для методов :class:`VkApi`.

    Attributes:
        body (dict): Тело ответа.
        status_code (int): Код статуса ответа.
    """
    body: dict
    status_code: int


class VkApi:
    """Представление взаимодействия с Api VK.

    Attributes:
        token (str): Токен пользователя.
        owner_id (int): ID страницы для взаимодействия (ID сообществ должен передаваться со знаком "-").
    """

    def __init__(self, owner_id: str, token: str, group_token: str = None, **kwargs):
        self.token = token
        self.owner_id = owner_id
        self.group_token = group_token

    def _get_url(self, api_method: str, params: dict):
        """Метод получения валидного url для отправки запроса.

        Args:
            api_method (str): Метод Api VK.
            params (dict): Параметры запроса.

        Returns:
            url (str): Url запроса.
        """
        p = params.copy()
        if api_method.startswith('messages') or api_method.startswith('groups'):
            token = self.group_token
        else:
            token = self.token
        p.update({
            'owner_id': self.owner_id,
            'access_token': token,
            'v': VkApiMethods.version,
            **params
        })
        url = VkApiMethods.get_url(api_method, p)

        return url

    def _send_api_request(self, api_method: str, params: dict):
        """Метод отправки запроса к Api VK.

        Args:
            api_method (str): Метод Api VK.
            params (dict): Параметры запроса.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.
        """

        if not VkApiMethods.has_method(api_method):
            return VkApiResponse(
                {'response': {
                    'error': 'Метод не существует'
                }},
                404
            )

        url = self._get_url(api_method, params=params)
        response = requests.request(
            method=VkApiMethods.get_http_method(api_method),
            url=url
        )
        try:
            response_body = response.json()
        except JSONDecodeError:
            return VkApiResponse(
                {'response': {
                     'error': 'Сервер не вернул валидный json.'
                }},
                502
            )

        return VkApiResponse(response_body, response.status_code)

    def get_posts(self, params: dict):
        """Метод получения постов.

        Args:
            params:

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_POSTS, params=params)

    @check_params(or_params=(('message', 'attachments'),))
    def publish_post(self, params: dict) -> VkApiResponse:
        """Метод для публикации поста.

        Args:
            params (dict): Параметры запроса. для публикации (см. https://vk.com/dev/wall.post).
                Обязательно должен содержать как минимум один из параметров ``message``, ``attachments``.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.PUBLISH_POST, params=params)

    @check_params(required_params=('post_id',))
    def delete_post(self, params: dict) -> VkApiResponse:
        """
        Метод для удаления поста.

        Args:
            params (dict): Параметры запроса (см. https://vk.com/dev/wall.getComment).
                Обязательно должен содержать ``post_id``.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.DELETE_POST, params=params)

    @check_params(required_params=('post_id',))
    def get_comment(self, params: dict) -> VkApiResponse:
        """Метод для получения комментария.

        Args:
            params (dict): Параметры запроса (см. https://vk.com/dev/wall.getComment).
                Обязательно должен содержать ``post_id``.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_COMMENT, params=params)

    @check_params(or_params=(('post_id', 'comment_id'),))
    def get_comments(self, params: dict) -> VkApiResponse:
        """Метод для получения комментариев по ветке или по посту.

        Args:
            params (dict): Параметры запроса для получения комментариев (см. https://vk.com/dev/wall.getComments).
                Обязательно должен содержать как минимум один из параметров ``post_id``, ``comment_id``.
        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_COMMENTS, params=params)

    @check_params(required_params=('post_id',))
    def create_comment(self, params: dict) -> VkApiResponse:
        """Метод отправки комментария.

        Args:
            params (dict): Параметры запроса для отправки комментария (см. https://vk.com/dev/wall.createComment).
                Обязательно должен содержать ``post_id``.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.CREATE_COMMENT, params=params)

    def get_conversations(self, params: dict) -> VkApiResponse:
        """Метод получения бесед.

        Args:
            params (dict): Параметры запроса для получения бесед (см. https://vk.com/dev/messages.getConversations).

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_CONVERSATIONS, params=params)

    @check_params(or_params=(('user_id', 'peer_id'),))
    def get_history(self, params: dict) -> VkApiResponse:
        """Метод получения истории сообщений.

        Args:
            params (dict): Параметры запроса для получения истории беседы (см. https://vk.com/dev/messages.getHistory).
                Обязательно должен содержать как минимум один из параметров ``user_id``, ``peer_id``.

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_HISTORY, params=params)

    @check_params(or_params=(('peer_ids', 'peer_id', 'user_id'), ('message', 'attachment')))
    def send_message(self, params: dict) -> VkApiResponse:
        """Метод отправки сообщения.

        Args:
            params: Параметры запроса для отправки сообщения (см. https://vk.com/dev/messages.send).
                Обязательно должен содержать как минимум один из параметров (``user_id``, ``peer_id``),
                (``message``, ``attachment``).

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        params['random_id'] = random.randint(1, 2**31-1)

        return self._send_api_request(VkApiMethods.SEND_MESSAGE, params=params)

    @check_params(required_params=('users_id',))
    def get_users_info(self, params: dict) -> VkApiResponse:
        """Метод получения информации о конкретных пользователях.

        Args:
            params: Параметры запроса для отправки сообщения (см. https://vk.com/dev/users.get).
                Обязательно должен содержать ``user_ids``

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.

        """

        return self._send_api_request(VkApiMethods.GET_USERS_INFO, params=params)

    @check_params(required_params=('group_id',))
    def upload_photo(self, params: dict) -> VkApiResponse:
        """
        Метод получения ссылки для загрузки мзображения на сервер VK.

        Args:
            params: Параметры запроса для получения ссылки (см. https://dev.vk.com/method/photos.getWallUploadServer).
                Обязательно должен содержать ``group_id``

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.
        """
        return self._send_api_request(VkApiMethods.UPLOAD_PHOTO, params=params)

    @check_params(required_params=('group_id', 'server', 'photo', 'hash',))
    def save_photo(self, params: dict) -> VkApiResponse:
        """
        Метод сохранения изображения в группе VK.

        Args:
            params: Параметры запроса для сохранения изображения (см. https://dev.vk.com/method/photos.saveWallPhoto).
                Обязательно должен содержать ``group_id``, ``server``, ``photo``, ``hash``
                Значения этих параметров необходимо взять из ответа после вызова функции upload_photo()

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.
        """
        return self._send_api_request(VkApiMethods.SAVE_PHOTO, params=params)

    @check_params(required_params=('group_id',))
    def save_video(self, params: dict) -> VkApiResponse:
        """
        Метод получения ссылки для загрузки видео в группу VK.

        Args:
            params: Параметры запроса для получения ссылки (см. https://dev.vk.com/method/video.save).
                Обязательно должен содержать ``group_id``

        Returns:
            :obj:`VkApiResponse`: Возвращает объект с телом и кодом ответа.
        """
        return self._send_api_request(VkApiMethods.SAVE_VIDEO, params=params)

    def get_callback_confirmation_code(self, params: dict) -> VkApiResponse:
        params['group_id'] = self.owner_id.strip('-')

        return self._send_api_request(VkApiMethods.GET_CALLBACK_CONFIRMATION_CODE, params=params)

    @check_params(required_params=('url', 'title', 'secret_key'))
    def add_callback_server(self, params: dict):
        params['group_id'] = self.owner_id.strip('-')

        return self._send_api_request(VkApiMethods.ADD_CALLBACK_SERVER, params=params)

    def get_callback_servers(self, params: dict):
        params['group_id'] = self.owner_id.strip('-')

        return self._send_api_request(VkApiMethods.GET_CALLBACK_SERVERS, params=params)
