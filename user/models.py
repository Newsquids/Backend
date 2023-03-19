import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from user.manager import UserManager
from news.models import News
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class User(AbstractUser):
    objects = UserManager()
    id = models.UUIDField(auto_created=True, unique=True, primary_key=True, default=uuid.uuid4)
    email = models.EmailField(
        unique=True,
        max_length=100
    )

    username, last_login, first_name, last_name = (None,None,None,None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'user'
    
class UserDetail(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, related_name='detail')
    username = models.CharField(max_length=100)
    gender = models.BooleanField(null=True, blank=False)

    class Meta:
        db_table = 'user_detail'

class UserBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='news')

    class Meta:
        db_table = 'user_bookmark'