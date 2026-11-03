from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError


class ClubEvent(models.Model):
    class Status(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Upcoming'
        ONGOING = 'ONGOING', 'Ongoing'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    title = models.CharField(max_length=200, help_text="Title of the college event")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='events',
        help_text="Organizing college club"
    )
    description = models.TextField(help_text="Full event details, agenda, and guidelines")
    poster = models.ImageField(upload_to='event_posters/', blank=True, null=True, help_text="Event banner or poster image")
    start_date_time = models.DateTimeField(help_text="When the event commences")
    end_date_time = models.DateTimeField(help_text="When the event concludes")
    venue = models.CharField(max_length=200, help_text="Campus location, hall, or virtual link")
    max_participants = models.PositiveIntegerField(default=100, help_text="Maximum registration capacity")
    registration_deadline = models.DateTimeField(help_text="Last date/time to register")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date_time']
        verbose_name = 'Club Event'
        verbose_name_plural = 'Club Events'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while ClubEvent.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def clean(self):
        if self.start_date_time and self.end_date_time and self.end_date_time <= self.start_date_time:
            raise ValidationError("Event end time must be after the start time.")
        if self.registration_deadline and self.start_date_time and self.registration_deadline > self.start_date_time:
            raise ValidationError("Registration deadline must be before the event begins.")

    def __str__(self):
        return f"{self.title} ({self.club.name})"

    @property
    def dynamic_status(self):
        if self.status == self.Status.CANCELLED:
            return self.Status.CANCELLED
        now = timezone.now()
        if now < self.start_date_time:
            return self.Status.UPCOMING
        elif self.start_date_time <= now <= self.end_date_time:
            return self.Status.ONGOING
        else:
            return self.Status.COMPLETED

    @property
    def registered_count(self):
        return self.registrations.filter(status=EventRegistration.Status.REGISTERED).count()

    @property
    def is_full(self):
        return self.registered_count >= self.max_participants

    @property
    def available_seats(self):
        return max(0, self.max_participants - self.registered_count)

    @property
    def is_registration_open(self):
        now = timezone.now()
        if self.status == self.Status.CANCELLED:
            return False
        if now > self.registration_deadline:
            return False
        if self.is_full:
            return False
        return True

    def get_poster_url(self):
        if self.poster and hasattr(self.poster, 'url'):
            return self.poster.url
        return '/static/images/default-event.png'

    def get_status_badge(self):
        status = self.dynamic_status
        if status == self.Status.UPCOMING:
            return 'bg-primary'
        elif status == self.Status.ONGOING:
            return 'bg-warning text-dark'
        elif status == self.Status.COMPLETED:
            return 'bg-secondary'
        return 'bg-danger'


class EventRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'REGISTERED', 'Confirmed Registration'
        ATTENDED = 'ATTENDED', 'Attended'
        CANCELLED = 'CANCELLED', 'Cancelled'

    event = models.ForeignKey(
        ClubEvent,
        on_delete=models.CASCADE,
        related_name='registrations',
        help_text="Registered event"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        help_text="Student registering for the event"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REGISTERED)
    attendance_notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-registered_at']
        unique_together = ('event', 'student')
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'

    def clean(self):
        if not self.pk:
            if not self.event.is_registration_open:
                raise ValidationError("Registration for this event is currently closed or full.")

    def __str__(self):
        return f"{self.student.username} -> {self.event.title} ({self.get_status_display()})"
