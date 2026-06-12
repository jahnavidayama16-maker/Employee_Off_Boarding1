from django import forms
from django.utils import timezone
from .models import Resignation
import datetime


class ResignationForm(forms.ModelForm):
    class Meta:
        model = Resignation
        fields = ['reason', 'expected_last_day', 'resignation_letter']
        REASON_OPTIONS = (
            ('', '--- Select a Reason ---'),
            ('Switching to a new company / Better Opportunity', 'Switching to a new company / Better Opportunity'),
            ('Relocation', 'Relocation'),
            ('Further Education', 'Further Education'),
            ('Health or Personal Reasons', 'Health or Personal Reasons'),
            ('Dissatisfaction with Role or Salary', 'Dissatisfaction with Role or Salary'),
            ('Other / Not Listed', 'Other / Not Listed'),
        )
        
        widgets = {
            'expected_last_day': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'reason': forms.Select(
                choices=REASON_OPTIONS,
                attrs={
                    'class': 'form-select',
                }
            ),
            'resignation_letter': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx',
            }),
        }
        labels = {
            'reason': 'Reason for Resignation',
            'expected_last_day': 'Expected Last Working Day',
            'resignation_letter': 'Resignation Letter (PDF/DOC)',
        }
        help_texts = {
            'reason': 'Please select the primary reason for your resignation.',
            'expected_last_day': 'Must be at least 14 days from today (standard notice period).',
            'resignation_letter': 'Optional but recommended. Accepted formats: PDF, DOC, DOCX.',
        }

    def clean_expected_last_day(self):
        last_day = self.cleaned_data.get('expected_last_day')
        if last_day:
            today = timezone.now().date()
            min_date = today + datetime.timedelta(days=14)  # 2-week minimum notice
            if last_day <= today:
                raise forms.ValidationError("Expected last day must be in the future.")
            if last_day < min_date:
                raise forms.ValidationError(
                    f"A minimum 14-day notice period is required. Earliest allowed date: {min_date.strftime('%d %B %Y')}."
                )
        return last_day

    def clean_resignation_letter(self):
        letter = self.cleaned_data.get('resignation_letter')
        if letter:
            # Validate file size (max 5MB)
            if letter.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")
            # Validate extension
            name = letter.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.doc') or name.endswith('.docx')):
                raise forms.ValidationError("Only PDF, DOC, or DOCX files are accepted.")
        return letter
