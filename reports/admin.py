from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import admin
from .models import Report, ReportShare
from django.contrib import messages


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ['query', 'staff__user__username', 'staff__user__last_name']
    list_display = ('query', 'staff', 'created_on', 'shared_with', 'shared_by')

    def shared_with(self, instance):
        reportChildrenShares = ReportShare.objects.filter(parent=instance)
        return ", ".join([str(r.child.staff) for r in reportChildrenShares])

    def shared_by(self, instance):
        reportParentShare = ReportShare.objects.filter(child=instance)
        return str(reportParentShare.first().shared_by) if reportParentShare.first() else ''

@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    search_fields = ['parent__id', 'parent__query', 'child__id', 'child__query',
                     'parent__staff', 'child__staff']
    list_display = ('parent', 'child')

class UserAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'username']

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
