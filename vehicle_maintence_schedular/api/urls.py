from django.urls import path
from . import views

urlpatterns = [
    path('schedule', views.schedule_all),
    path('schedule/<int:depot_id>', views.schedule_depot),
]
