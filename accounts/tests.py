from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, StudentProfile


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(username='admin_test', email='admin@test.com', password='password123', role=User.Role.ADMIN)
        self.coordinator = User.objects.create_user(username='coord_test', email='coord@test.com', password='password123', role=User.Role.COORDINATOR)
        self.student = User.objects.create_user(username='student_test', email='stu@test.com', password='password123', role=User.Role.STUDENT)

    def test_student_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'new_student',
            'email': 'new_stu@college.edu',
            'first_name': 'New',
            'last_name': 'Student',
            'phone_number': '1234567890',
            'roll_number': '23BCS999',
            'department': 'CSE',
            'year_of_study': 1,
            'password': 'Password@123',
            'confirm_password': 'Password@123',
        })
        self.assertEqual(response.status_code, 302)
        new_user = User.objects.get(username='new_student')
        self.assertEqual(new_user.role, User.Role.STUDENT)
        self.assertEqual(new_user.student_profile.roll_number, '23BCS999')

    def test_login_and_logout(self):
        login_resp = self.client.post(reverse('accounts:login'), {
            'username': 'student_test',
            'password': 'password123',
        })
        self.assertEqual(login_resp.status_code, 302)

        logout_resp = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_resp.status_code, 302)

    def test_role_based_access(self):
        # Student cannot access admin dashboard
        self.client.login(username='student_test', password='password123')
        resp = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(resp.status_code, 302)

        # Student cannot access coordinator dashboard
        resp = self.client.get(reverse('dashboard:coordinator'))
        self.assertEqual(resp.status_code, 302)

        # Student CAN access student dashboard
        resp = self.client.get(reverse('dashboard:student'))
        self.assertEqual(resp.status_code, 200)

        # Admin CAN access admin dashboard
        self.client.login(username='admin_test', password='password123')
        resp = self.client.get(reverse('dashboard:admin'))
        self.assertEqual(resp.status_code, 200)
