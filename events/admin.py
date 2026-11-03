from django.contrib import admin
from .models import ClubEvent, EventRegistration


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'venue', 'start_date_time', 'max_participants', 'status')
    list_filter = ('status', 'club', 'start_date_time')
    search_fields = ('title', 'description', 'venue', 'club__name')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'status', 'registered_at')
    list_filter = ('status', 'event__club', 'registered_at')
    search_fields = ('student__username', 'event__title')
