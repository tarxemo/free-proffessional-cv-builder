from django import forms
from django.forms import ModelForm, DateInput
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class DateInput(forms.DateInput):
    input_type = 'date'


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 
            'city', 'country', 'postal_code', 'linkedin_url', 
            'github_url', 'portfolio_url', 'professional_summary'
        ]
        widgets = {
            'professional_summary': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level', 'category']
        widgets = {
            'level': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'level':
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            'job_title', 'company', 'location', 'start_date', 
            'end_date', 'current', 'description', 'achievements'
        ]
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['description', 'achievements', 'current']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        current = cleaned_data.get('current')
        
        if not current and not end_date:
            raise forms.ValidationError(
                "Please provide an end date or check 'Current' if this is your current position."
            )
            
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(
                "End date should be greater than or equal to start date."
            )
            
        return cleaned_data


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            'degree', 'degree_type', 'field_of_study', 'institution', 
            'location', 'start_date', 'end_date', 'current', 
            'description', 'gpa'
        ]
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'degree_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['degree_type', 'description', 'current']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        current = cleaned_data.get('current')
        
        if not current and not end_date:
            raise forms.ValidationError(
                "Please provide an end date or check 'Current' if this is your current education."
            )
            
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(
                "End date should be greater than or equal to start date."
            )
            
        return cleaned_data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'technologies', 
            'project_url', 'github_url', 'start_date', 
            'end_date', 'current'
        ]
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'technologies': forms.TextInput(attrs={'placeholder': 'e.g., Python, Django, JavaScript'}),
            'current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['description', 'current']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean_technologies(self):
        technologies = self.cleaned_data.get('technologies')
        # Clean up the technologies string
        if technologies:
            # Split by comma, strip whitespace, and join with comma+space
            tech_list = [tech.strip() for tech in technologies.split(',')]
            return ', '.join(tech_list)
        return technologies
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        current = cleaned_data.get('current')
        
        if not current and not end_date:
            raise forms.ValidationError(
                "Please provide an end date or check 'Current' if this is an ongoing project."
            )
            
        if end_date and start_date and end_date < start_date:
            raise forms.ValidationError(
                "End date should be greater than or equal to start date."
            )
            
        return cleaned_data


class UserCVForm(forms.ModelForm):
    class Meta:
        model = UserCV
        fields = ['title', 'template', 'is_public']
        widgets = {
            'template': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['template'].queryset = CVTemplate.objects.filter(is_active=True)


class CVTemplateForm(forms.ModelForm):
    class Meta:
        model = CVTemplate
        fields = ['name', 'description', 'template_file', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_active':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
