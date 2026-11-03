from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, StudentProfile
from clubs.models import Club
from memberships.models import ClubMembership
from events.models import ClubEvent, EventRegistration
from announcements.models import Announcement
from dashboard.models import ActivityLog


class Command(BaseCommand):
    help = 'Seeds initial demonstration data: Admin, Coordinators, Students, 6 Required Clubs, Events, and Announcements'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting database seeding for College Club Management System..."))

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@college.edu',
                'first_name': 'College',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '+91 9876543210'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Admin: admin / admin123"))
        else:
            admin_user.role = User.Role.ADMIN
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.set_password('admin123')
            admin_user.save()

        # 2. Create Coordinators
        coordinators_data = [
            ('coord_hackathon', 'Dr. Arvind', 'Kumar', 'arvind@college.edu', 'Hackathon Club Coordinator', '+91 9811111111'),
            ('coord_science', 'Prof. Sunita', 'Sharma', 'sunita@college.edu', 'Science Club Faculty Lead', '+91 9822222222'),
            ('coord_cultural', 'Dr. Meera', 'Nair', 'meera@college.edu', 'Cultural Activities Head', '+91 9833333333'),
            ('coord_abstract', 'Prof. Rohan', 'Verma', 'rohan@college.edu', 'Design & Arts Mentor', '+91 9844444444'),
            ('coord_nss', 'Dr. Rajesh', 'Gupta', 'rajesh@college.edu', 'NSS Program Officer', '+91 9855555555'),
            ('coord_ncc', 'Lt. Col. Vikram', 'Singh', 'vikram@college.edu', 'NCC Associate Officer', '+91 9866666666'),
        ]

        coord_objs = {}
        for username, fname, lname, email, bio, phone in coordinators_data:
            coord, c_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'role': User.Role.COORDINATOR,
                    'phone_number': phone,
                }
            )
            coord.set_password('coord123')
            coord.role = User.Role.COORDINATOR
            coord.save()
            coord_objs[username] = coord
        self.stdout.write(self.style.SUCCESS("Created 6 Coordinators (password: coord123)"))

        # 3. Create Students
        students_data = [
            ('student_rohit', 'Rohit', 'Sharma', 'rohit@student.college.edu', '21BCS101', 'CSE', 3, 'Full-stack enthusiast, hackathon participant, loves Python and AI.'),
            ('student_priya', 'Priya', 'Patel', 'priya@student.college.edu', '22BEC204', 'ECE', 2, 'Robotics buff, cultural dancer, social volunteer.'),
            ('student_ananya', 'Ananya', 'Iyer', 'ananya@student.college.edu', '23BIT305', 'IT', 1, 'UI/UX designer, digital artist, eager to learn abstract creative tools.'),
            ('student_rahul', 'Rahul', 'Verma', 'rahul@student.college.edu', '20BME408', 'ME', 4, 'NCC Cadet, athletics champion, fitness mentor.'),
        ]

        student_objs = {}
        for username, fname, lname, email, roll, dept, year, bio in students_data:
            stu, s_created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': email,
                    'role': User.Role.STUDENT,
                    'phone_number': '+91 9988776655',
                }
            )
            stu.set_password('student123')
            stu.role = User.Role.STUDENT
            stu.save()
            profile, _ = StudentProfile.objects.get_or_create(user=stu)
            profile.roll_number = roll
            profile.department = dept
            profile.year_of_study = year
            profile.bio = bio
            profile.interests = "Technology, Design, Social Work, Sports"
            profile.save()
            student_objs[username] = stu
        self.stdout.write(self.style.SUCCESS("Created 4 Sample Students (password: student123)"))

        # 4. Create the 6 Required Clubs
        now = timezone.now()
        clubs_specs = [
            {
                'name': 'Hackathon Club',
                'category': Club.Category.TECH,
                'coordinator': coord_objs['coord_hackathon'],
                'description': 'The premier technology and innovation forum on campus. We host intensive 24 to 36-hour hackathons, algorithmic coding sprints, open-source cohorts, and hands-on workshops in web development, AI/ML, and cloud computing.',
                'max_capacity': 120,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'Turing Innovation Lab, Block 3',
                'contact_email': 'hackathons@college.edu',
                'established_date': now.date() - timedelta(days=1200),
            },
            {
                'name': 'Science Club',
                'category': Club.Category.SCIENCE,
                'coordinator': coord_objs['coord_science'],
                'description': 'Dedicated to fostering scientific temperament, academic inquiry, and multidisciplinary research. We organize science exhibitions, astronomy nights, drone building, and scholarly guest lectures.',
                'max_capacity': 100,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'C.V. Raman Science Hall, Room 204',
                'contact_email': 'scienceclub@college.edu',
                'established_date': now.date() - timedelta(days=1500),
            },
            {
                'name': 'Cultural Club',
                'category': Club.Category.CULTURAL,
                'coordinator': coord_objs['coord_cultural'],
                'description': 'The heartbeat of campus vibrance and performing arts. Encompassing dance troupes, classical and western music bands, theatrical drama, poetry slams, and the grand annual inter-college cultural fest.',
                'max_capacity': 150,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'Main Campus Auditorium & Amphitheatre',
                'contact_email': 'cultural@college.edu',
                'established_date': now.date() - timedelta(days=1800),
            },
            {
                'name': 'Abstract Club',
                'category': Club.Category.CREATIVE,
                'coordinator': coord_objs['coord_abstract'],
                'description': 'A nexus for visual arts, graphic design, UI/UX prototyping, digital illustration, and photography. We believe in thinking outside boundaries and expressing emotions through visual aesthetics.',
                'max_capacity': 80,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'Design Studio & Media Lab, 4th Floor',
                'contact_email': 'abstract.arts@college.edu',
                'established_date': now.date() - timedelta(days=900),
            },
            {
                'name': 'NSS Club',
                'category': Club.Category.SOCIAL,
                'coordinator': coord_objs['coord_nss'],
                'description': 'National Service Scheme (NSS) Club embodying the motto "Not Me But You". Our volunteers lead blood donation drives, literacy outreach in adopted villages, environmental green campaigns, and disaster relief.',
                'max_capacity': 200,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'NSS Activity Center, Student Activity Block',
                'contact_email': 'nss@college.edu',
                'established_date': now.date() - timedelta(days=2500),
            },
            {
                'name': 'NCC Club',
                'category': Club.Category.LEADERSHIP,
                'coordinator': coord_objs['coord_ncc'],
                'description': 'National Cadet Corps (NCC) Unit fostering character, comradeship, discipline, secular outlook, spirit of adventure, and ideals of selfless service among students. Regular parade drills, firing practice, and obstacle training.',
                'max_capacity': 120,
                'status': Club.Status.ACTIVE,
                'meeting_venue': 'NCC Parade Ground & Armory Wing',
                'contact_email': 'ncc@college.edu',
                'established_date': now.date() - timedelta(days=3000),
            },
        ]

        club_objs = {}
        for spec in clubs_specs:
            name = spec.pop('name')
            club, cl_created = Club.objects.update_or_create(
                name=name,
                defaults=spec
            )
            club_objs[name] = club
        self.stdout.write(self.style.SUCCESS("Created/Updated 6 Required Clubs"))

        # 5. Memberships
        memberships_seed = [
            (student_objs['student_rohit'], club_objs['Hackathon Club'], ClubMembership.Status.APPROVED, 'Very eager to contribute to coding competitions.'),
            (student_objs['student_rohit'], club_objs['Science Club'], ClubMembership.Status.PENDING, 'Interested in AI research team.'),
            (student_objs['student_priya'], club_objs['Cultural Club'], ClubMembership.Status.APPROVED, 'Classical dance soloist and event organizer.'),
            (student_objs['student_priya'], club_objs['NSS Club'], ClubMembership.Status.APPROVED, 'Regular volunteer for campus cleanliness drives.'),
            (student_objs['student_ananya'], club_objs['Abstract Club'], ClubMembership.Status.APPROVED, 'Figma designer and creative artist.'),
            (student_objs['student_ananya'], club_objs['Hackathon Club'], ClubMembership.Status.PENDING, 'Want to design UI/UX for hackathon projects.'),
            (student_objs['student_rahul'], club_objs['NCC Club'], ClubMembership.Status.APPROVED, 'Senior cadet candidate, passed A-certificate.'),
            (student_objs['student_rahul'], club_objs['NSS Club'], ClubMembership.Status.PENDING, 'Willing to coordinate medical camp logistics.'),
        ]

        for stu, club, status, rem in memberships_seed:
            mem, _ = ClubMembership.objects.get_or_create(
                student=stu,
                club=club,
                defaults={
                    'status': status,
                    'remarks': rem,
                    'decision_date': now if status == ClubMembership.Status.APPROVED else None,
                    'reviewed_by': club.coordinator if status == ClubMembership.Status.APPROVED else None
                }
            )
            mem.status = status
            mem.save()
        self.stdout.write(self.style.SUCCESS("Created Sample Club Memberships (Approved & Pending)"))

        # 6. Events
        events_specs = [
            {
                'title': 'CodeStorm 2026: 36-Hour National Hackathon',
                'club': club_objs['Hackathon Club'],
                'description': 'Join the largest university hackathon of the season! Innovate in AI, Web3, Healthcare, and Smart City automation with mentors from top tech giants. Win prizes worth Rs 2,50,000!',
                'venue': 'Main Indoor Sports Complex & High-Tech Labs',
                'start_date_time': now + timedelta(days=14, hours=10),
                'end_date_time': now + timedelta(days=15, hours=22),
                'registration_deadline': now + timedelta(days=12),
                'max_participants': 250,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_hackathon'],
            },
            {
                'title': 'National Science Day: Robotics & Innovation Expo',
                'club': club_objs['Science Club'],
                'description': 'Annual science exhibition featuring line-follower bots, solar power working models, and drone displays. Special keynote by ISRO scientist.',
                'venue': 'Science Quadrangle & Lab Pavilion',
                'start_date_time': now + timedelta(days=21, hours=9),
                'end_date_time': now + timedelta(days=21, hours=17),
                'registration_deadline': now + timedelta(days=18),
                'max_participants': 150,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_science'],
            },
            {
                'title': 'Tarang: Annual Inter-College Cultural Carnival',
                'club': club_objs['Cultural Club'],
                'description': 'Three days of non-stop dance face-offs, battle of the bands, standup comedy, fashion shows, and celebrity musical night!',
                'venue': 'University Grand Open Air Amphitheatre',
                'start_date_time': now + timedelta(days=30, hours=16),
                'end_date_time': now + timedelta(days=32, hours=23),
                'registration_deadline': now + timedelta(days=25),
                'max_participants': 500,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_cultural'],
            },
            {
                'title': 'Abstract Canvas: UI/UX Prototyping Workshop',
                'club': club_objs['Abstract Club'],
                'description': 'A masterclass on user psychology, interactive micro-interactions, Figma component libraries, and portfolio presentation for design careers.',
                'venue': 'Multimedia Lab 402',
                'start_date_time': now + timedelta(days=8, hours=14),
                'end_date_time': now + timedelta(days=8, hours=18),
                'registration_deadline': now + timedelta(days=6),
                'max_participants': 60,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_abstract'],
            },
            {
                'title': 'Campus Mega Blood Donation Camp & Health Checkup',
                'club': club_objs['NSS Club'],
                'description': 'In collaboration with the District Red Cross Blood Bank. Every donor receives an official donor certificate, health card, and refreshment package.',
                'venue': 'Student Center Ground Floor',
                'start_date_time': now + timedelta(days=10, hours=9),
                'end_date_time': now + timedelta(days=10, hours=16),
                'registration_deadline': now + timedelta(days=9),
                'max_participants': 300,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_nss'],
            },
            {
                'title': 'Combined Cadet Training Camp & Firing Drills',
                'club': club_objs['NCC Club'],
                'description': 'Rigorous drill rehearsals, weapon handling safety demonstration, map reading practice, and obstacle crossing for B and C certificate aspirants.',
                'venue': 'Campus NCC Grounds & Obstacle Course',
                'start_date_time': now + timedelta(days=18, hours=6),
                'end_date_time': now + timedelta(days=18, hours=15),
                'registration_deadline': now + timedelta(days=15),
                'max_participants': 100,
                'status': ClubEvent.Status.UPCOMING,
                'created_by': coord_objs['coord_ncc'],
            },
            {
                'title': 'Python & Open Source Starter Bootcamp',
                'club': club_objs['Hackathon Club'],
                'description': 'Completed introductory bootcamp for freshers covering Git, GitHub workflows, and building Django applications.',
                'venue': 'Virtual Seminar Hall',
                'start_date_time': now - timedelta(days=15, hours=10),
                'end_date_time': now - timedelta(days=15, hours=16),
                'registration_deadline': now - timedelta(days=17),
                'max_participants': 120,
                'status': ClubEvent.Status.COMPLETED,
                'created_by': coord_objs['coord_hackathon'],
            },
        ]

        event_objs = []
        for espec in events_specs:
            title = espec.pop('title')
            ev, _ = ClubEvent.objects.update_or_create(
                title=title,
                defaults=espec
            )
            event_objs.append(ev)
        self.stdout.write(self.style.SUCCESS("Created Sample Upcoming and Completed Events"))

        # 7. Event Registrations
        ev_codestorm = event_objs[0]
        ev_python_bootcamp = event_objs[6]
        ev_blood_camp = event_objs[4]

        EventRegistration.objects.get_or_create(
            event=ev_codestorm,
            student=student_objs['student_rohit'],
            defaults={'status': EventRegistration.Status.REGISTERED}
        )
        EventRegistration.objects.get_or_create(
            event=ev_codestorm,
            student=student_objs['student_ananya'],
            defaults={'status': EventRegistration.Status.REGISTERED}
        )
        EventRegistration.objects.get_or_create(
            event=ev_blood_camp,
            student=student_objs['student_priya'],
            defaults={'status': EventRegistration.Status.REGISTERED}
        )
        EventRegistration.objects.get_or_create(
            event=ev_python_bootcamp,
            student=student_objs['student_rohit'],
            defaults={'status': EventRegistration.Status.ATTENDED, 'attendance_notes': 'Awarded Certificate of Merit'}
        )
        self.stdout.write(self.style.SUCCESS("Created Sample Event Registrations"))

        # 8. Announcements
        announcements_seed = [
            (None, 'Welcome to the New Academic Semester Club Portal!', 'All students are encouraged to explore college clubs, register for events, and apply for memberships through this portal.', Announcement.Priority.HIGH, admin_user),
            (club_objs['Hackathon Club'], 'CodeStorm 2026 Problem Statements Released', 'Problem statements for FinTech, EduTech, and ClimateTech categories have been posted. Team formations can now begin.', Announcement.Priority.URGENT, coord_objs['coord_hackathon']),
            (club_objs['Science Club'], 'Call for Robotics Expo Working Models', 'Interested students can submit project abstracts to Science Club committee before Friday.', Announcement.Priority.NORMAL, coord_objs['coord_science']),
            (club_objs['NSS Club'], 'Volunteer Orientation Session this Wednesday', 'All newly approved NSS members are requested to attend the orientation session in the Student Center at 4:30 PM.', Announcement.Priority.HIGH, coord_objs['coord_nss']),
            (club_objs['Abstract Club'], 'Graphic Asset Kit for Hackathon Available', 'Our design team has released open-source stickers and presentation slide decks for campus innovators.', Announcement.Priority.NORMAL, coord_objs['coord_abstract']),
        ]

        for club, title, content, priority, author in announcements_seed:
            Announcement.objects.get_or_create(
                title=title,
                defaults={
                    'club': club,
                    'content': content,
                    'priority': priority,
                    'created_by': author,
                }
            )
        self.stdout.write(self.style.SUCCESS("Created Sample Announcements"))

        # 9. Activity Log entries
        ActivityLog.objects.get_or_create(
            user=admin_user,
            action="System initialized with baseline college clubs and coordinators",
            category='CLUB'
        )
        ActivityLog.objects.get_or_create(
            user=student_objs['student_rohit'],
            action="Registered for CodeStorm 2026: 36-Hour National Hackathon",
            category='EVENT'
        )

        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("  DATABASE SEEDING COMPLETE! READY FOR DEMONSTRATION!  "))
        self.stdout.write(self.style.SUCCESS("========================================================"))
        self.stdout.write(self.style.SUCCESS("Credentials for Testing:"))
        self.stdout.write(self.style.SUCCESS("  - Administrator:  admin / admin123"))
        self.stdout.write(self.style.SUCCESS("  - Coordinators:   coord_hackathon / coord123 (and science, cultural, abstract, nss, ncc)"))
        self.stdout.write(self.style.SUCCESS("  - Students:       student_rohit / student123 (and priya, ananya, rahul)"))
        self.stdout.write(self.style.SUCCESS("========================================================\n"))
