from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from .models import ClubMembership
from .forms import MembershipRequestForm, MembershipReviewForm
from clubs.models import Club
from accounts.decorators import admin_required, coordinator_or_admin_required, student_required
from dashboard.models import ActivityLog


@login_required
def request_membership_view(request, club_slug):
    club = get_object_or_404(Club, slug=club_slug)

    if club.status != Club.Status.ACTIVE:
        messages.error(request, "This club is currently not accepting new members.")
        return redirect('clubs:detail', slug=club.slug)

    # Check existing membership
    existing = ClubMembership.objects.filter(student=request.user, club=club).first()
    if existing:
        if existing.status == ClubMembership.Status.APPROVED:
            messages.info(request, f"You are already an active member of {club.name}.")
        elif existing.status == ClubMembership.Status.PENDING:
            messages.warning(request, f"Your membership request for {club.name} is currently pending review.")
        else:
            messages.info(request, f"Your previous request was rejected. You may contact the coordinator.")
        return redirect('clubs:detail', slug=club.slug)

    if club.is_full:
        messages.error(request, f"Sorry, {club.name} has reached its maximum member capacity of {club.max_capacity}.")
        return redirect('clubs:detail', slug=club.slug)

    if request.method == 'POST':
        form = MembershipRequestForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.student = request.user
            membership.club = club
            membership.status = ClubMembership.Status.PENDING
            membership.save()
            ActivityLog.log(request.user, f"Requested to join club: {club.name}", category='MEMBERSHIP')
            messages.success(request, f"Membership request submitted for {club.name}! You will be notified once reviewed.")
            return redirect('memberships:my_memberships')
    else:
        form = MembershipRequestForm()

    context = {
        'club': club,
        'form': form,
    }
    return render(request, 'memberships/request_membership.html', context)


@login_required
def cancel_membership_view(request, pk):
    membership = get_object_or_404(ClubMembership, pk=pk, student=request.user)
    if request.method == 'POST':
        club_name = membership.club.name
        membership.delete()
        ActivityLog.log(request.user, f"Cancelled membership for {club_name}", category='MEMBERSHIP')
        messages.info(request, f"Your membership for {club_name} has been cancelled.")
    return redirect('memberships:my_memberships')


@login_required
def club_members_view(request, club_slug):
    club = get_object_or_404(Club, slug=club_slug)

    # Permission check: Admin or assigned coordinator
    if not (request.user.is_admin_role or (request.user.is_coordinator_role and club.coordinator == request.user)):
        messages.error(request, "You are not authorized to view the management members list for this club.")
        return redirect('clubs:detail', slug=club.slug)

    status_filter = request.GET.get('status', 'PENDING')
    memberships = ClubMembership.objects.filter(club=club).select_related('student', 'student__student_profile', 'reviewed_by')

    if status_filter in ['PENDING', 'APPROVED', 'REJECTED']:
        memberships = memberships.filter(status=status_filter)

    paginator = Paginator(memberships, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    counts = {
        'PENDING': ClubMembership.objects.filter(club=club, status=ClubMembership.Status.PENDING).count(),
        'APPROVED': ClubMembership.objects.filter(club=club, status=ClubMembership.Status.APPROVED).count(),
        'REJECTED': ClubMembership.objects.filter(club=club, status=ClubMembership.Status.REJECTED).count(),
        'TOTAL': ClubMembership.objects.filter(club=club).count(),
    }

    context = {
        'club': club,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'counts': counts,
    }
    return render(request, 'memberships/club_members.html', context)


@login_required
def approve_membership_view(request, pk):
    membership = get_object_or_404(ClubMembership.objects.select_related('club'), pk=pk)
    club = membership.club

    if not (request.user.is_admin_role or (request.user.is_coordinator_role and club.coordinator == request.user)):
        messages.error(request, "Permission denied.")
        return redirect('dashboard:index')

    if club.is_full and membership.status != ClubMembership.Status.APPROVED:
        messages.error(request, f"Cannot approve! {club.name} has reached maximum capacity ({club.max_capacity}).")
        return redirect('memberships:club_members', club_slug=club.slug)

    if request.method == 'POST':
        remarks = request.POST.get('remarks', 'Approved by coordinator.')
        membership.approve(reviewer=request.user, remarks=remarks)
        ActivityLog.log(request.user, f"Approved membership for {membership.student.username} in {club.name}", category='MEMBERSHIP')
        messages.success(request, f"Approved membership for {membership.student.get_full_name() or membership.student.username}!")

    return redirect('memberships:club_members', club_slug=club.slug)


@login_required
def reject_membership_view(request, pk):
    membership = get_object_or_404(ClubMembership.objects.select_related('club'), pk=pk)
    club = membership.club

    if not (request.user.is_admin_role or (request.user.is_coordinator_role and club.coordinator == request.user)):
        messages.error(request, "Permission denied.")
        return redirect('dashboard:index')

    if request.method == 'POST':
        remarks = request.POST.get('remarks', 'Membership request rejected.')
        membership.reject(reviewer=request.user, remarks=remarks)
        ActivityLog.log(request.user, f"Rejected membership for {membership.student.username} in {club.name}", category='MEMBERSHIP')
        messages.info(request, f"Rejected membership request for {membership.student.username}.")

    return redirect('memberships:club_members', club_slug=club.slug)


@login_required
def my_memberships_view(request):
    memberships = ClubMembership.objects.filter(student=request.user).select_related('club', 'club__coordinator').order_by('-request_date')
    return render(request, 'memberships/my_memberships.html', {'memberships': memberships})


@admin_required
def all_memberships_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    club_filter = request.GET.get('club', '').strip()

    memberships = ClubMembership.objects.select_related('student', 'student__student_profile', 'club', 'reviewed_by').order_by('-request_date')

    if query:
        memberships = memberships.filter(
            student__username__icontains=query
        ) | memberships.filter(
            student__first_name__icontains=query
        ) | memberships.filter(
            club__name__icontains=query
        )

    if status_filter:
        memberships = memberships.filter(status=status_filter)

    if club_filter:
        memberships = memberships.filter(club_id=club_filter)

    paginator = Paginator(memberships, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    clubs = Club.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'club_filter': club_filter,
        'clubs': clubs,
        'total_memberships': memberships.count(),
    }
    return render(request, 'memberships/all_memberships.html', context)
