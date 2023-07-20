from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (BaseUserManager, PermissionsMixin)
from django.db import models
from django.core import validators


class UserManager(BaseUserManager):

    def create_user(self, email, name, password):

        if email is None:
            raise TypeError('email is missing')

        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, name, password):

        if email is None:
            raise TypeError('email is missing')

        if password is None:
            raise TypeError('password is missing')

        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(
        "Full name", max_length=255, blank=False, null=False)

    email = models.EmailField(unique=True)

    verify_token = models.CharField(max_length=225, blank=True, null=False)

    email_verified = models.BooleanField(default=False)

    password = models.CharField(max_length=128, blank=True, null=False, validators=[
        validators.RegexValidator(
            regex='^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{8,}$',
            message='Please enter a strong password'
        )
    ])

    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField("Created At", auto_now_add=True)

    updated_at = models.DateTimeField("Updated At", auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __st__(self):

        return self.email
