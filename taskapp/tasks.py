from celery import shared_task
from django.core.mail import send_mail
from .models import Reminder
from datetime import datetime

@shared_task
def send_reminders():
    reminders = Reminder.objects.filter(date_of_remind__lte=datetime.now())
    for reminder in reminders:
        if reminder.type_of_remind == 'Email':
            send_mail(
                'Напоминание о задаче',
                f'Напоминаем о задаче {reminder.task_id}.',
                'noreply@example.com',
                [reminder.task.user.email]  # Предполагается, что в задаче есть пользователь
            )
        elif reminder.type_of_remind == 'Push':
            # Логика отправки push-уведомлений
            pass
