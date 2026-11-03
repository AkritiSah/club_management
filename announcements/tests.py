from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from clubs.models import Club
from announcements.models import Announcement


class AnnouncementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.coordinator = User.objects.create_user(username='coord_ann', password='password123', role=User.Role.COORDINATOR)
        self.student = User.objects.create_user(username='student_ann', password='password123', role=User.Role.STUDENT)
        self.club = Club.objects.create(name='Cultural Club', description='Arts', coordinator=self.coordinator)

    def test_create_and_view_announcement(self):
        self.client.login(username='coord_ann', password='password123')
        resp = self.client.post(reverse('announcements:create'), {
            'title': 'Auditions for Annual Play',
            'club': self.club.id,
            'priority': Announcement.Priority.HIGH,
            'content': 'Auditions will be held on Thursday in the Audi.',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Announcement.objects.filter(title='Auditions for Annual Play').exists())

        # Student views announcement
        self.client.login(username='student_ann', password='password123')
        resp_list = self.client.get(reverse('announcements:list'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, 'Auditions for Annual Play')
