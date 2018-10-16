from django.contrib import admin

from .models import Action


@admin.register(Action)
class ReportAdmin(admin.ModelAdmin):
    search_fields = ['student']
