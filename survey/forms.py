"""Forms for the survey application."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Survey, SurveyInvitation, SurveyResponse, StrengthRanking, OpportunityRanking
from .utils import get_question_texts, get_strength_choices, get_opportunity_choices
from datetime import datetime, timedelta


class AdminLoginForm(AuthenticationForm):
    """Custom login form for admin interface."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CreateSurveyForm(forms.ModelForm):
    """Form for creating a new survey."""
    class Meta:
        model = Survey
        fields = ['title', 'leader_name', 'leader_email']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter survey title'
            }),
            'leader_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter leader name'
            }),
            'leader_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter leader email'
            }),
        }


class InvitationForm(forms.Form):
    """Form for sending survey invitations."""
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter email addresses (one per line)'
        }),
        help_text='Enter participant email addresses, one per line'
    )
    expires_at = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        initial=lambda: datetime.now() + timedelta(days=14),
        help_text='Set expiration date for survey links'
    )
    
    def clean_emails(self):
        """Clean and validate email addresses."""
        emails_text = self.cleaned_data['emails']
        emails = []
        
        for line in emails_text.split('\n'):
            email = line.strip()
            if email:
                # Basic email validation
                if '@' not in email or '.' not in email.split('@')[1]:
                    raise forms.ValidationError(f"Invalid email address: {email}")
                emails.append(email.lower())
        
        if not emails:
            raise forms.ValidationError("Please enter at least one email address")
        
        return emails


class LeaderSelfAssessmentForm(forms.ModelForm):
    """Form for leader self-assessment."""
    
    # Dynamic fields for strengths and opportunities
    strengths = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'strength-checkbox'}),
        required=True,
        label="Select your top 5 strengths (you will rank them next)"
    )
    
    opportunities = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'opportunity-checkbox'}),
        required=True,
        label="Select your top 5 opportunities for improvement (you will rank them next)"
    )
    
    class Meta:
        model = SurveyResponse
        fields = [
            'q2_response', 'q3_response', 'q4_response', 'q5_response', 'q6_response',
            'q7_response', 'q8_response', 'q9_response', 'q10_response', 'q11_response',
            'q12_response', 'q13_response', 'q14_response', 'q15_response', 'q16_response',
            'q17_response', 'q18_response', 'q19_response', 'q20_response', 'q21_response',
            'q22_response', 'q23_response', 'q24_response', 'q25_response', 'q26_response',
            'q27_response', 'q28_response', 'q29_response', 'q30_response', 'q31_response',
            'q32_response', 'q33_response', 'q34_response', 'q35_response', 'q36_response',
            'q37_response', 'q38_response', 'q39_response', 'q40_response', 'q41_response',
            'q42_response', 'q43_response', 'q44_response', 'q45_response', 'q46_response',
            'q47_response', 'q48_response', 'q49_response', 'q50_response', 'q51_response',
            'q52_response', 'q53_response', 'q54_response', 'q55_response',
            'continue_doing', 'stop_doing', 'start_doing'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up Likert scale fields - use same text as participants
        question_texts = get_question_texts()
        for i in range(2, 56):
            field_name = f'q{i}_response'
            if field_name in self.fields:
                # Keep original "This leader" text for self-assessment too
                self.fields[field_name].label = question_texts[i]
                self.fields[field_name].widget = forms.RadioSelect(
                    attrs={'class': 'likert-scale'}
                )
                # Explicitly set choices without empty option
                self.fields[field_name].choices = SurveyResponse.LIKERT_CHOICES
                self.fields[field_name].empty_label = None
        
        # Set up strengths and opportunities choices
        strength_choices = [(str(i), choice) for i, choice in enumerate(get_strength_choices())]
        opportunity_choices = [(str(i), choice) for i, choice in enumerate(get_opportunity_choices())]
        
        self.fields['strengths'].choices = strength_choices
        self.fields['opportunities'].choices = opportunity_choices
        
        # Set up open-ended fields
        self.fields['continue_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What positive behaviors should you continue?'
        })
        self.fields['stop_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What behaviors should you stop?'
        })
        self.fields['start_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What new behaviors should you start?'
        })
    
    def clean_strengths(self):
        """Validate that exactly 5 strengths are selected."""
        strengths = self.cleaned_data.get('strengths', [])
        if len(strengths) != 5:
            raise forms.ValidationError("Please select exactly 5 strengths.")
        return strengths
    
    def clean_opportunities(self):
        """Validate that exactly 5 opportunities are selected."""
        opportunities = self.cleaned_data.get('opportunities', [])
        if len(opportunities) != 5:
            raise forms.ValidationError("Please select exactly 5 opportunities for improvement.")
        return opportunities


