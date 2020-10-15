from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token


class CustomModelBase(models.base.ModelBase):
    def __new__( cls, name, bases, attrs, **kwargs ):
        if name != "CustomModel":
            class MetaB:
                db_table = "" + name.lower()

            attrs["Meta"] = MetaB

        return super().__new__( cls, name, bases, attrs, **kwargs )

class CustomModel(models.Model, metaclass=CustomModelBase):
    class Meta:
        abstract = True

# ===================================================
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(CustomModel, AbstractBaseUser):
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=254, null=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now=True)
    group = models.ForeignKey('Group', on_delete=models.PROTECT, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def has_perm_page(self, page):
        return True if (self.group and page in self.group.permission_page) or (self) else False

    @property
    def token(self):
        return Token.objects.get(user_id=self)

class Group(CustomModel):
    name = models.CharField(max_length=254)
    permission_page = models.TextField(null=True)

class Trend(CustomModel):
    name = models.CharField(max_length=254)
    site = models.CharField(max_length=254, null=True)
    type = models.CharField(max_length=254, null=True)

class Interest(CustomModel):
    trend = models.ForeignKey('Trend', on_delete=models.PROTECT, null=True)
    pull_datetime = models.DateTimeField()
    pull_value = models.FloatField()
    pull_type = models.CharField(max_length=100)