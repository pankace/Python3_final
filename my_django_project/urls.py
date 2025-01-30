from django.contrib import admin
from django.urls import path
from stock_app.views import stock_view, get_intervals

urlpatterns = [
    path('', stock_view, name='home'),
    path('stock/', stock_view, name='stock'),
    path('get_intervals/', get_intervals, name='get_intervals'),  # Ensure this line exists
    path('admin/', admin.site.urls),
]