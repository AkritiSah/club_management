from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.paginator import Paginator

from .models import User, StudentProfile
from .forms import (
    StudentRegistrationForm, UserLoginForm, UserProfileUpdateForm,
    StudentProfileUpdateForm, CoordinatorCreationForm
)
from .decorators import admin_required, coordinator_or_admin_required
from dashboard.models import ActivityLog


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            ActivityLog.log(user, "Created new student account", category='AUTH')
            messages.success(request, f"Welcome {user.first_name or user.username}! Your student account has been registered successfully.")
            login(request, user)
            return redirect('dashboard:student')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            ActivityLog.log(user, "Logged in to the system", category='AUTH')
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    ActivityLog.log(request.user, "Logged out of the system", category='AUTH')
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('landing')


@login_required
def profile_view(request):
    user = request.user
    user_form = UserProfileUpdateForm(instance=user)
    student_profile, _ = StudentProfile.objects.get_or_create(user=user)
    student_form = StudentProfileUpdateForm(instance=student_profile) if user.is_student_role else None

    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if user.is_student_role:
            student_form = StudentProfileUpdateForm(request.POST, instance=student_profile)
            if user_form.is_valid() and student_form.is_valid():
                user_form.save()
                student_form.save()
                ActivityLog.log(user, "Updated profile information", category='AUTH')
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('accounts:profile')
        else:
            if user_form.is_valid():
                user_form.save()
                ActivityLog.log(user, "Updated profile information", category='AUTH')
                messages.success(request, "Your profile has been updated successfully.")
                return redirect('accounts:profile')

    context = {
        'user_form': user_form,
        'student_form': student_form,
        'student_profile': student_profile,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            ActivityLog.log(user, "Changed account password", category='AUTH')
            messages.success(request, "Your password was successfully updated!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@admin_required
def coordinator_list_view(request):
    coordinators = User.objects.filter(role=User.Role.COORDINATOR).prefetch_related('coordinated_clubs').order_by('username')
    form = CoordinatorCreationForm()

    if request.method == 'POST':
        form = CoordinatorCreationForm(request.POST)
        if form.is_valid():
            new_coord = form.save()
            ActivityLog.log(request.user, f"Created new coordinator: {new_coord.username}", category='AUTH')
            messages.success(request, f"Coordinator account '{new_coord.username}' created successfully.")
            return redirect('accounts:coordinators')
        else:
            messages.error(request, "Error creating coordinator. Check inputs.")

    context = {
        'coordinators': coordinators,
        'form': form,
    }
    return render(request, 'accounts/coordinator_list.html', context)


@coordinator_or_admin_required
def student_list_view(request):
    query = request.GET.get('q', '').strip()
    department = request.GET.get('dept', '').strip()

    students = User.objects.filter(role=User.Role.STUDENT).select_related('student_profile').prefetch_related('memberships__club').order_by('username')

    if query:
        students = students.filter(
            username__icontains=query
        ) | students.filter(
            first_name__icontains=query
        ) | students.filter(
            last_name__icontains=query
        ) | students.filter(
            student_profile__roll_number__icontains=query
        )

    if department:
        students = students.filter(student_profile__department=department)

    paginator = Paginator(students.distinct(), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = StudentProfile.DEPARTMENT_CHOICES

    context = {
        'page_obj': page_obj,
        'query': query,
        'department': department,
        'departments': departments,
        'total_students': students.distinct().count(),
    }
    return render(request, 'accounts/student_list.html', context)
