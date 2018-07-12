from django.contrib import admin
from .models import Report, Worksheet, WorksheetMembership, ReportShare


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ['query', 'staff__user__username', 'staff__user__last_name']
    list_display = ('query', 'staff', 'created_on', 'shared_with', 'shared_by')

    def shared_with(self, instance):
        reportChildrenShares = ReportShare.objects.filter(parent=instance)
        return ", ".join([str(r.child.staff) for r in reportChildrenShares])

    def shared_by(self, instance):
        reportParentShare = ReportShare.objects.filter(child=instance)
        return str(reportParentShare.first().parent.staff) if reportParentShare.exists() else ''

@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    search_fields = ['parent__id', 'parent__query', 'child__id', 'child__query',
                     'parent__staff', 'child__staff']
    list_display = ('parent', 'child')

@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    search_fields = ['title', 'staff__user__username', 'staff__user__last_name']
    list_display = ('title', 'staff', 'created_on')

@admin.register(WorksheetMembership)
class WorksheetMembershipAdmin(admin.ModelAdmin):
    search_fields = ['report', 'worksheet', 'worksheet__staff__user__username']
    list_display = ('report', 'worksheet', 'created_on')
