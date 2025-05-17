from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskapp.settings')

app = Celery('taskapp')

# Загрузка конфигурации Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическая регистрация задач из всех установленных приложений
app.autodiscover_tasks()
