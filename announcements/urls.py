from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list_view, name='list'),
    path('create/', views.announcement_create_view, name='create'),
    path('<int:pk>/edit/', views.announcement_update_view, name='update'),
    path('<int:pk>/delete/', views.announcement_delete_view, name='delete'),
]
