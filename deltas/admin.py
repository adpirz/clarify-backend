from django.contrib import admin

from .models import Action, Delta
from sis_pull.models import Student

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    search_fields = ['student']
    list_display = ('student', 'due_on', 'type', 'completed_on')


@admin.register(Delta)
class DeltaAdmin(admin.ModelAdmin):
    search_fields = ['student']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            kwargs["queryset"] = Student.objects.order_by('first_name')
        return super(DeltaAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)