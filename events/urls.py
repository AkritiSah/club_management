from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list_view, name='list'),
    path('create/', views.event_create_view, name='create'),
    path('my-registrations/', views.my_registrations_view, name='my_registrations'),
    path('<slug:slug>/', views.event_detail_view, name='detail'),
    path('<slug:slug>/edit/', views.event_update_view, name='update'),
    path('<slug:slug>/delete/', views.event_delete_view, name='delete'),
    path('<slug:slug>/register/', views.register_event_view, name='register'),
    path('<slug:slug>/cancel/', views.cancel_event_registration_view, name='cancel_registration'),
    path('<slug:slug>/registrations/', views.event_registrations_view, name='registrations'),
]
