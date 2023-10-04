import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

username_validator = UnicodeUsernameValidator()


def validate_username(value):
    """Функция-валидатор проверяет корректность username."""
    if value.lower() == "me":
        raise ValidationError(
            'Имя "me" не разрешено для использования.'
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Недопустимые символы <{value}> в имени пользователя.'),
            params={'value': value},
        )
