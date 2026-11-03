from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        COORDINATOR = 'COORDINATOR', 'Club Coordinator'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Designates the role and permission level for this user."
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_coordinator_role(self):
        return self.role == self.Role.COORDINATOR

    @property
    def is_student_role(self):
        return self.role == self.Role.STUDENT

    def get_role_badge_class(self):
        if self.is_admin_role:
            return 'bg-danger'
        elif self.is_coordinator_role:
            return 'bg-primary'
        return 'bg-success'

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def __str__(self):
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        return f"{display} ({self.get_role_display()})"


class StudentProfile(models.Model):
    YEAR_CHOICES = [
        (1, '1st Year (Freshman)'),
        (2, '2nd Year (Sophomore)'),
        (3, '3rd Year (Junior)'),
        (4, '4th Year (Senior)'),
    ]

    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science & Engineering'),
        ('IT', 'Information Technology'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EE', 'Electrical Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('BT', 'Biotechnology'),
        ('BBA', 'Business Administration'),
        ('OTHER', 'Other Department'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='CSE')
    year_of_study = models.PositiveSmallIntegerField(choices=YEAR_CHOICES, default=1)
    bio = models.TextField(blank=True, help_text="Brief student bio or statement of purpose")
    interests = models.CharField(max_length=255, blank=True, help_text="Comma-separated interests (e.g. Coding, Robotics, Debate)")

    def __str__(self):
        return f"Profile of {self.user.username} - {self.roll_number or 'No Roll No'}"


@receiver(post_save, sender=User)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.STUDENT:
        StudentProfile.objects.get_or_create(user=instance)
