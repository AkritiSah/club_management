from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from clubs.models import Club
from events.models import ClubEvent, EventRegistration


class EventTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = User.objects.create_user(username='coord_ev', password='password123', role=User.Role.COORDINATOR)
        self.student = User.objects.create_user(username='student_ev', password='password123', role=User.Role.STUDENT)

        self.club = Club.objects.create(
            name='Science Club',
            description='Science and research',
            category=Club.Category.SCIENCE,
            coordinator=self.coordinator,
            max_capacity=50,
            status=Club.Status.ACTIVE
        )

        now = timezone.now()
        self.event = ClubEvent.objects.create(
            title='Robotics Expo',
            club=self.club,
            description='Hands-on robotics demo',
            venue='Robotics Lab 101',
            start_date_time=now + timedelta(days=5),
            end_date_time=now + timedelta(days=5, hours=4),
            registration_deadline=now + timedelta(days=4),
            max_participants=2,
            status=ClubEvent.Status.UPCOMING,
            created_by=self.coordinator
        )

    def test_event_registration_and_capacity_limits(self):
        self.client.login(username='student_ev', password='password123')

        # Register student for event
        resp = self.client.post(reverse('events:register', kwargs={'slug': self.event.slug}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(EventRegistration.objects.filter(event=self.event, student=self.student, status=EventRegistration.Status.REGISTERED).exists())

        # Register second student
        stu2 = User.objects.create_user(username='stu2', password='password123', role=User.Role.STUDENT)
        self.client.login(username='stu2', password='password123')
        self.client.post(reverse('events:register', kwargs={'slug': self.event.slug}))

        self.assertEqual(self.event.registered_count, 2)
        self.assertTrue(self.event.is_full)

        # Third student cannot register because event is full
        stu3 = User.objects.create_user(username='stu3', password='password123', role=User.Role.STUDENT)
        self.client.login(username='stu3', password='password123')
        resp_full = self.client.post(reverse('events:register', kwargs={'slug': self.event.slug}))
        self.assertEqual(resp_full.status_code, 302)
        self.assertEqual(self.event.registered_count, 2)
