from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True,
                                validators=[validate_slug])
    first_name = models.CharField(max_length=150, blank=True,
                                  null=True, validators=[validate_slug])
    last_name = models.CharField(max_length=150, blank=True,
                                 null=True, validators=[validate_slug])

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = (
        "username",
        'first_name',
        'last_name',
    )

    def save(self, *args, **kwargs):
        if self.first_name and not self.first_name.isalpha():
            raise ValidationError("First name должно содержать только буквы.")
        if self.last_name and not self.last_name.isalpha():
            raise ValidationError("Last name должно содержать только буквы.")
        if self.username == "me":
            raise ValidationError("Username не может быть 'me'.")
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
