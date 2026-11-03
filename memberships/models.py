from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class ClubMembership(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved Member'
        REJECTED = 'REJECTED', 'Rejected'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="Student who submitted the membership request"
    )
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='memberships',
        help_text="Club being joined"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    request_date = models.DateTimeField(auto_now_add=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_memberships'
    )
    remarks = models.TextField(blank=True, help_text="Reason for approval/rejection or coordinator notes")

    class Meta:
        ordering = ['-request_date']
        # Prevent duplicate requests by the same student for the same club
        unique_together = ('student', 'club')
        verbose_name = 'Club Membership'
        verbose_name_plural = 'Club Memberships'

    def clean(self):
        # Validate that user is indeed a student (or allow admin/coords for testing)
        if self.status == self.Status.APPROVED and self.club.is_full and not self.pk:
            raise ValidationError(f"Cannot join {self.club.name}. Maximum membership capacity ({self.club.max_capacity}) reached.")

    def approve(self, reviewer=None, remarks=''):
        self.status = self.Status.APPROVED
        self.decision_date = timezone.now()
        if reviewer:
            self.reviewed_by = reviewer
        if remarks:
            self.remarks = remarks
        self.save()

    def reject(self, reviewer=None, remarks=''):
        self.status = self.Status.REJECTED
        self.decision_date = timezone.now()
        if reviewer:
            self.reviewed_by = reviewer
        if remarks:
            self.remarks = remarks
        self.save()

    def get_status_badge(self):
        if self.status == self.Status.APPROVED:
            return 'bg-success'
        elif self.status == self.Status.PENDING:
            return 'bg-warning text-dark'
        return 'bg-danger'

    def __str__(self):
        return f"{self.student.username} -> {self.club.name} [{self.get_status_display()}]"
