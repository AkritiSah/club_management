from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from clubs.models import Club
from dashboard.models import ActivityLog


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin_dash', password='password123', role=User.Role.ADMIN)
        self.coordinator = User.objects.create_user(username='coord_dash', password='password123', role=User.Role.COORDINATOR)
        self.student = User.objects.create_user(username='student_dash', password='password123', role=User.Role.STUDENT)
        self.club = Club.objects.create(name='Abstract Club', coordinator=self.coordinator)

    def test_dashboard_redirector(self):
        # Admin redirects to admin dashboard
        self.client.login(username='admin_dash', password='password123')
        resp = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(resp, reverse('dashboard:admin'))

        # Coordinator redirects to coordinator dashboard
        self.client.login(username='coord_dash', password='password123')
        resp = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(resp, reverse('dashboard:coordinator'))

        # Student redirects to student dashboard
        self.client.login(username='student_dash', password='password123')
        resp = self.client.get(reverse('dashboard:index'))
        self.assertRedirects(resp, reverse('dashboard:student'))

    def test_activity_logging(self):
        ActivityLog.log(self.student, "Viewed club details", category='CLUB')
        self.assertEqual(ActivityLog.objects.filter(user=self.student).count(), 1)
