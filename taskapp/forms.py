from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import Project, Task, TaskMakerUser
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = TaskMakerUser
        fields = ['user_name', 'user_surname', 'user_email', 'user_login', 'password1', 'password2']


from django import forms
from django.core.exceptions import ValidationError
from .models import Project, ProjectMember
from .models import TaskMakerUser  # твоя модель пользователя

class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=TaskMakerUser.objects.all(),
        widget=forms.SelectMultiple(attrs={'size': 5}),
        label="Участники проекта",
        required=False
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'members']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'start_date': 'Дата начала',
            'end_date': 'Дата завершения',
        }

    def clean_end_date(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise ValidationError("Дата завершения должна быть позже даты начала.")
        return end_date

    def clean_members(self):
        members = self.cleaned_data.get('members')
        if not members:
            raise ValidationError('Необходимо выбрать хотя бы одного участника.')
        if len(members) > 10:
            raise ValidationError('Максимальное количество участников проекта — 10.')
        return members

    def save(self, commit=True):
        project = super().save(commit=False)
        if commit:
            project.save()
        if self.cleaned_data.get('members'):
            # Чистим старые связи, чтобы не дублировать
            ProjectMember.objects.filter(project=project).delete()
            # Создаем новые
            for user in self.cleaned_data['members']:
                ProjectMember.objects.create(project=project, user=user)
        return project



class TaskForm(forms.ModelForm):
    # Добавляем обязательные поля для user_id и project_id
    user_id = forms.IntegerField(required=True)
    project_id = forms.IntegerField(required=True)

    class Meta:
        model = Task
        fields = ['task_name', 'task_description', 'task_should_done_date',
                  'task_priority', 'task_status', 'assignee', 'task_home', 'task_mode', 'project']

    def clean(self):
        # Проводим общую валидацию формы
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        project_id = cleaned_data.get('project_id')

        # Проверяем, что оба поля присутствуют
        if not user_id or not project_id:
            raise ValidationError("Both user_id and project_id are required.")

        return cleaned_data

    def clean_task_should_done_date(self):
        task_should_done_date = self.cleaned_data.get('task_should_done_date')
        project = self.cleaned_data.get('project')

        # Проверяем, что дата выполнения задачи не в прошлом
        if task_should_done_date and task_should_done_date < timezone.now().date():
            raise ValidationError("Дата завершения задачи не может быть в прошлом.")

        # Проверяем, что дата выполнения задачи не позже даты завершения проекта
        if project and task_should_done_date > project.end_date:
            raise ValidationError("Дата завершения задачи не может быть позже даты завершения проекта.")

        return task_should_done_date

    def save(self, commit=True):
        # Извлекаем значения user_id и project_id
        user_id = self.cleaned_data.get('user_id')
        project_id = self.cleaned_data.get('project_id')

        # Если один из параметров отсутствует, то не сохраняем задачу
        if not user_id or not project_id:
            raise ValidationError("Both user_id and project_id are required.")

        # Сохраняем объект задачи, но не сразу сохраняем в базу
        task = super().save(commit=False)
        task.user_id = user_id  # Присваиваем user_id
        task.project_id = project_id  # Присваиваем project_id

        if commit:
            task.save()  # Сохраняем задачу в базе данных
        return task

from django import forms
from django.core.exceptions import ValidationError
from .models import TaskMakerUser

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'id': 'id_name'}))
    surname = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'id': 'id_surname'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'id': 'id_email'}))
    login = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'id': 'id_login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_password'}), min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_confirm_password'}), label="Подтвердите пароль")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if TaskMakerUser.objects.filter(user_email=email).exists():
            raise ValidationError('Этот email уже зарегистрирован.')
        return email

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if TaskMakerUser.objects.filter(user_login=login).exists():
            raise ValidationError('Этот логин уже занят.')
        return login

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self):
        user = TaskMakerUser.objects.create_user(
            user_name=self.cleaned_data['name'],
            user_surname=self.cleaned_data['surname'],
            user_email=self.cleaned_data['email'],
            user_login=self.cleaned_data['login'],
            password=self.cleaned_data['password']
        )
        return user

from django import forms
from .models import ProjectMember

class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ['user', 'project_role']
        labels = {
            'user': 'Пользователь',
            'project_role': 'Роль в проекте',
        }
        widgets = {
            'project_role': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectMemberForm, self).__init__(*args, **kwargs)
        self.fields['project_role'].required = True
