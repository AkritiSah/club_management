from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'priority', 'created_by', 'created_at')
    list_filter = ('priority', 'club', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
