from django.contrib import admin

from .models import Staff
# Register your models here.


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    list_display = ('user', 'prefix')
