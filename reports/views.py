import random
from json import loads
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from sis_pull.models import Student, AttendanceDailyRecord

from mimesis import Person

from .report_builder import query_to_data


@login_required
def ReportView(request):
    return JsonResponse(query_to_data(request))