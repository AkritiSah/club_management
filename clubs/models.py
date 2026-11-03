from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Club(models.Model):
    class Category(models.TextChoices):
        TECH = 'TECH', 'Technology & Innovation'
        SCIENCE = 'SCIENCE', 'Academics & Science'
        CULTURAL = 'CULTURAL', 'Arts & Culture'
        CREATIVE = 'CREATIVE', 'Creative Arts & Design'
        SOCIAL = 'SOCIAL', 'Social Service & Community'
        LEADERSHIP = 'LEADERSHIP', 'Discipline & Leadership'
        SPORTS = 'SPORTS', 'Sports & Fitness'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PENDING = 'PENDING', 'Pending Approval'
        INACTIVE = 'INACTIVE', 'Inactive'

    name = models.CharField(max_length=150, unique=True, help_text="Official name of the college club")
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    logo = models.ImageField(upload_to='club_logos/', blank=True, null=True, help_text="Upload club insignia or logo")
    description = models.TextField(help_text="Detailed overview of club mission, activities and goals")
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_clubs',
        help_text="Designated faculty or student coordinator"
    )
    established_date = models.DateField(default=timezone.now, help_text="Date of club foundation")
    max_capacity = models.PositiveIntegerField(default=100, help_text="Maximum allowed student members")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    # Optional metadata
    contact_email = models.EmailField(blank=True, null=True)
    meeting_venue = models.CharField(max_length=150, blank=True, help_text="Regular meeting place (e.g. Lab 402, Audi 1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'College Club'
        verbose_name_plural = 'College Clubs'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.memberships.filter(status='APPROVED').count()

    @property
    def is_full(self):
        return self.member_count >= self.max_capacity

    @property
    def available_slots(self):
        return max(0, self.max_capacity - self.member_count)

    @property
    def capacity_percentage(self):
        if self.max_capacity <= 0:
            return 100
        return min(100, int((self.member_count / self.max_capacity) * 100))

    def get_logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        # Category-based default fallback icons or avatars
        return '/static/images/default-club.png'

    def get_status_badge(self):
        if self.status == self.Status.ACTIVE:
            return 'bg-success'
        elif self.status == self.Status.PENDING:
            return 'bg-warning text-dark'
        return 'bg-secondary'
