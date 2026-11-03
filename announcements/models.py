from django.db import models
from django.conf import settings


class Announcement(models.Model):
    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        HIGH = 'HIGH', 'High Priority'
        URGENT = 'URGENT', 'Urgent Announcement'

    title = models.CharField(max_length=200, help_text="Announcement headline")
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='announcements',
        null=True,
        blank=True,
        help_text="Associated club (Leave blank for College-Wide announcement)"
    )
    content = models.TextField(help_text="Detailed announcement body")
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posted_announcements'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'

    def __str__(self):
        club_tag = f"[{self.club.name}]" if self.club else "[College-Wide]"
        return f"{club_tag} {self.title}"

    def get_priority_badge(self):
        if self.priority == self.Priority.URGENT:
            return 'bg-danger text-white'
        elif self.priority == self.Priority.HIGH:
            return 'bg-warning text-dark'
        return 'bg-info text-dark'
