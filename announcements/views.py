from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Announcement
from .forms import AnnouncementForm
from clubs.models import Club
from accounts.decorators import coordinator_or_admin_required
from dashboard.models import ActivityLog


def announcement_list_view(request):
    query = request.GET.get('q', '').strip()
    club_filter = request.GET.get('club', '').strip()
    priority_filter = request.GET.get('priority', '').strip()

    announcements = Announcement.objects.select_related('club', 'created_by').order_by('-created_at')

    if club_filter:
        if club_filter == 'college':
            announcements = announcements.filter(club__isnull=True)
        else:
            announcements = announcements.filter(club_id=club_filter)

    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)

    if query:
        announcements = announcements.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(club__name__icontains=query)
        )

    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    clubs = Club.objects.filter(status=Club.Status.ACTIVE).order_by('name')

    context = {
        'page_obj': page_obj,
        'query': query,
        'club_filter': club_filter,
        'priority_filter': priority_filter,
        'clubs': clubs,
        'priorities': Announcement.Priority.choices,
        'total_announcements': announcements.count(),
    }
    return render(request, 'announcements/announcement_list.html', context)


@login_required
def announcement_create_view(request):
    if not (request.user.is_admin_role or request.user.is_coordinator_role):
        messages.error(request, "Permission denied.")
        return redirect('announcements:list')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, user=request.user)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            # Ensure coordinator can only post for their clubs
            if not request.user.is_admin_role:
                if not announcement.club or announcement.club.coordinator != request.user:
                    messages.error(request, "You can only post announcements for your assigned club.")
                    return redirect('announcements:list')
            announcement.save()
            ActivityLog.log(request.user, f"Posted announcement: {announcement.title}", category='ANNOUNCEMENT')
            messages.success(request, "Announcement published successfully!")
            return redirect('announcements:list')
    else:
        initial = {}
        club_id = request.GET.get('club')
        if club_id:
            initial['club'] = club_id
        form = AnnouncementForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'title': 'Publish New Announcement',
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
def announcement_update_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    # Permission check: author or admin
    if not (request.user.is_admin_role or announcement.created_by == request.user or (announcement.club and announcement.club.coordinator == request.user)):
        messages.error(request, "You are not authorized to edit this announcement.")
        return redirect('announcements:list')

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement, user=request.user)
        if form.is_valid():
            form.save()
            ActivityLog.log(request.user, f"Updated announcement: {announcement.title}", category='ANNOUNCEMENT')
            messages.success(request, "Announcement updated successfully!")
            return redirect('announcements:list')
    else:
        form = AnnouncementForm(instance=announcement, user=request.user)

    context = {
        'form': form,
        'announcement': announcement,
        'title': 'Edit Announcement',
        'is_edit': True,
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
def announcement_delete_view(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)

    if not (request.user.is_admin_role or announcement.created_by == request.user or (announcement.club and announcement.club.coordinator == request.user)):
        messages.error(request, "You are not authorized to delete this announcement.")
        return redirect('announcements:list')

    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        ActivityLog.log(request.user, f"Deleted announcement: {title}", category='ANNOUNCEMENT')
        messages.success(request, f"Announcement '{title}' deleted.")
        return redirect('announcements:list')

    return render(request, 'announcements/announcement_confirm_delete.html', {'announcement': announcement})
