import re

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

username_validator = UnicodeUsernameValidator()


def validate_color(value):
    """Проверяет цвет тега на соответствие hex-color."""
    reg = re.compile(r'^#([a-f0-9]{6}|[A-F0-9]{6})$')
    if not reg.match(value):
        raise ValidationError(
            'Введите правильный 6-значный код hex-color в одном регистре.'
        )
