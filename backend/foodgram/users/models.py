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


class User(AbstractUser):
    email = models.EmailField(max_length=254,
                              unique=True)
    username = models.CharField(max_length=150,
                                unique=True,
                                validators=[validate_slug])
    first_name = models.CharField(max_length=150,
                                  blank=True,
                                  null=True,
                                  validators=[name_validator])
    last_name = models.CharField(max_length=150,
                                 blank=True,
                                 null=True,
                                 validators=[name_validator])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", 'first_name', 'last_name',)

    def clean(self):
        super().clean()
        if not self.first_name and not self.last_name:
            raise ValidationError({"first_name": _("Обязательное поле."), "last_name": _("Обязательное поле.")})

        if self.username == "me":
            raise ValidationError({"username": _("Username не может быть 'me'."),})


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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
