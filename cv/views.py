from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View, FormView
)
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
import json
import os
from django.conf import settings
from django.template.loader import get_template
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import tempfile

# Try to import WeasyPrint, but make it optional
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: WeasyPrint is not installed. PDF generation will not be available.")

from .models import Profile, Skill, Experience, Education, Project, CVTemplate, UserCV
from .forms import *
class CVTemplateListView(LoginRequiredMixin, ListView):
    model = CVTemplate
    template_name = 'cv/template_list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return CVTemplate.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CV Templates'
        return context


class HomeView(TemplateView):
    template_name = 'cv/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ProTechCV - Create Professional CVs for Tech Professionals'
        return context


class AboutView(TemplateView):
    template_name = 'cv/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'About ProTechCV'
        return context


class PricingView(TemplateView):
    template_name = 'cv/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Pricing - ProTechCV'
        return context


class SignUpView(View):
    template_name = 'cv/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('cv:dashboard')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('cv:dashboard')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('cv:profile_create')
        return render(request, self.template_name, {'form': form})


# Dashboard View
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'cv/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard - ProTechCV'
        context['profile'] = getattr(self.request.user, 'profile', None)
        context['cvs'] = UserCV.objects.filter(user=self.request.user).order_by('-updated_at')[:5]
        return context


