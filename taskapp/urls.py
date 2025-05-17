from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import TaskAPIView, TaskDetailAPIView

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)

urlpatterns = [
    # DRF API Views
    path('taskapp/api/task-list/', TaskAPIView.as_view(), name='task-api'),
    path('taskapp/api/task-detail/<int:pk>/', TaskDetailAPIView.as_view(), name='task-detail-api'),
    path('taskapp/api/tasks/', views.task_list_json, name='task_list_json'),
    path('taskapp/api/tasks_by_month/', views.api_tasks_by_month, name='api_tasks_by_month'),
    path('taskapp/api_task_list/', views.api_task_list, name='api_task_list'),

    # Обычные представления
    path('', views.home, name='home'),
    path('taskapp/api/add_task/', views.add_task, name='add_task'),
    path('taskapp/api/add_task/<int:project_id>/', views.add_task, name='add_task_with_project'),
    path('taskapp/register/', views.register, name='register'),
    path('taskapp/task_list/<int:user_id>/', views.task_list, name='task_list'),
    path('taskapp/task_list/ajax/', views.task_list_ajax, name='task_list_ajax'),
    path('taskapp/calendar/', views.calendar_view, name='calendar_view'),
    path('taskapp/team_work/<int:project_id>/', views.team_work, name='team_work'),
    path('taskapp/create_team/', views.create_team, name='create_team'),
    path('taskapp/assign_task/<int:project_id>/', views.assign_task, name='assign_task'),
    path('taskapp/manage_project/', views.manage_project, name='manage_project'),
    path('taskapp/manage_project/<int:project_id>/', views.manage_project, name='manage_project_with_id'),
    path('taskapp/team_work/<int:project_id>/', views.project_calendar_view, name='project_calendar_view'),

    # DRF ViewSet routes
    path('api/', include(router.urls)),
]