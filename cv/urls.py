from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views
from .views_cv_builder import (
    CVAPISaveView, CVAPILoadView, CVAPIDeleteView,
    CVPreviewView, CVDownloadView, CVTemplatePreviewView
)

app_name = 'cv'

urlpatterns = [
    # Public pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    
    # Authentication
    path('signup/', views.SignUpView.as_view(), name='signup'),
    
    # Dashboard
    path('dashboard/', login_required(views.DashboardView.as_view()), name='dashboard'),
    
    # Profile management
    path('profile/create/', login_required(views.ProfileCreateView.as_view()), name='profile_create'),
    path('profile/update/', login_required(views.ProfileUpdateView.as_view()), name='profile_update'),
    
    # Skills management
    path('skills/', login_required(views.SkillListView.as_view()), name='skill_list'),
    path('skills/add/', login_required(views.SkillCreateView.as_view()), name='skill_create'),
    path('skills/<int:pk>/update/', login_required(views.SkillUpdateView.as_view()), name='skill_update'),
    path('skills/<int:pk>/delete/', login_required(views.SkillDeleteView.as_view()), name='skill_delete'),
    
    # Experience management
    path('experience/', login_required(views.ExperienceListView.as_view()), name='experience_list'),
    path('experience/add/', login_required(views.ExperienceCreateView.as_view()), name='experience_create'),
    path('experience/<int:pk>/update/', login_required(views.ExperienceUpdateView.as_view()), name='experience_update'),
    path('experience/<int:pk>/delete/', login_required(views.ExperienceDeleteView.as_view()), name='experience_delete'),
    
    # Education management
    path('education/', login_required(views.EducationListView.as_view()), name='education_list'),
    path('education/add/', login_required(views.EducationCreateView.as_view()), name='education_create'),
    path('education/<int:pk>/update/', login_required(views.EducationUpdateView.as_view()), name='education_update'),
    path('education/<int:pk>/delete/', login_required(views.EducationDeleteView.as_view()), name='education_delete'),
    
    # Projects management
    path('projects/', login_required(views.ProjectListView.as_view()), name='project_list'),
    path('projects/add/', login_required(views.ProjectCreateView.as_view()), name='project_create'),
    path('projects/<int:pk>/update/', login_required(views.ProjectUpdateView.as_view()), name='project_update'),
    path('projects/<int:pk>/delete/', login_required(views.ProjectDeleteView.as_view()), name='project_delete'),
    
    # CV Builder
    path('builder/', login_required(views.CVBuilderView.as_view()), name='cv_builder'),
    path('templates/', login_required(views.CVTemplateListView.as_view()), name='cv_templates'),
    
    # CV Builder API Endpoints
    path('api/cv/save/', login_required(CVAPISaveView.as_view()), name='cv_api_save'),
    path('api/cv/load/', login_required(CVAPILoadView.as_view()), name='cv_api_load'),
    path('api/cv/delete/', login_required(CVAPIDeleteView.as_view()), name='cv_api_delete'),
    
    # CV Preview and Download
    path('cv/<int:pk>/preview/', login_required(CVPreviewView.as_view()), name='cv_preview'),
    path('cv/<int:pk>/download/', login_required(CVDownloadView.as_view()), name='cv_download'),
    path('templates/<int:pk>/preview/', login_required(CVTemplatePreviewView.as_view()), name='template_preview'),
    
    # User CVs
    path('my-cvs/', login_required(views.UserCVListView.as_view()), name='cv_list'),
    path('cv/<slug:slug>/', login_required(views.UserCVDetailView.as_view()), name='cv_detail'),
    path('cv/<int:pk>/delete/', login_required(views.UserCVDeleteView.as_view()), name='cv_delete'),
    path('cv/<int:pk>/preview/', login_required(views.CVPreviewView.as_view()), name='cv_preview'),
    
    # Public CV view (for sharing)
    path('public/cv/<slug:slug>/', views.PublicCVView.as_view(), name='public_cv'),
]
