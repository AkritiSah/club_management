# College Club Management System (CCMS)

A complete, full-stack web application built using **Python Django, HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons, and SQLite**. Designed as an enterprise-grade university project for managing college clubs, student memberships, campus activities, workshops, hackathons, and announcements.

---

## 🌟 Technology Stack

- **Backend**: Python 3.10+, Django 5.2 (MVT architecture)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6)
- **CSS Framework**: Bootstrap 5.3.3 & Bootstrap Icons 1.11.3
- **Database**: SQLite3 (fully normalized relational schema)
- **Image Processing**: Pillow 12.3+ (logos & event posters)
- **Authentication**: Django Custom User Model with Role-Based Access Control (RBAC)

---

## 👥 User Roles & Access Control

### 1. 🛡️ Administrator
- Comprehensive system statistics (students, clubs, coordinators, memberships, events).
- Full CRUD operations on College Clubs.
- Review and Approve/Reject club creation proposals.
- Create and assign Club Coordinators.
- View and search student directory with department and roll numbers.
- View and audit all college-wide memberships and activity logs.
- Direct access to Django Admin panel.

### 2. 🎖️ Club Coordinator
- Dedicated Coordinator Workspace with live metrics.
- Manage assigned club details, logos, description, and capacity.
- Review pending student membership applications (Approve / Reject with custom remarks).
- Create, update, and manage club events (dates, venue, participant limits, registration deadlines).
- View attendee registrations roster and update attendance status.
- Publish club announcements and notices.

### 3. 🎓 Student
- Student registration with Roll Number, Department, Year of Study, and interests.
- Explore active college clubs with search and category filtering.
- Request club membership with duplicate request prevention and capacity checks.
- Live membership status tracking (Pending, Approved, Rejected).
- Browse campus events calendar (Upcoming, Ongoing, Completed).
- Register for events with automatic seat quota and deadline validation.
- Personal tickets history and activity dashboard.
- Submit new club proposals to the Administrator.

---

## 🏛️ Seeded Official College Clubs

The system comes pre-configured with all 6 required clubs:
1. **Hackathon Club** (`TECH`): Technology, 36-hr hackathons, AI/ML workshops, coding competitions.
2. **Science Club** (`SCIENCE`): Academic inquiry, research expos, robotics, stargazing nights.
3. **Cultural Club** (`CULTURAL`): Performing arts, music bands, theater, annual university cultural fest.
4. **Abstract Club** (`CREATIVE`): Visual arts, graphic design, UI/UX prototyping, digital animation.
5. **NSS Club** (`SOCIAL`): National Service Scheme, blood donation camps, village literacy drives.
6. **NCC Club** (`LEADERSHIP`): National Cadet Corps, parade drills, obstacle training, camp certifications.

---

## 🔑 Demonstration Demo Accounts

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full superuser access |
| **Hackathon Coordinator** | `coord_hackathon` | `coord123` | Manages Hackathon Club |
| **Science Coordinator** | `coord_science` | `coord123` | Manages Science Club |
| **Cultural Coordinator** | `coord_cultural` | `coord123` | Manages Cultural Club |
| **Abstract Coordinator** | `coord_abstract` | `coord123` | Manages Abstract Club |
| **NSS Coordinator** | `coord_nss` | `coord123` | Manages NSS Club |
| **NCC Coordinator** | `coord_ncc` | `coord123` | Manages NCC Club |
| **Student (3rd Year CSE)** | `student_rohit` | `student123` | Active member in Hackathon Club |
| **Student (2nd Year ECE)** | `student_priya` | `student123` | Member in Cultural & NSS Clubs |
| **Student (1st Year IT)** | `student_ananya` | `student123` | Member in Abstract Club |
| **Student (4th Year ME)** | `student_rahul` | `student123` | Member in NCC Club |

---

## 🚀 Quick Setup & Execution

### 1. Run Migrations (if setting up fresh)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Seed Initial Demo Data
To populate all 6 clubs, coordinators, events, and sample students:
```bash
python manage.py seed_data
```

### 3. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
**`http://127.0.0.1:8000/`**

### 4. Run Test Suite
```bash
python manage.py test
```

---

## 📂 Project Architecture

```
club_management/
├── config/                  # Django project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   └── views.py             # Landing page view
├── accounts/                # Authentication, profiles, RBAC decorators
│   ├── models.py            # User (AbstractUser), StudentProfile
│   ├── views.py
│   ├── forms.py
│   ├── decorators.py        # @admin_required, @coordinator_required, etc.
│   └── context_processors.py
├── clubs/                   # Club models, CRUD, categories, capacity
│   ├── models.py            # Club
│   ├── views.py
│   ├── forms.py
│   └── templatetags/
├── memberships/             # Membership applications & approvals
│   ├── models.py            # ClubMembership (UniqueConstraint)
│   ├── views.py
│   └── forms.py
├── events/                  # Campus events & registration tickets
│   ├── models.py            # ClubEvent, EventRegistration
│   ├── views.py
│   └── forms.py
├── announcements/           # Notices & bulletins
│   ├── models.py            # Announcement
│   ├── views.py
│   └── forms.py
├── dashboard/               # Role-based dashboards & audit logs
│   ├── models.py            # ActivityLog
│   ├── views.py
│   └── management/commands/seed_data.py
├── static/                  # CSS design system, JS, generated placeholder media
├── templates/               # Responsive HTML templates with Bootstrap 5
├── requirements.txt
└── manage.py
```
