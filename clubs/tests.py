from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User
from clubs.models import Club
from memberships.models import ClubMembership


class ClubAndMembershipTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin_u', email='admin@u.com', password='password123', role=User.Role.ADMIN)
        self.coordinator = User.objects.create_user(username='coord_u', email='coord@u.com', password='password123', role=User.Role.COORDINATOR)
        self.student = User.objects.create_user(username='student_u', email='student@u.com', password='password123', role=User.Role.STUDENT)

        self.club = Club.objects.create(
            name='Hackathon Club',
            description='Tech club',
            category=Club.Category.TECH,
            coordinator=self.coordinator,
            max_capacity=50,
            status=Club.Status.ACTIVE
        )

    def test_club_list_and_detail(self):
        resp = self.client.get(reverse('clubs:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Hackathon Club')

        resp_detail = self.client.get(reverse('clubs:detail', kwargs={'slug': self.club.slug}))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, 'Hackathon Club')

    def test_membership_request_and_duplicate_prevention(self):
        self.client.login(username='student_u', password='password123')
        
        # Submit membership request
        resp = self.client.post(reverse('memberships:request', kwargs={'club_slug': self.club.slug}), {
            'remarks': 'Excited to join!'
        })
        self.assertEqual(resp.status_code, 302)
        
        # Check membership was created as PENDING
        mem = ClubMembership.objects.get(student=self.student, club=self.club)
        self.assertEqual(mem.status, ClubMembership.Status.PENDING)

        # Attempt duplicate request - should redirect and warn
        resp_dup = self.client.post(reverse('memberships:request', kwargs={'club_slug': self.club.slug}), {
            'remarks': 'Duplicate attempt'
        })
        self.assertEqual(resp_dup.status_code, 302)
        self.assertEqual(ClubMembership.objects.filter(student=self.student, club=self.club).count(), 1)

    def test_coordinator_approval_workflow(self):
        mem = ClubMembership.objects.create(
            student=self.student,
            club=self.club,
            status=ClubMembership.Status.PENDING
        )

        # Coordinator approves
        self.client.login(username='coord_u', password='password123')
        resp = self.client.post(reverse('memberships:approve', kwargs={'pk': mem.id}), {
            'remarks': 'Welcome to Hackathon Club!'
        })
        self.assertEqual(resp.status_code, 302)

        mem.refresh_from_db()
        self.assertEqual(mem.status, ClubMembership.Status.APPROVED)
        self.assertEqual(self.club.member_count, 1)
