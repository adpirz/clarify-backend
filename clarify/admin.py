from django.contrib import admin

from .models import UserProfile, Student, Term
# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_display = ('user', 'prefix')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ('first_name', 'last_name')

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    pass