from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('coordinator/', views.coordinator_dashboard, name='coordinator'),
    path('student/', views.student_dashboard, name='student'),
]
