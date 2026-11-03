def user_role_context(request):
    if not request.user.is_authenticated:
        return {
            'is_site_admin': False,
            'is_club_coord': False,
            'is_student_user': False,
            'user_role': None,
            'user_coordinated_clubs': [],
            'pending_requests_badge_count': 0,
        }

    user = request.user
    is_admin = user.is_admin_role
    is_coord = user.is_coordinator_role
    is_student = user.is_student_role

    user_coordinated_clubs = []
    pending_count = 0

    if is_coord or is_admin:
        try:
            from clubs.models import Club
            from memberships.models import ClubMembership

            if is_coord:
                user_coordinated_clubs = Club.objects.filter(coordinator=user)
                pending_count = ClubMembership.objects.filter(
                    club__coordinator=user,
                    status=ClubMembership.Status.PENDING
                ).count()
            elif is_admin:
                user_coordinated_clubs = Club.objects.all()
                pending_count = ClubMembership.objects.filter(
                    status=ClubMembership.Status.PENDING
                ).count()
        except Exception:
            pass

    return {
        'is_site_admin': is_admin,
        'is_club_coord': is_coord,
        'is_student_user': is_student,
        'user_role': user.role,
        'user_coordinated_clubs': user_coordinated_clubs,
        'pending_requests_badge_count': pending_count,
    }
