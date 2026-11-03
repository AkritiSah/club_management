from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = [StudentProfileInline]

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile Info', {'fields': ('role', 'phone_number', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Profile Info', {'fields': ('role', 'phone_number', 'avatar')}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'department', 'year_of_study')
    list_filter = ('department', 'year_of_study')
    search_fields = ('user__username', 'roll_number', 'user__first_name', 'user__last_name')
