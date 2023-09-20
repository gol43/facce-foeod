from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from django.core.validators import validate_slug

name_validator = RegexValidator(
    regex=r'^[a-zA-Zа-яА-Я]+$',
    message=_("Используйте только буквы."),
)


def validate_username(value):
    if value.lower() == 'me':
        raise ValidationError('Нельзя использовать "me" в качестве username.')


class User(AbstractUser):
    email = models.EmailField(max_length=254,
                              unique=True)
    username = models.CharField(max_length=150,
                                unique=True,
                                validators=[validate_slug, validate_username])
    first_name = models.CharField(max_length=150,
                                  blank=False,
                                  null=False,
                                  validators=[name_validator])
    last_name = models.CharField(max_length=150,
                                 blank=False,
                                 null=False,
                                 validators=[name_validator])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", 'first_name', 'last_name',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    def __str__(self):
        return f'Пользователь {self.user} -> автор {self.author}'
