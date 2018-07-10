from django.contrib import admin
from .models import Report, Worksheet, WorksheetMembership


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ['query', 'staff__user__username', 'staff__user__last_name']
    list_display = ('query', 'staff', 'created_on')

@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    search_fields = ['title', 'staff__user__username', 'staff__user__last_name']
    list_display = ('title', 'staff', 'created_on')

@admin.register(WorksheetMembership)
class WorksheetMembershipAdmin(admin.ModelAdmin):
    search_fields = ['report', 'worksheet', 'worksheet__staff__user__username']
    list_display = ('report', 'worksheet', 'created_on')
