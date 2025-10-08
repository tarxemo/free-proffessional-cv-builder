from django.views.generic import View, TemplateView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
import os
import json
import uuid
from datetime import datetime

from .models import Profile, Skill, Experience, Education, Project, CVTemplate, UserCV
from .forms import ProfileForm, SkillForm, ExperienceForm, EducationForm, ProjectForm, UserCVForm

# Import WeasyPrint if available
try:
    from weasyprint import HTML
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

class CVBuilderView(LoginRequiredMixin, TemplateView):
    template_name = 'cv/base_builder.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Get all related data
        skills = Skill.objects.filter(profile=profile).order_by('-proficiency', 'name')
        experiences = Experience.objects.filter(profile=profile).order_by('-start_date')
        educations = Education.objects.filter(profile=profile).order_by('-start_date')
        projects = Project.objects.filter(profile=profile).order_by('-date_completed')
        templates = CVTemplate.objects.filter(is_active=True)
        
        # Get or create a default CV for the user
        user_cv, created = UserCV.objects.get_or_create(
            user=user,
            is_default=True,
            defaults={
                'title': f"{user.get_full_name() or user.username}'s CV",
                'template': templates.first(),
                'content': json.dumps(self.get_default_cv_content(profile))
            }
        )
        
        context.update({
            'profile': profile,
            'skills': skills,
            'experiences': experiences,
            'educations': educations,
            'projects': projects,
            'templates': templates,
            'user_cv': user_cv,
            'weasyprint_available': WEASYPRINT_AVAILABLE
        })
        
        return context
    
    def get_default_cv_content(self, profile):
        """Generate default CV content structure"""
        return {
            'profile': {
                'first_name': profile.first_name or '',
                'last_name': profile.last_name or '',
                'email': profile.email or '',
                'phone': profile.phone or '',
                'address': profile.address or '',
                'city': profile.city or '',
                'country': profile.country or '',
                'postal_code': profile.postal_code or '',
                'linkedin_url': profile.linkedin_url or '',
                'github_url': profile.github_url or '',
                'portfolio_url': profile.portfolio_url or '',
                'professional_summary': profile.professional_summary or ''
            },
            'sections': ['summary', 'experience', 'education', 'skills', 'projects', 'languages']
        }

class CVAPISaveView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = request.user
            
            with transaction.atomic():
                # Get or create CV
                cv_id = data.get('id')
                if cv_id:
                    user_cv = get_object_or_404(UserCV, id=cv_id, user=user)
                else:
                    user_cv = UserCV(user=user)
                
                # Update CV data
                user_cv.title = data.get('title', 'My CV')
                user_cv.content = json.dumps(data.get('content', {}))
                
                if 'template_id' in data:
                    user_cv.template_id = data['template_id']
                
                # Handle default CV setting
                is_default = data.get('is_default', False)
                if is_default:
                    UserCV.objects.filter(user=user, is_default=True).update(is_default=False)
                user_cv.is_default = is_default
                
                user_cv.save()
                
                return JsonResponse({
                    'status': 'success',
                    'cv': {
                        'id': user_cv.id,
                        'title': user_cv.title,
                        'is_default': user_cv.is_default,
                        'updated_at': user_cv.updated_at.isoformat(),
                        'preview_url': reverse_lazy('cv:cv_preview', kwargs={'pk': user_cv.id})
                    },
                    'message': 'CV saved successfully'
                })
                
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, 
                status=400
            )


class CVAPILoadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            cv_id = request.GET.get('id')
            
            if cv_id:
                user_cv = get_object_or_404(UserCV, id=cv_id, user=user)
            else:
                # Get default CV or create a new one
                user_cv = UserCV.objects.filter(user=user, is_default=True).first()
                if not user_cv:
                    profile = Profile.objects.get_or_create(user=user)[0]
                    user_cv = UserCV.objects.create(
                        user=user,
                        title=f"{user.get_full_name() or user.username}'s CV",
                        is_default=True,
                        template=CVTemplate.objects.filter(is_active=True).first()
                    )
            
            return JsonResponse({
                'status': 'success',
                'cv': {
                    'id': user_cv.id,
                    'title': user_cv.title,
                    'content': json.loads(user_cv.content) if user_cv.content else {},
                    'template_id': user_cv.template_id,
                    'is_default': user_cv.is_default,
                    'created_at': user_cv.created_at.isoformat(),
                    'updated_at': user_cv.updated_at.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, 
                status=400
            )


class CVAPIDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cv_id = data.get('id')
            
            if not cv_id:
                raise ValueError('CV ID is required')
                
            user_cv = get_object_or_404(UserCV, id=cv_id, user=request.user)
            user_cv.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'CV deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse(
                {'status': 'error', 'message': str(e)}, 
                status=400
            )

class CVPreviewView(LoginRequiredMixin, DetailView):
    model = UserCV
    template_name = 'cv/cv_preview.html'
    context_object_name = 'cv'
    
    def get_queryset(self):
        return UserCV.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cv = context['cv']
        
        # Parse CV content
        try:
            cv_content = json.loads(cv.content) if cv.content else {}
        except json.JSONDecodeError:
            cv_content = {}
        
        # Get related data
        profile_data = cv_content.get('profile', {})
        
        context.update({
            'cv_content': cv_content,
            'profile_data': profile_data,
            'sections': cv_content.get('sections', []),
            'weasyprint_available': WEASYPRINT_AVAILABLE
        })
        
        return context
        try:
            cv_data = json.loads(cv.content) if cv.content else {}
        except (TypeError, json.JSONDecodeError):
            cv_data = {}
        
        # Get template context
        template = get_object_or_404(CVTemplate, id=cv.template_id)
        
        # Get related data
        profile_data = cv_data.get('profile', {})
        
        context.update({
            'cv_data': cv_data,
            'profile_data': profile_data,
            'sections': cv_data.get('sections', []),
            'template': template,
            'weasyprint_available': WEASYPRINT_AVAILABLE
        })
        
        return context

class CVDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not WEASYPRINT_AVAILABLE:
            messages.error(request, 'PDF generation is not available. Please install WeasyPrint.')
            return redirect('cv:cv_builder')
        
        cv = get_object_or_404(UserCV, id=kwargs.get('pk'), user=request.user)
        
        try:
            # Parse CV content
            cv_content = json.loads(cv.content) if cv.content else {}
            
            # Generate HTML for PDF
            html_string = render_to_string('cv/pdf_template.html', {
                'cv': cv,
                'cv_content': cv_content,
                'profile_data': cv_content.get('profile', {}),
                'sections': cv_content.get('sections', []),
                'static_path': settings.STATIC_ROOT or settings.STATICFILES_DIRS[0],
                'media_path': settings.MEDIA_ROOT
            })
            
            # Generate PDF
            font_config = FontConfiguration()
            html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
            pdf_file = html.write_pdf(stylesheets=[
                os.path.join(settings.BASE_DIR, 'static/css/pdf-styles.css')
            ], font_config=font_config)
            
            # Create response
            response = HttpResponse(pdf_file, content_type='application/pdf')
            filename = f"{cv.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('cv:cv_preview', pk=cv.id)

        context = {
            'cv': cv,
            'sections': json.loads(cv.content).get('sections', {}) if cv.content else {},
            'profile': request.user.profile,
            'skills': Skill.objects.filter(profile=request.user.profile).order_by('-proficiency', 'name'),
            'experiences': Experience.objects.filter(profile=request.user.profile).order_by('-start_date'),
            'educations': Education.objects.filter(profile=request.user.profile).order_by('-start_date'),
            'projects': Project.objects.filter(profile=request.user.profile).order_by('-date_completed'),
            'is_pdf': True
        }
        
        # Render HTML
        html_string = render_to_string(template_name, context)
        
        # Generate PDF
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf_file = html.write_pdf()
        
        # Create response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        filename = f"{cv.title.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

class CVTemplatePreviewView(LoginRequiredMixin, DetailView):
    model = CVTemplate
    template_name = 'cv/template_preview.html'
    context_object_name = 'template'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        return context
