"""API URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import include, url
from django.contrib import admin
from .views import (TestView, StudentView, SectionView, GradeLevelView,
SchoolView, SessionView)

urlpatterns = [
    url(r'^test', TestView, name='test'),
    url(r'^student/', StudentView),
    url(r'^section/', SectionView),
    url(r'^grade-level/', GradeLevelView),
    url(r'^school/', SchoolView),
    url(r'^session/', SessionView),
]
