from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

from .models import UserProfile, Student, Term, Site, Section
# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
    list_display = ('user', 'prefix')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ('first_name', 'last_name')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    pass

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    pass

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass

class UserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'username', 'email']

    def sign_in_as_user(modeladmin, request, queryset):
        if len(queryset) > 1:
            messages.error(request, "You cannot sign in as more than one user.")
            return
        elif not request.user.is_superuser:
            messages.error(request, "You have no power here.")
            return
        else:
            login(request, queryset[0])

    actions = [sign_in_as_user]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
