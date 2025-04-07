from django.shortcuts import render
from django.shortcuts import render
from django.db import connection
from .forms import RegisterForm

def register_user_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT register_user(%s, %s, %s, %s, %s);
                    """, (
                        data['name'],
                        data['surname'],
                        data['email'],
                        data['login'],
                        data['password']
                    ))
                return render(request, 'register.html', {'form': form, 'success': True})
            except Exception as e:
                return render(request, 'register.html', {'form': form, 'error': str(e)})
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



from django.shortcuts import render, redirect
from .forms import RegisterForm
import psycopg2

def home_view(request):
    return render(request, 'home.html')

def register_user_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                conn = psycopg2.connect(
                    dbname="taskmaster",
                    user="kuznecovaveravladislavovna",
                    password="1212",
                    host="localhost",
                    port="5433"
                )
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT register_user(%s, %s, %s, %s, %s);
                """, (data['name'], data['surname'], data['email'], data['login'], data['password']))
                conn.commit()
                cursor.close()
                conn.close()
                return render(request, 'success.html')
            except Exception as e:
                form.add_error(None, f'Ошибка регистрации: {e}')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def task_list_view(request):
    tasks = []
    try:
        conn = psycopg2.connect(
            dbname="taskmaster",
            user="kuznecovaveravladislavovna",
            password="1212",
            host="localhost",
            port="5433"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_summary_view;")  # Используем представление
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при получении задач: {e}")

    return render(request, 'task_list.html', {'tasks': tasks})
