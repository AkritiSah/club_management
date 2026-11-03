from django import forms
from django.contrib.auth import get_user_model
from .models import Club

User = get_user_model()


class ClubForm(forms.ModelForm):
    coordinator = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.COORDINATOR),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select assigned coordinator"
    )

    class Meta:
        model = Club
        fields = [
            'name', 'category', 'description', 'logo', 'coordinator',
            'established_date', 'max_capacity', 'status', 'meeting_venue', 'contact_email'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Club Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed club description...'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'established_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 10}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'meeting_venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Science Block Audi'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'club@college.edu'}),
        }


class ClubProposalForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'category', 'description', 'logo', 'max_capacity', 'meeting_venue', 'contact_email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proposed Club Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Why should this club be established in our college?'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 10}),
            'meeting_venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proposed meeting location'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@example.com'}),
        }

    def save(self, commit=True):
        club = super().save(commit=False)
        club.status = Club.Status.PENDING
        if commit:
            club.save()
        return club
