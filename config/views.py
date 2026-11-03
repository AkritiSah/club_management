from django.shortcuts import render
from django.utils import timezone
from clubs.models import Club
from events.models import ClubEvent
from accounts.models import User
from memberships.models import ClubMembership
from announcements.models import Announcement


def landing_view(request):
    now = timezone.now()

    # Public active clubs
    featured_clubs = Club.objects.filter(status=Club.Status.ACTIVE).select_related('coordinator')[:6]

    # Upcoming events
    upcoming_events = ClubEvent.objects.filter(
        status=ClubEvent.Status.UPCOMING,
        start_date_time__gt=now
    ).select_related('club').order_by('start_date_time')[:3]

    # Recent announcements
    recent_announcements = Announcement.objects.select_related('club').order_by('-created_at')[:4]

    # Stats counters
    stats = {
        'clubs': Club.objects.filter(status=Club.Status.ACTIVE).count(),
        'students': User.objects.filter(role=User.Role.STUDENT).count(),
        'events': ClubEvent.objects.count(),
        'memberships': ClubMembership.objects.filter(status=ClubMembership.Status.APPROVED).count(),
    }

    context = {
        'featured_clubs': featured_clubs,
        'upcoming_events': upcoming_events,
        'recent_announcements': recent_announcements,
        'stats': stats,
    }
    return render(request, 'landing.html', context)
