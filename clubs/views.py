from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Club
from .forms import ClubForm, ClubProposalForm
from memberships.models import ClubMembership
from events.models import ClubEvent
from announcements.models import Announcement
from accounts.decorators import admin_required, coordinator_or_admin_required
from dashboard.models import ActivityLog


def club_list_view(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    # Active clubs for regular view
    clubs = Club.objects.filter(status=Club.Status.ACTIVE).select_related('coordinator').annotate(
        approved_members=Count('memberships', filter=Q(memberships__status=ClubMembership.Status.APPROVED))
    ).order_by('name')

    if query:
        clubs = clubs.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(coordinator__username__icontains=query) |
            Q(coordinator__first_name__icontains=query)
        )

    if category:
        clubs = clubs.filter(category=category)

    # If student is logged in, find their membership statuses
    user_memberships = {}
    if request.user.is_authenticated and request.user.is_student_role:
        memberships = ClubMembership.objects.filter(student=request.user)
        for m in memberships:
            user_memberships[m.club_id] = m.status

    paginator = Paginator(clubs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Club.Category.choices

    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'user_memberships': user_memberships,
        'total_clubs': clubs.count(),
    }
    return render(request, 'clubs/club_list.html', context)


def club_detail_view(request, slug):
    club = get_object_or_404(Club.objects.select_related('coordinator'), slug=slug)

    # Check student membership status
    membership = None
    if request.user.is_authenticated and request.user.is_student_role:
        membership = ClubMembership.objects.filter(student=request.user, club=club).first()

    # Club's upcoming and past events
    upcoming_events = ClubEvent.objects.filter(club=club, status__in=[ClubEvent.Status.UPCOMING, ClubEvent.Status.ONGOING]).order_by('start_date_time')[:4]
    past_events = ClubEvent.objects.filter(club=club, status=ClubEvent.Status.COMPLETED).order_by('-start_date_time')[:3]

    # Club's announcements
    announcements = Announcement.objects.filter(club=club).order_by('-created_at')[:5]

    # Approved members count
    approved_members = ClubMembership.objects.filter(club=club, status=ClubMembership.Status.APPROVED).select_related('student', 'student__student_profile')[:10]

    can_manage = False
    if request.user.is_authenticated:
        if request.user.is_admin_role or (request.user.is_coordinator_role and club.coordinator == request.user):
            can_manage = True

    context = {
        'club': club,
        'membership': membership,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'announcements': announcements,
        'approved_members': approved_members,
        'can_manage': can_manage,
    }
    return render(request, 'clubs/club_detail.html', context)


@login_required
def club_create_view(request):
    if request.user.is_admin_role:
        # Full Club Form for Administrator
        if request.method == 'POST':
            form = ClubForm(request.POST, request.FILES)
            if form.is_valid():
                club = form.save()
                ActivityLog.log(request.user, f"Created new club: {club.name}", category='CLUB')
                messages.success(request, f"Club '{club.name}' created successfully!")
                return redirect('clubs:detail', slug=club.slug)
            else:
                messages.error(request, "Please check the form inputs.")
        else:
            form = ClubForm()
        is_proposal = False
    else:
        # Club Proposal Form for Coordinators or Students
        if request.method == 'POST':
            form = ClubProposalForm(request.POST, request.FILES)
            if form.is_valid():
                club = form.save(commit=False)
                if request.user.is_coordinator_role:
                    club.coordinator = request.user
                club.status = Club.Status.PENDING
                club.save()
                ActivityLog.log(request.user, f"Submitted club creation proposal: {club.name}", category='CLUB')
                messages.success(request, f"Club proposal for '{club.name}' submitted successfully! Awaiting Administrator approval.")
                return redirect('clubs:list')
            else:
                messages.error(request, "Please correct errors in proposal form.")
        else:
            form = ClubProposalForm()
        is_proposal = True

    context = {
        'form': form,
        'is_proposal': is_proposal,
        'title': 'Propose New Club' if is_proposal else 'Create New Club',
    }
    return render(request, 'clubs/club_form.html', context)


@login_required
def club_update_view(request, slug):
    club = get_object_or_404(Club, slug=slug)

    # Permission check: Admin or assigned coordinator
    if not (request.user.is_admin_role or (request.user.is_coordinator_role and club.coordinator == request.user)):
        messages.error(request, "You are not authorized to edit this club.")
        return redirect('clubs:detail', slug=club.slug)

    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            club = form.save()
            ActivityLog.log(request.user, f"Updated club details: {club.name}", category='CLUB')
            messages.success(request, f"Club '{club.name}' updated successfully!")
            return redirect('clubs:detail', slug=club.slug)
    else:
        form = ClubForm(instance=club)

    context = {
        'form': form,
        'club': club,
        'title': f'Edit Club: {club.name}',
        'is_edit': True,
    }
    return render(request, 'clubs/club_form.html', context)


@admin_required
def club_delete_view(request, slug):
    club = get_object_or_404(Club, slug=slug)
    if request.method == 'POST':
        club_name = club.name
        club.delete()
        ActivityLog.log(request.user, f"Deleted club: {club_name}", category='CLUB')
        messages.success(request, f"Club '{club_name}' has been permanently deleted.")
        return redirect('clubs:list')

    return render(request, 'clubs/club_confirm_delete.html', {'club': club})


@admin_required
def club_requests_view(request):
    pending_clubs = Club.objects.filter(status=Club.Status.PENDING).order_by('-created_at')
    return render(request, 'clubs/club_requests.html', {'pending_clubs': pending_clubs})


@admin_required
def approve_club_proposal_view(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if request.method == 'POST':
        club.status = Club.Status.ACTIVE
        club.save()
        ActivityLog.log(request.user, f"Approved club creation: {club.name}", category='CLUB')
        messages.success(request, f"Club '{club.name}' has been approved and is now active!")
    return redirect('clubs:requests')


@admin_required
def reject_club_proposal_view(request, pk):
    club = get_object_or_404(Club, pk=pk)
    if request.method == 'POST':
        club_name = club.name
        club.delete()
        ActivityLog.log(request.user, f"Rejected club proposal: {club_name}", category='CLUB')
        messages.info(request, f"Club proposal '{club_name}' was rejected and removed.")
    return redirect('clubs:requests')


@login_required
def my_clubs_view(request):
    user = request.user
    if user.is_coordinator_role:
        clubs = Club.objects.filter(coordinator=user).annotate(
            approved_members=Count('memberships', filter=Q(memberships__status=ClubMembership.Status.APPROVED)),
            pending_members=Count('memberships', filter=Q(memberships__status=ClubMembership.Status.PENDING))
        )
        return render(request, 'clubs/coordinator_clubs.html', {'clubs': clubs})
    elif user.is_student_role:
        memberships = ClubMembership.objects.filter(student=user).select_related('club', 'club__coordinator').order_by('-request_date')
        return render(request, 'clubs/student_clubs.html', {'memberships': memberships})
    else:
        return redirect('clubs:list')
