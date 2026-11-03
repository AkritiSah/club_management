from django.db import models
from django.conf import settings


class ActivityLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=255, help_text="Summary of action performed")
    category = models.CharField(
        max_length=50,
        choices=[
            ('MEMBERSHIP', 'Membership'),
            ('EVENT', 'Event'),
            ('CLUB', 'Club'),
            ('ANNOUNCEMENT', 'Announcement'),
            ('AUTH', 'Authentication'),
        ],
        default='MEMBERSHIP'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"{self.user.username}: {self.action} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

    @classmethod
    def log(cls, user, action, category='MEMBERSHIP'):
        if user and user.is_authenticated:
            cls.objects.create(user=user, action=action, category=category)
