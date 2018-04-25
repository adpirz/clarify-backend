from json import loads
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from sis_pull.models import (
    Student, Section, GradeLevel, Site, Staff,
    SectionLevelRosterPerYear
)

from mimesis import Person

# Create your views here.

@login_required
def UserView(request):
    if request.method == 'GET':
        user = request.user
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })

@login_required
def StudentView(request):
    def _shape(student):
        return {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
        }
    user = request.user
    request_teacher = Staff.objects.filter(user=user)
    teacher_student_ids = (SectionLevelRosterPerYear.objects
        .filter(user=request_teacher)
        .values_list('student_id')
    )
    teacher_students = Student.objects.filter(id__in=teacher_student_ids)

    return JsonResponse({
        'data': [_shape(s) for s in teacher_students]
    })


@login_required
def SectionView(request):
    def _shape(section):
        return {
            'id': section.id,
            'section_name': section.section_name,
        }
    # Decided somewhat arbitrarily to return all sections associated with a
    # staff member. We'll want to come up with more specific rules for that soon,
    # aka all sections at a staff member's site, that accounts for multi-site
    # staff, etc.
    user = request.user
    request_teacher = Staff.objects.filter(user=user)
    teacher_section_ids = (SectionLevelRosterPerYear.objects
        .filter(user=request_teacher)
        .filter(section__section_name__isnull=False)
        .exclude(section__section_name__exact="")
        .values_list('section_id')
    )
    teacher_sections = Section.objects.filter(id__in=teacher_section_ids)

    return JsonResponse({
        'data': [_shape(s) for s in teacher_sections]
    })

@login_required
def GradeLevelView(request):
    def _shape(grade_level):
        return {
            'id': grade_level.id,
            'short_name': grade_level.short_name,
            'long_name': grade_level.long_name,
        }
    user = request.user
    request_teacher = Staff.objects.filter(user=user)
    teacher_grade_level_ids = (SectionLevelRosterPerYear.objects
        .filter(user=request_teacher)
        .values_list('grade_level_id')
    )
    teacher_grade_levels = GradeLevel.objects.filter(id__in=teacher_grade_level_ids)

    return JsonResponse({
        'data': [_shape(g) for g in teacher_grade_levels]
    })

@login_required
def SiteView(request):
    def _shape(site):
        return {
            'id': site.id,
            'site_name': site.site_name,
        }

    user = request.user
    request_teacher = Staff.objects.filter(user=user)
    teacher_site_ids = (SectionLevelRosterPerYear.objects
        .filter(user=request_teacher)
        .values_list('site_id')
    )
    teacher_sites = Site.objects.filter(id__in=teacher_site_ids)

    return JsonResponse({
        'data': [_shape(s) for s in teacher_sites]
    })

@csrf_exempt
def SessionView(request):
    if request.method not in ['GET', 'POST', 'DELETE']:
        return JsonResponse({
            'error': 'Method not allowed.'
        })
    user = request.user
    if request.method == 'GET':
        if user.is_authenticated():
            return JsonResponse(
                {'data': 'Success'},
                status=200
            )
        return JsonResponse(
            {'error': 'No session for user'},
            status=404
        )
    elif request.method == 'POST':
        if user.is_authenticated():
            return JsonResponse(
                {'data': 'Success'},
                status=200
            )
        else:
            parseablePost = request.body.decode('utf8').replace("'", '"')
            parsedPost = loads(parseablePost)
            requestUsername = parsedPost.get('username')
            requestPassword = parsedPost.get('password', '')
            user = authenticate(username=requestUsername, password=requestPassword)
            if user:
                login(request, user)
                return JsonResponse(
                    {'data': 'Success'},
                    status=201
                )
            else:
                return JsonResponse(
                    {'error': 'Username and password were incorrect'},
                    status=400
                )
    elif request.method == 'DELETE':
        if not user.is_authenticated():
            return JsonResponse(
                {'error': 'No session for that user'},
                status=400
            )
        logout(request)
        return JsonResponse(
            {'data': 'Success'},
            status=200
        )
    return JsonResponse(
        {'error': 'Response not handled'},
        status=400
    )
