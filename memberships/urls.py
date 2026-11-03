from django.urls import path
from . import views

app_name = 'memberships'

urlpatterns = [
    path('my-requests/', views.my_memberships_view, name='my_memberships'),
    path('all/', views.all_memberships_view, name='all_memberships'),
    path('request/<slug:club_slug>/', views.request_membership_view, name='request'),
    path('cancel/<int:pk>/', views.cancel_membership_view, name='cancel'),
    path('club/<slug:club_slug>/', views.club_members_view, name='club_members'),
    path('approve/<int:pk>/', views.approve_membership_view, name='approve'),
    path('reject/<int:pk>/', views.reject_membership_view, name='reject'),
]
