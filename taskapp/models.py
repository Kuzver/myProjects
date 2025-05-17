# models.py

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Менеджер для пользовательской модели

# Модель для пользователя
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class TaskMakerUserManager(BaseUserManager):
    def create_user(self, user_login, user_email, user_name, user_surname, password=None):
        if not user_email:
            raise ValueError("User must have an email address")
        user = self.model(
            user_login=user_login,
            user_email=user_email,
            user_name=user_name,
            user_surname=user_surname
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_login, user_email, user_name, user_surname, password=None):
        user = self.create_user(
            user_login=user_login,
            user_email=user_email,
            user_name=user_name,
            user_surname=user_surname,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class TaskMakerUser(AbstractBaseUser, PermissionsMixin):
    user_email = models.EmailField(max_length=255, unique=True)
    user_name = models.CharField(max_length=255)
    user_login = models.CharField(max_length=255, unique=True)
    user_surname = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default='')

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # Make sure this is the proper field to authenticate the user
    USERNAME_FIELD = 'user_login'
    REQUIRED_FIELDS = ['user_email', 'user_name', 'user_surname']

    objects = TaskMakerUserManager()

    def __str__(self):
        return self.user_login

    # Admin interface permissions
    @property
    def is_staff(self):
        return self.is_admin

    # Additional methods for Django's authentication system
    def get_full_name(self):
        return f"{self.user_name} {self.user_surname}"

    def get_short_name(self):
        return self.user_name

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


# Модель для проекта
from django.conf import settings

class Project(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Project Name"))
    description = models.TextField(blank=True, verbose_name=_("Project Description"))
    start_date = models.DateField(blank=True, null=True, verbose_name=_("Start Date"))
    end_date = models.DateField(blank=True, null=True, verbose_name=_("End Date"))

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='projects'
    )

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['start_date']

    def __str__(self):
        return self.name


# Модель для задачи
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Высокий', 'Высокий'),
        ('Средний', 'Средний'),
        ('Низкий', 'Низкий'),
    ]

    STATUS_CHOICES = [
        ('Новая', 'Новая'),
        ('В работе', 'В работе'),
        ('Завершена', 'Завершена'),
        ('Отложена', 'Отложена'),
    ]

    MODE_CHOICES = [
        ('Личный', 'Личный'),
        ('Командный', 'Командный'),
    ]

    creator = models.ForeignKey(
        'taskapp.TaskMakerUser',  # Update with your app's name
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    project = models.ForeignKey(
        'Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None
    )

    task_name = models.CharField(max_length=255)
    task_description = models.TextField(blank=True)
    task_make_date = models.DateTimeField(auto_now_add=True)
    task_update_date = models.DateTimeField(auto_now=True)
    task_should_done_date = models.DateField(null=True, blank=True)
    task_implementer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Средний'
    )
    task_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Новая'
    )
    assignee = models.ForeignKey(
        'taskapp.TaskMakerUser',  # Update with your app's name
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    task_home = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    task_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default='Личный'
    )

    def __str__(self):
        return self.task_name

    class Meta:
        ordering = ['task_make_date']

    # Метод для преобразования задачи в словарь
    def to_dict(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'task_description': self.task_description,
            'task_make_date': self.task_make_date.strftime('%Y-%m-%d %H:%M:%S') if self.task_make_date else None,
            'task_update_date': self.task_update_date.strftime('%Y-%m-%d %H:%M:%S') if self.task_update_date else None,
            'task_should_done_date': self.task_should_done_date.strftime(
                '%Y-%m-%d') if self.task_should_done_date else None,
            'task_priority': self.task_priority,
            'task_status': self.task_status,
            'assignee': self.assignee.get_full_name() if self.assignee else '',
        }



# Модель для комментариев
class Comment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey('taskapp.TaskMakerUser', on_delete=models.CASCADE)  # Update with your app's name
    description = models.TextField()
    date_of_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Комментарий к '{self.task}' от {self.user}"


# Модель для файлов, прикрепленных к задачам
class File(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_files/', blank=True, null=True)
    file_weight = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.file.name


class ProjectMember(models.Model):
    ROLE_CHOICES = [
        ('Администратор', 'Администратор'),
        ('Участник', 'Участник'),
        ('Наблюдатель', 'Наблюдатель'),
    ]
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('taskapp.TaskMakerUser', on_delete=models.CASCADE)
    project_role = models.CharField(max_length=50, choices=ROLE_CHOICES, blank=True, null=True)

    class Meta:
        unique_together = ('project', 'user')
        verbose_name = _("Project Member")
        verbose_name_plural = _("Project Members")

    def __str__(self):
        return f"{self.user} в проекте {self.project}"



# Модель для напоминаний
class Reminder(models.Model):
    REMIND_CHOICES = [
        ('Email', 'Email'),
        ('Push', 'Push'),
    ]

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    date_of_remind = models.DateTimeField()
    type_of_remind = models.CharField(max_length=20, choices=REMIND_CHOICES, default='Push')

    def __str__(self):
        return f"Напоминание для '{self.task}' ({self.type_of_remind})"

    def clean(self):
        if self.date_of_remind and self.date_of_remind < timezone.now():
            raise ValidationError("Reminder date cannot be in the past.")
