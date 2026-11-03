from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from .models import ClubEvent, EventRegistration
from .forms import ClubEventForm, EventAttendanceForm
from clubs.models import Club
from accounts.decorators import admin_required, coordinator_or_admin_required, student_required
from dashboard.models import ActivityLog


def event_list_view(request):
    query = request.GET.get('q', '').strip()
    club_filter = request.GET.get('club', '').strip()
    status_filter = request.GET.get('status', '').strip()

    events = ClubEvent.objects.select_related('club').prefetch_related('registrations').order_by('start_date_time')

    now = timezone.now()

    if status_filter == 'UPCOMING':
        events = events.filter(start_date_time__gt=now, status=ClubEvent.Status.UPCOMING)
    elif status_filter == 'ONGOING':
        events = events.filter(start_date_time__lte=now, end_date_time__gte=now)
    elif status_filter == 'COMPLETED':
        events = events.filter(Q(end_date_time__lt=now) | Q(status=ClubEvent.Status.COMPLETED)).order_by('-start_date_time')

    if club_filter:
        events = events.filter(club_id=club_filter)

    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(venue__icontains=query) |
            Q(club__name__icontains=query)
        )

    # If student is logged in, record their registered events
    user_registrations = set()
    if request.user.is_authenticated and request.user.is_student_role:
        user_registrations = set(
            EventRegistration.objects.filter(
                student=request.user,
                status=EventRegistration.Status.REGISTERED
            ).values_list('event_id', flat=True)
        )

    paginator = Paginator(events, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    clubs = Club.objects.filter(status=Club.Status.ACTIVE).order_by('name')

    context = {
        'page_obj': page_obj,
        'query': query,
        'club_filter': club_filter,
        'status_filter': status_filter,
        'clubs': clubs,
        'user_registrations': user_registrations,
        'total_events': events.count(),
    }
    return render(request, 'events/event_list.html', context)


def event_detail_view(request, slug):
    event = get_object_or_404(ClubEvent.objects.select_related('club', 'club__coordinator'), slug=slug)

    is_registered = False
    registration = None
    if request.user.is_authenticated and request.user.is_student_role:
        registration = EventRegistration.objects.filter(event=event, student=request.user).first()
        is_registered = bool(registration and registration.status == EventRegistration.Status.REGISTERED)

    can_manage = False
    if request.user.is_authenticated:
        if request.user.is_admin_role or (request.user.is_coordinator_role and event.club.coordinator == request.user):
            can_manage = True

    context = {
        'event': event,
        'is_registered': is_registered,
        'registration': registration,
        'can_manage': can_manage,
    }
    return render(request, 'events/event_detail.html', context)


@login_required
def event_create_view(request):
    # Only Admin or Coordinators can create events
    if not (request.user.is_admin_role or request.user.is_coordinator_role):
        messages.error(request, "Permission denied.")
        return redirect('events:list')

    if request.method == 'POST':
        form = ClubEventForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            # Ensure coordinator can only assign to their club
            if not request.user.is_admin_role and event.club.coordinator != request.user:
                messages.error(request, "You can only create events for your assigned club.")
                return redirect('events:list')
            event.save()
            ActivityLog.log(request.user, f"Created event: {event.title} for {event.club.name}", category='EVENT')
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('events:detail', slug=event.slug)
    else:
        initial = {}
        club_id = request.GET.get('club')
        if club_id:
            initial['club'] = club_id
        form = ClubEventForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'title': 'Create New Event',
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_update_view(request, slug):
    event = get_object_or_404(ClubEvent, slug=slug)

    # Permission check
    if not (request.user.is_admin_role or (request.user.is_coordinator_role and event.club.coordinator == request.user)):
        messages.error(request, "You are not authorized to edit this event.")
        return redirect('events:detail', slug=event.slug)

    if request.method == 'POST':
        form = ClubEventForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            event = form.save()
            ActivityLog.log(request.user, f"Updated event details: {event.title}", category='EVENT')
            messages.success(request, f"Event '{event.title}' updated successfully!")
            return redirect('events:detail', slug=event.slug)
    else:
        form = ClubEventForm(instance=event, user=request.user)

    context = {
        'form': form,
        'event': event,
        'title': f'Edit Event: {event.title}',
        'is_edit': True,
    }
    return render(request, 'events/event_form.html', context)


@login_required
def event_delete_view(request, slug):
    event = get_object_or_404(ClubEvent, slug=slug)

    if not (request.user.is_admin_role or (request.user.is_coordinator_role and event.club.coordinator == request.user)):
        messages.error(request, "You are not authorized to delete this event.")
        return redirect('events:detail', slug=event.slug)

    if request.method == 'POST':
        title = event.title
        event.delete()
        ActivityLog.log(request.user, f"Deleted event: {title}", category='EVENT')
        messages.success(request, f"Event '{title}' has been deleted.")
        return redirect('events:list')

    return render(request, 'events/event_confirm_delete.html', {'event': event})


@login_required
def register_event_view(request, slug):
    event = get_object_or_404(ClubEvent, slug=slug)

    if not event.is_registration_open:
        messages.error(request, "Registration for this event is closed or reached full capacity.")
        return redirect('events:detail', slug=event.slug)

    # Check if already registered
    reg, created = EventRegistration.objects.get_or_create(
        event=event,
        student=request.user,
        defaults={'status': EventRegistration.Status.REGISTERED}
    )

    if not created:
        if reg.status == EventRegistration.Status.CANCELLED:
            reg.status = EventRegistration.Status.REGISTERED
            reg.registered_at = timezone.now()
            reg.save()
            ActivityLog.log(request.user, f"Re-registered for event: {event.title}", category='EVENT')
            messages.success(request, f"You have re-registered for '{event.title}'!")
        else:
            messages.info(request, f"You are already registered for '{event.title}'.")
    else:
        ActivityLog.log(request.user, f"Registered for event: {event.title}", category='EVENT')
        messages.success(request, f"Successfully registered for '{event.title}'! Save the date.")

    return redirect('events:detail', slug=event.slug)


@login_required
def cancel_event_registration_view(request, slug):
    event = get_object_or_404(ClubEvent, slug=slug)
    reg = EventRegistration.objects.filter(event=event, student=request.user).first()
    if reg and reg.status == EventRegistration.Status.REGISTERED:
        reg.status = EventRegistration.Status.CANCELLED
        reg.save()
        ActivityLog.log(request.user, f"Cancelled registration for event: {event.title}", category='EVENT')
        messages.info(request, f"Your registration for '{event.title}' has been cancelled.")
    return redirect('events:detail', slug=event.slug)


@login_required
def event_registrations_view(request, slug):
    event = get_object_or_404(ClubEvent.objects.select_related('club'), slug=slug)

    # Permission check
    if not (request.user.is_admin_role or (request.user.is_coordinator_role and event.club.coordinator == request.user)):
        messages.error(request, "Permission denied.")
        return redirect('events:detail', slug=event.slug)

    registrations = EventRegistration.objects.filter(event=event).select_related('student', 'student__student_profile').order_by('-registered_at')

    # Update individual attendance status if requested
    if request.method == 'POST':
        reg_id = request.POST.get('registration_id')
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        if reg_id and new_status:
            target_reg = get_object_or_404(EventRegistration, id=reg_id, event=event)
            target_reg.status = new_status
            if notes:
                target_reg.attendance_notes = notes
            target_reg.save()
            messages.success(request, f"Updated attendance for {target_reg.student.username}.")
            return redirect('events:registrations', slug=event.slug)

    context = {
        'event': event,
        'registrations': registrations,
        'total_registrations': registrations.filter(status=EventRegistration.Status.REGISTERED).count(),
        'attended_count': registrations.filter(status=EventRegistration.Status.ATTENDED).count(),
    }
    return render(request, 'events/event_registrations.html', context)


@login_required
def my_registrations_view(request):
    registrations = EventRegistration.objects.filter(student=request.user).select_related('event', 'event__club').order_by('-registered_at')
    return render(request, 'events/my_registrations.html', {'registrations': registrations})
