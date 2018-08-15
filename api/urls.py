"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import (
    StudentView, SectionView, GradeLevelView,
    SiteView, SessionView, UserView, ReportView, CourseView,
    StaffView, ReportShareView)

urlpatterns = [
    url(r'^user/me/', UserView),
    url(r'^student/', StudentView),
    url(r'^course/', CourseView),
    url(r'^section/', SectionView),
    url(r'^grade-level/', GradeLevelView),
    url(r'^site/', SiteView),
    url(r'^session/', SessionView),
    url(r'^report/(?P<report_id>\w+)', ReportView),
    url(r'^report/', ReportView),
    url(r'^report-share/', ReportShareView),
    url(r'^staff/', StaffView),
    url(r'^experiemnt/', include('experiment.urls', namespace='experiment'))
]
