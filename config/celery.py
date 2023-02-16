import os
from celery import Celery
from celery.schedules import crontab

# celery -A config worker -l info
# celery -A config beat -l info

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    'crawler' : {
        'task' : 'crawler.tasks.crawling_site',
        # 매 시 30분에 Run
        'schedule' : crontab(minute='30')
    }
}

app.autodiscover_tasks()