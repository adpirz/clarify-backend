"""Clarify URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import url

from clarify.views import handleManualRosterUpload

urlpatterns = [
    url(r'^manual-upload/$', handleManualRosterUpload),
]
