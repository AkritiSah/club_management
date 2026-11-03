from django.contrib import admin
from .models import ClubMembership


@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'club', 'status', 'request_date', 'decision_date', 'reviewed_by')
    list_filter = ('status', 'club', 'request_date')
    search_fields = ('student__username', 'club__name', 'remarks')
