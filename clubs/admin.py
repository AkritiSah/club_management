from django.contrib import admin
from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'coordinator', 'max_capacity', 'status', 'established_date')
    list_filter = ('category', 'status', 'established_date')
    search_fields = ('name', 'description', 'coordinator__username')
    prepopulated_fields = {'slug': ('name',)}
