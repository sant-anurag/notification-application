# notifications/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('read/all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),
]