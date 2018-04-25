"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import (StudentView, SectionView, GradeLevelView,
SiteView, SessionView, UserView)
from reports.views import ReportView

urlpatterns = [
    url(r'^user/me', UserView),
    url(r'^student/', StudentView),
    url(r'^section/', SectionView),
    url(r'^grade-level/', GradeLevelView),
    url(r'^site/', SiteView),
    url(r'^session/', SessionView),
    url(r'^report/', ReportView)
]
