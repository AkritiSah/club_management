from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from accounts.models import User, StudentProfile
from clubs.models import Club
from memberships.models import ClubMembership
from events.models import ClubEvent, EventRegistration
from announcements.models import Announcement
from dashboard.models import ActivityLog
from accounts.decorators import admin_required, coordinator_required, student_required


@login_required
def dashboard_index(request):
    """Directs logged in user to their role-specific dashboard."""
    if request.user.is_admin_role:
        return redirect('dashboard:admin')
    elif request.user.is_coordinator_role:
        return redirect('dashboard:coordinator')
    else:
        return redirect('dashboard:student')


@admin_required
def admin_dashboard(request):
    now = timezone.now()

    # Core statistics
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_clubs = Club.objects.count()
    active_clubs = Club.objects.filter(status=Club.Status.ACTIVE).count()
    pending_clubs = Club.objects.filter(status=Club.Status.PENDING).count()
    total_coordinators = User.objects.filter(role=User.Role.COORDINATOR).count()
    
    total_memberships = ClubMembership.objects.count()
    approved_memberships = ClubMembership.objects.filter(status=ClubMembership.Status.APPROVED).count()
    pending_memberships = ClubMembership.objects.filter(status=ClubMembership.Status.PENDING).count()

    total_events = ClubEvent.objects.count()
    upcoming_events = ClubEvent.objects.filter(start_date_time__gt=now, status=ClubEvent.Status.UPCOMING).count()
    total_registrations = EventRegistration.objects.filter(status=EventRegistration.Status.REGISTERED).count()

    # Recent items
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:8]
    pending_club_requests = Club.objects.filter(status=Club.Status.PENDING).order_by('-created_at')[:5]
    pending_membership_requests = ClubMembership.objects.filter(status=ClubMembership.Status.PENDING).select_related('student', 'club').order_by('-request_date')[:5]
    upcoming_events_list = ClubEvent.objects.filter(start_date_time__gt=now).select_related('club').order_by('start_date_time')[:5]

    context = {
        'total_students': total_students,
        'total_clubs': total_clubs,
        'active_clubs': active_clubs,
        'pending_clubs': pending_clubs,
        'total_coordinators': total_coordinators,
        'total_memberships': total_memberships,
        'approved_memberships': approved_memberships,
        'pending_memberships': pending_memberships,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'total_registrations': total_registrations,
        'recent_activities': recent_activities,
        'pending_club_requests': pending_club_requests,
        'pending_membership_requests': pending_membership_requests,
        'upcoming_events_list': upcoming_events_list,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@coordinator_required
def coordinator_dashboard(request):
    user = request.user
    now = timezone.now()

    # Clubs coordinated by this user
    coordinated_clubs = Club.objects.filter(coordinator=user)
    first_club = coordinated_clubs.first()

    # Stats across all coordinated clubs
    total_members = ClubMembership.objects.filter(
        club__in=coordinated_clubs,
        status=ClubMembership.Status.APPROVED
    ).count()

    pending_requests = ClubMembership.objects.filter(
        club__in=coordinated_clubs,
        status=ClubMembership.Status.PENDING
    ).select_related('student', 'student__student_profile', 'club').order_by('-request_date')

    upcoming_events = ClubEvent.objects.filter(
        club__in=coordinated_clubs,
        start_date_time__gt=now
    ).order_by('start_date_time')

    total_registrations = EventRegistration.objects.filter(
        event__club__in=coordinated_clubs,
        status=EventRegistration.Status.REGISTERED
    ).count()

    recent_announcements = Announcement.objects.filter(
        club__in=coordinated_clubs
    ).order_by('-created_at')[:5]

    context = {
        'coordinated_clubs': coordinated_clubs,
        'first_club': first_club,
        'total_members': total_members,
        'pending_requests_count': pending_requests.count(),
        'pending_requests': pending_requests[:8],
        'upcoming_events_count': upcoming_events.count(),
        'upcoming_events': upcoming_events[:5],
        'total_registrations': total_registrations,
        'recent_announcements': recent_announcements,
    }
    return render(request, 'dashboard/coordinator_dashboard.html', context)


@student_required
def student_dashboard(request):
    user = request.user
    now = timezone.now()

    # Joined approved clubs
    joined_memberships = ClubMembership.objects.filter(
        student=user,
        status=ClubMembership.Status.APPROVED
    ).select_related('club', 'club__coordinator')

    joined_club_ids = joined_memberships.values_list('club_id', flat=True)

    # Pending membership requests
    pending_memberships = ClubMembership.objects.filter(
        student=user,
        status=ClubMembership.Status.PENDING
    ).select_related('club')

    # Upcoming registered events
    registered_events = EventRegistration.objects.filter(
        student=user,
        status=EventRegistration.Status.REGISTERED,
        event__start_date_time__gt=now
    ).select_related('event', 'event__club').order_by('event__start_date_time')

    # Announcements from joined clubs OR college-wide
    relevant_announcements = Announcement.objects.filter(
        Q(club_id__in=joined_club_ids) | Q(club__isnull=True)
    ).select_related('club', 'created_by').order_by('-created_at')[:6]

    # Completed events attended
    past_participations = EventRegistration.objects.filter(
        student=user
    ).select_related('event', 'event__club').order_by('-registered_at')[:5]

    context = {
        'joined_memberships': joined_memberships,
        'joined_clubs_count': joined_memberships.count(),
        'pending_memberships': pending_memberships,
        'pending_count': pending_memberships.count(),
        'registered_events': registered_events,
        'registered_events_count': registered_events.count(),
        'relevant_announcements': relevant_announcements,
        'past_participations': past_participations,
    }
    return render(request, 'dashboard/student_dashboard.html', context)
