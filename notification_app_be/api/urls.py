from django.urls import path
from . import views

urlpatterns = [
    path('notifications', views.get_all_notifications),
    path('notifications/unread-count', views.unread_count),
    path('notifications/read-all', views.mark_all_read),
    path('notifications/<uuid:notification_id>', views.get_one_notification),
    path('notifications/<uuid:notification_id>/read', views.mark_one_read),
    path('notifications/<uuid:notification_id>/delete', views.delete_notification),
    path('notifications/create', views.create_notification),
]