# Profile Views
class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'cv/profile_form.html'
    success_url = reverse_lazy('cv:dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Profile created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Profile'
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'cv/profile_form.html'
    success_url = reverse_lazy('cv:dashboard')
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Profile'
        return context


# Skill Views
class SkillListView(LoginRequiredMixin, ListView):
    model = Skill
    template_name = 'cv/skill_list.html'
    context_object_name = 'skills'
    
    def get_queryset(self):
        return Skill.objects.filter(profile__user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Skills'
        return context


class SkillCreateView(LoginRequiredMixin, CreateView):
    model = Skill
    form_class = SkillForm
    template_name = 'cv/skill_form.html'
    success_url = reverse_lazy('cv:skill_list')
    
    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        messages.success(self.request, 'Skill added successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Skill'
        return context


class SkillUpdateView(LoginRequiredMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'cv/skill_form.html'
    success_url = reverse_lazy('cv:skill_list')
    
    def get_queryset(self):
        return Skill.objects.filter(profile__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Skill updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Skill'
        return context


class SkillDeleteView(LoginRequiredMixin, DeleteView):
    model = Skill
    template_name = 'cv/skill_confirm_delete.html'
    success_url = reverse_lazy('cv:skill_list')
    
    def get_queryset(self):
        return Skill.objects.filter(profile__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Skill deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Experience Views (similar pattern as Skill Views)
class ExperienceListView(LoginRequiredMixin, ListView):
    model = Experience
    template_name = 'cv/experience_list.html'
    context_object_name = 'experiences'
    
    def get_queryset(self):
        return Experience.objects.filter(profile__user=self.request.user).order_by('-start_date')


class ExperienceCreateView(LoginRequiredMixin, CreateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'cv/experience_form.html'
    success_url = reverse_lazy('cv:experience_list')
    
    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        messages.success(self.request, 'Experience added successfully!')
        return super().form_valid(form)


class ExperienceUpdateView(LoginRequiredMixin, UpdateView):
    model = Experience
    form_class = ExperienceForm
    template_name = 'cv/experience_form.html'
    success_url = reverse_lazy('cv:experience_list')
    
    def get_queryset(self):
        return Experience.objects.filter(profile__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Experience updated successfully!')
        return super().form_valid(form)


class ExperienceDeleteView(LoginRequiredMixin, DeleteView):
    model = Experience
    template_name = 'cv/experience_confirm_delete.html'
    success_url = reverse_lazy('cv:experience_list')
    
    def get_queryset(self):
        return Experience.objects.filter(profile__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Experience deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Education Views (similar pattern as Skill Views)
class EducationListView(LoginRequiredMixin, ListView):
    model = Education
    template_name = 'cv/education_list.html'
    context_object_name = 'educations'
    
    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user).order_by('-start_date')


class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    form_class = EducationForm
    template_name = 'cv/education_form.html'
    success_url = reverse_lazy('cv:education_list')
    
    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        messages.success(self.request, 'Education added successfully!')
        return super().form_valid(form)


class EducationUpdateView(LoginRequiredMixin, UpdateView):
    model = Education
    form_class = EducationForm
    template_name = 'cv/education_form.html'
    success_url = reverse_lazy('cv:education_list')
    
    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Education updated successfully!')
        return super().form_valid(form)


class EducationDeleteView(LoginRequiredMixin, DeleteView):
    model = Education
    template_name = 'cv/education_confirm_delete.html'
    success_url = reverse_lazy('cv:education_list')
    
    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Education deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Project Views (similar pattern as Skill Views)
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'cv/project_list.html'
    context_object_name = 'projects'
    
    def get_queryset(self):
        return Project.objects.filter(profile__user=self.request.user).order_by('-start_date')


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'cv/project_form.html'
    success_url = reverse_lazy('cv:project_list')
    
    def form_valid(self, form):
        form.instance.profile = self.request.user.profile
        messages.success(self.request, 'Project added successfully!')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'cv/project_form.html'
    success_url = reverse_lazy('cv:project_list')
    
    def get_queryset(self):
        return Project.objects.filter(profile__user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'cv/project_confirm_delete.html'
    success_url = reverse_lazy('cv:project_list')
    
    def get_queryset(self):
        return Project.objects.filter(profile__user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)


# CV Builder Views
class CVBuilderView(LoginRequiredMixin, TemplateView):
    template_name = 'cv/cv_builder.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'CV Builder'
        context['templates'] = CVTemplate.objects.filter(is_active=True)
        return context


class CVTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'cv/cv_template.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = get_object_or_404(CVTemplate, id=self.kwargs.get('template_id'), is_active=True)
        profile = get_object_or_404(Profile, user=self.request.user)
        
        context.update({
            'title': f'CV - {template.name}',
            'template': template,
            'profile': profile,
            'skills': Skill.objects.filter(profile=profile),
            'experiences': Experience.objects.filter(profile=profile).order_by('-start_date'),
            'educations': Education.objects.filter(profile=profile).order_by('-start_date'),
            'projects': Project.objects.filter(profile=profile).order_by('-start_date'),
            'current_year': datetime.now().year
        })
        return context


class CVSaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        title = request.POST.get('title', 'My CV')
        template_id = request.POST.get('template_id')
        is_public = request.POST.get('is_public') == 'on'
        
        try:
            template = CVTemplate.objects.get(id=template_id, is_active=True)
            profile = Profile.objects.get(user=request.user)
            
            cv = UserCV.objects.create(
                user=request.user,
                profile=profile,
                template=template,
                title=title,
                is_public=is_public
            )
            
            messages.success(request, 'CV saved successfully!')
            return redirect('cv:cv_detail', slug=cv.slug)
            
        except (CVTemplate.DoesNotExist, Profile.DoesNotExist) as e:
            messages.error(request, 'Error saving CV. Please try again.')
            return redirect('cv:cv_builder')


class CVDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cv = get_object_or_404(UserCV, id=kwargs.get('cv_id'), user=request.user)
        
        # Render the template to HTML
        html_string = render_to_string(
            f'cv/templates/{cv.template.template_file}.html',
            self.get_context_data(cv)
        )
        
        # Generate PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
        
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{cv.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def get_context_data(self, cv):
        return {
            'cv': cv,
            'profile': cv.profile,
            'skills': Skill.objects.filter(profile=cv.profile),
            'experiences': Experience.objects.filter(profile=cv.profile).order_by('-start_date'),
            'educations': Education.objects.filter(profile=cv.profile).order_by('-start_date'),
            'projects': Project.objects.filter(profile=cv.profile).order_by('-start_date'),
            'current_year': datetime.now().year
        }


# User CV Views
class UserCVListView(LoginRequiredMixin, ListView):
    model = UserCV
    template_name = 'cv/cv_list.html'
    context_object_name = 'cvs'
    
    def get_queryset(self):
        return UserCV.objects.filter(user=self.request.user).order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My CVs'
        return context


class UserCVDetailView(LoginRequiredMixin, DetailView):
    model = UserCV
    template_name = 'cv/cv_detail.html'
    context_object_name = 'cv'
    
    def get_queryset(self):
        return UserCV.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class UserCVDeleteView(LoginRequiredMixin, DeleteView):
    model = UserCV
    template_name = 'cv/cv_confirm_delete.html'
    success_url = reverse_lazy('cv:cv_list')
    
    def get_queryset(self):
        return UserCV.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'CV deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CVPreviewView(LoginRequiredMixin, DetailView):
    model = UserCV
    template_name = 'cv/cv_preview.html'
    context_object_name = 'cv'
    
    def get_queryset(self):
        return UserCV.objects.filter(user=self.request.user)
    
    def get_template_names(self):
        return [f"cv/templates/{self.object.template.template_file}.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_mode'] = True
        return context


# Public CV View
class PublicCVView(DetailView):
    model = UserCV
    template_name = 'cv/public_cv.html'
    context_object_name = 'cv'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return UserCV.objects.filter(is_public=True)
    
    def get_template_names(self):
        return [f"cv/templates/{self.object.template.template_file}.html"]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['public_view'] = True
        return context


# AJAX Views
@method_decorator(csrf_exempt, name='dispatch')
class AIAssistantView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from openai import OpenAI
        
        prompt = request.POST.get('prompt', '')
        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)
        
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that helps with CV writing and career advice."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return JsonResponse({
                'response': response.choices[0].message.content
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Helper function to generate PDF
def generate_pdf(request, cv_id):
    cv = get_object_or_404(UserCV, id=cv_id, user=request.user)
    
    # Render the template to HTML
    html_string = render_to_string(
        f'cv/templates/{cv.template.template_file}.html',
        {
            'cv': cv,
            'profile': cv.profile,
            'skills': Skill.objects.filter(profile=cv.profile),
            'experiences': Experience.objects.filter(profile=cv.profile).order_by('-start_date'),
            'educations': Education.objects.filter(profile=cv.profile).order_by('-start_date'),
            'projects': Project.objects.filter(profile=cv.profile).order_by('-start_date'),
            'current_year': datetime.now().year,
            'pdf_mode': True
        }
    )
    
    # Generate PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"{cv.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
