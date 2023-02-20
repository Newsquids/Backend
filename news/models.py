from django.db import models

# Create your models here.

class NewsChannel(models.Model):
    id = models.SmallAutoField(primary_key=True, auto_created=True)
    channel_name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "news_channel"

class NewsCategory(models.Model):
    id = models.SmallAutoField(primary_key=True, auto_created=True)
    category_name = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "news_category"

class News(models.Model):
    link = models.CharField(max_length=300, unique=True)
    headline = models.CharField(max_length=300)
    image = models.CharField(max_length=300, null=True, blank=True)
    create_time = models.DateTimeField()
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_DEFAULT, related_name='category', default=-1)
    channel = models.ForeignKey(NewsChannel, on_delete=models.SET_DEFAULT, related_name='channel', default=-1)

    class Meta:
        db_table = "news"