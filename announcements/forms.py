from django import forms
from .models import Announcement
from clubs.models import Club


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'club', 'priority', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'}),
            'club': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Announcement text...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_admin_role:
            # Coordinator can only choose their own clubs
            self.fields['club'].queryset = Club.objects.filter(coordinator=user)
            self.fields['club'].empty_label = None
            self.fields['club'].required = True
        else:
            self.fields['club'].empty_label = "-- All Clubs (College-Wide) --"
            self.fields['club'].required = False
