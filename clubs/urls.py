from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list_view, name='list'),
    path('create/', views.club_create_view, name='create'),
    path('my-clubs/', views.my_clubs_view, name='my_clubs'),
    path('requests/', views.club_requests_view, name='requests'),
    path('requests/<int:pk>/approve/', views.approve_club_proposal_view, name='approve_proposal'),
    path('requests/<int:pk>/reject/', views.reject_club_proposal_view, name='reject_proposal'),
    path('<slug:slug>/', views.club_detail_view, name='detail'),
    path('<slug:slug>/edit/', views.club_update_view, name='update'),
    path('<slug:slug>/delete/', views.club_delete_view, name='delete'),
]
