# my_django_project/my_django_project/urls.py

from django.contrib import admin
from django.urls import path
from stock_app.views import stock_view, get_intervals, chat_with_ai

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get_intervals/', get_intervals, name='get_intervals'),
    path('chat/', chat_with_ai, name='chat_with_ai'),
    path('', stock_view, name='home'),
    path('stock/', stock_view, name='stock'),
]