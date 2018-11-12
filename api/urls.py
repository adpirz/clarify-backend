"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import url
from .views import (
    StudentView, SectionView, SessionView,
    UserView, CourseView, ActionView, DeltaView)

urlpatterns = [
    url(r'^user/me/$', UserView),
    url(r'^student/$', StudentView),
    url(r'^course/$', CourseView),
    url(r'^section/$', SectionView),
    url(r'^session/$', SessionView),
    url(r'^delta/$', DeltaView),
    url(r'^delta/student/([0-9]+)/$', DeltaView),
    url(r'^action/$', ActionView),
    url(r'^action/([0-9]+)/$', ActionView),
]
