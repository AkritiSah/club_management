from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'category', 'timestamp')
    list_filter = ('category', 'timestamp')
    search_fields = ('user__username', 'action')
