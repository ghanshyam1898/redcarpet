import secrets

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from accounts.password_utils import make_password


# We cannot inherit AbstractUser provided by Django because we want our own password hashing function
class User(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_AGENT = "agent"
    ROLE_CUSTOMER = "customer"
    ALL_ROLES = (ROLE_ADMIN, ROLE_AGENT, ROLE_CUSTOMER,)

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=(
        (ROLE_ADMIN, ROLE_ADMIN,),
        (ROLE_AGENT, ROLE_AGENT,),
        (ROLE_CUSTOMER, ROLE_CUSTOMER,),
    ))

    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)

    @staticmethod
    def create_user(**kwargs):

        kwargs['password'] = make_password(kwargs['password'])
        return User.objects.create(**kwargs)

    @staticmethod
    def get_user_by_token(request):
        if "Authorization" in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            try:
                return AuthToken.objects.get(token=token).user
            except AuthToken.DoesNotExist:
                return None
        else:
            return None

    @staticmethod
    def get_or_create_user(**kwargs):
        try:
            return User.objects.get(username=kwargs['username'])
        except User.DoesNotExist:
            return User.create_user(**kwargs)


class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128)

    @staticmethod
    def get_or_create_token(user):
        try:
            return AuthToken.objects.get(user=user).token
        except AuthToken.DoesNotExist:
            object = AuthToken(
                user=user,
                token=secrets.token_urlsafe(32)
            )
            object.save()
            return object.token
