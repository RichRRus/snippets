from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import Optional


class MissingParams(Exception):
    pass


class BaseCheck(metaclass=ABCMeta):
    """Базовый класс для классов проверки.

    Метод __init__ принимает ``**parameters``.
    В этом атрибуте должны содержаться обязательные параметры под ключом, который задаётся для наследуемых классов
    путём расширения метода __init__ (например ``self.required_parameters = parameters.get('required_parameters')``).

    Attributes:
        params (Iterable): Параметры для проверки.

    """

    def __init__(self, params, **parameters):
        self.params = params or ()
        self.__errors = []
        self._error_status_code = 400

    @property
    def errors(self) -> tuple:
        """
        tuple: Ошибки, возникшие при проверке параметров.

        """
        return tuple(self.__errors)

    @errors.setter
    def errors(self, val):
        self.__errors.append(val)

    @property
    def error_message(self) -> str:
        """
        str: Сообщение об ошибке.

        """
        raise NotImplemented()

    @property
    def error_status_code(self) -> int:
        """
        int: Код ошибки.

        """
        return self._error_status_code

    @error_status_code.setter
    def error_status_code(self, val: int):
        self._error_status_code = val

    @abstractmethod
    def _check_param(self, **kwargs) -> bool:
        """Метод проверки параметра.
        Допустимо использование без дополнительных аргументов.

        Args:
            **kwargs: Почти во всех случаях передаваться конкретный параметр.

        Returns:
            bool: True если параметр прошёл проверку, иначе False

        """
        pass

    @abstractmethod
    def check_params(self) -> Optional[tuple]:
        """Метод проверки параметров.

        Returns:
            tuple (optional): Кортеж с ошибками.
            В большинстве случаев кортеж должен содержать строковые значения.
            Если все параметры прошли проверку, следует передать None.

        """
        pass


class RequiredParamsCheck(BaseCheck):
    """Класс для проверки наличия всех аргументов, переданных в ``parameters['required_params'].

    """

    error_message = 'Отсутствует обязательный параметр {}'

    def __init__(self, params, **parameters):
        super().__init__(params, **parameters)
        self.required_params = parameters.get('required_params')

    def _check_param(self, required_param) -> bool:
        if required_param in self.params:
            return True
        return False

    def check_params(self):
        if not self.required_params:
            return None
        for required_param in self.required_params:
            if not self._check_param(required_param):
                self.errors = self.error_message.format(required_param)
        return self.errors


class OrParamsCheck(BaseCheck):
    """Класс для проверки наличия хотя бы одного аргумента из переданных в ``parameters['or_params']``.
    ``parameters['or_params']`` должен соответствовать типу Iterable[Iterable].

    """

    error_message = 'Отсутвтвует как минимум один из обязательных параметров {}'

    def __init__(self, params, **parameters):
        super().__init__(params=params, **parameters)
        self.or_params = parameters.get('or_params')

    def _check_param(self, or_params) -> bool:
        return any(param in self.params for param in or_params)

    def check_params(self) -> Optional[tuple]:
        if not self.or_params:
            return None
        for or_params in self.or_params:
            if not self._check_param(or_params):
                self.errors = self.error_message.format(', '.join(or_params))
                print(f'{self.errors=}')
        return self.errors


def check_params(**parameters):
    """Декоратор для проверки аргументов.

    Args:
        **parameters: В это аргументе должны быть переданны итерируемые объекты, состоящие из аргументов.
            Каждый объект передаётся под своим ключом.
            В зависимости от ключа аргументы попадут только под определённую проверку (см. :class:`BaseCheck`).

    """
    def inner_function(func):
        def set_errors(params):
            """Получение ошибок по параметрам.

            Args:
                params: Параметры для проверки.

            Returns:
                tuple (optional): Список ошибок. При их отсутствии возвращается пустой список.

            """
            errors = []
            for checker_cls in BaseCheck.__subclasses__():
                if e := checker_cls(params, **parameters).check_params():
                    errors.extend(e)
            return errors

        @wraps(func)
        def wrapper(*args, **kwargs):
            """

            Raises:
                MissingParams: Если в параметры не прошли проверку.

            """
            errors = set_errors(kwargs.get('params'))
            if errors:
                raise MissingParams(errors)
            return func(*args, **kwargs)
        return wrapper

    return inner_function
