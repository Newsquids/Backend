from django.db import models

# Create your models here.

class NewsChannel(models.Model):
    id = models.SmallAutoField(primary_key=True)
    channel_name = models.CharField(max_length=30)

    class Meta:
        db_table = "news_channel"

class News(models.Model):
    link = models.CharField(max_length=300)
    headline = models.CharField(max_length=300)
    image = models.CharField(max_length=300, null=True, blank=True)
    time = models.DateTimeField()
    channel = models.ForeignKey(NewsChannel, on_delete=models.SET_DEFAULT, related_name='channel')

    class Meta:
        db_table = "news"