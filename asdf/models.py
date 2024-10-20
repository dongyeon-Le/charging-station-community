from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone

class Users(AbstractBaseUser):
    user_id = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 50)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=250)
    address_detail = models.CharField(max_length=250)

    USERNAME_FIELD = 'user_id'


class Posts(models.Model):
    connected_user = models.ForeignKey(Users, on_delete = models.CASCADE, related_name = 'posts')
    title = models.CharField(max_length = 50)
    content = models.TextField()
    author = models.CharField(max_length = 50, default = "")
    location = models.TextField()
    location_detail = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # 작성일자
    image = models.ImageField(upload_to='images/', blank=True, null=True)  # 이미지 파일 업로드


class Comment(models.Model):
    connected_post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # 댓글 작성 시간

