from django import forms
from .models import ClubEvent, EventRegistration
from clubs.models import Club


class ClubEventForm(forms.ModelForm):
    class Meta:
        model = ClubEvent
        fields = [
            'title', 'club', 'description', 'poster',
            'start_date_time', 'end_date_time', 'venue',
            'max_participants', 'registration_deadline', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'club': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Event details, agenda, and instructions...'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
            'start_date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Auditorium 2 or Online (Meet link)'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_admin_role:
            # Filter clubs only to ones this coordinator manages
            self.fields['club'].queryset = Club.objects.filter(coordinator=user)


class EventAttendanceForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['status', 'attendance_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'attendance_notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Notes (e.g. Winner, Participated)'}),
        }
