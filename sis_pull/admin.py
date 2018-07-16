from django.contrib import admin

from .models import Staff, Student
# Register your models here.


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_display = ('user', 'prefix')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name']
    list_display = ('first_name', 'last_name')
