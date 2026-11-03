from django import forms
from .models import ClubMembership


class MembershipRequestForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Why do you want to join this club? Share your interest and relevant skills...'
            }),
        }
        labels = {
            'remarks': 'Statement of Interest (Optional)',
        }


class MembershipReviewForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Feedback or reason for decision...'
            }),
        }
