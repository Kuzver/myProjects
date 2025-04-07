from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_user_view, name='register'),
    path('tasks/', views.task_list_view, name='task_list'),

]
