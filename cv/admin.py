from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from .models import (
    Profile, Skill, Experience, Education, 
    Project, CVTemplate, UserCV
)

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')


class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'profile', 'level', 'category')
    list_filter = ('level', 'category')
    search_fields = ('name', 'profile__user__username')


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'profile', 'start_date', 'end_date', 'current')
    list_filter = ('current', 'start_date')
    search_fields = ('job_title', 'company', 'profile__user__username')
    date_hierarchy = 'start_date'


class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'profile', 'degree_type', 'start_date', 'end_date')
    list_filter = ('degree_type', 'start_date')
    search_fields = ('degree', 'institution', 'profile__user__username')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'start_date', 'end_date', 'current')
    search_fields = ('title', 'technologies', 'profile__user__username')
    list_filter = ('current', 'start_date')


class CVTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


class UserCVAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_public', 'created_at', 'updated_at')
    list_filter = ('is_public', 'template')
    search_fields = ('title', 'user__username', 'profile__first_name', 'profile__last_name')
    readonly_fields = ('created_at', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}


# Unregister the default User admin and register our custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register other models
admin.site.register(Profile)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(CVTemplate, CVTemplateAdmin)
admin.site.register(UserCV, UserCVAdmin)