class SurveyResponseForm(forms.ModelForm):
    """Form for participant survey responses (excludes Self relationship)."""
    
    # Dynamic fields for strengths and opportunities
    strengths = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'strength-checkbox'}),
        required=True,
        label="Select your top 5 strengths (you will rank them next)"
    )
    
    opportunities = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'opportunity-checkbox'}),
        required=True,
        label="Select your top 5 opportunities for improvement (you will rank them next)"
    )
    
    class Meta:
        model = SurveyResponse
        fields = [
            'relationship',
            'q2_response', 'q3_response', 'q4_response', 'q5_response', 'q6_response',
            'q7_response', 'q8_response', 'q9_response', 'q10_response', 'q11_response',
            'q12_response', 'q13_response', 'q14_response', 'q15_response', 'q16_response',
            'q17_response', 'q18_response', 'q19_response', 'q20_response', 'q21_response',
            'q22_response', 'q23_response', 'q24_response', 'q25_response', 'q26_response',
            'q27_response', 'q28_response', 'q29_response', 'q30_response', 'q31_response',
            'q32_response', 'q33_response', 'q34_response', 'q35_response', 'q36_response',
            'q37_response', 'q38_response', 'q39_response', 'q40_response', 'q41_response',
            'q42_response', 'q43_response', 'q44_response', 'q45_response', 'q46_response',
            'q47_response', 'q48_response', 'q49_response', 'q50_response', 'q51_response',
            'q52_response', 'q53_response', 'q54_response', 'q55_response',
            'continue_doing', 'stop_doing', 'start_doing'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up relationship field - exclude 'Self' for participant surveys
        participant_choices = [
            ('supervisor', 'Supervisor/Manager'),
            ('peer', 'Peer/Colleague'),
            ('teacher', 'Teacher/Staff'),
            ('student', 'Student'),
            ('parent', 'Parent/Community Representative'),
        ]
        self.fields['relationship'].choices = participant_choices
        self.fields['relationship'].widget = forms.RadioSelect(
            attrs={'class': 'form-check-input'}
        )
        
        # Set up Likert scale fields
        question_texts = get_question_texts()
        for i in range(2, 56):
            field_name = f'q{i}_response'
            if field_name in self.fields:
                # Keep original text for participants (about "This leader")
                self.fields[field_name].label = question_texts[i]
                self.fields[field_name].widget = forms.RadioSelect(
                    attrs={'class': 'likert-scale'}
                )
                # Explicitly set choices without empty option
                self.fields[field_name].choices = SurveyResponse.LIKERT_CHOICES
                self.fields[field_name].empty_label = None
        
        # Set up strengths and opportunities choices
        strength_choices = [(str(i), choice) for i, choice in enumerate(get_strength_choices())]
        opportunity_choices = [(str(i), choice) for i, choice in enumerate(get_opportunity_choices())]
        
        self.fields['strengths'].choices = strength_choices
        self.fields['opportunities'].choices = opportunity_choices
        
        # Set up open-ended fields
        self.fields['continue_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What positive behaviors should this leader continue?'
        })
        self.fields['stop_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What behaviors should this leader stop?'
        })
        self.fields['start_doing'].widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What new behaviors should this leader start?'
        })
    
    def clean_strengths(self):
        """Validate that exactly 5 strengths are selected."""
        strengths = self.cleaned_data.get('strengths', [])
        if len(strengths) != 5:
            raise forms.ValidationError("Please select exactly 5 strengths.")
        return strengths
    
    def clean_opportunities(self):
        """Validate that exactly 5 opportunities are selected."""
        opportunities = self.cleaned_data.get('opportunities', [])
        if len(opportunities) != 5:
            raise forms.ValidationError("Please select exactly 5 opportunities for improvement.")
        return opportunities