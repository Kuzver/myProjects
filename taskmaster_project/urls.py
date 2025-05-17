from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админка Django
    path('admin/', admin.site.urls),

    path('accounts/', include('django.contrib.auth.urls')),  # добавьте это для аутентификации

    # Подключение URL-ов из приложения taskapp
    path('', include('taskapp.urls')),  # это подключает URLs из taskapp

    # Дополнительные маршруты, если они есть
    # например, можно добавить пути для API, или другие пути, если необходимо
]

# Для статики (например, картинок или стилей) в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


