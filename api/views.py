from json import loads
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from sis_pull.models import (
    Student, Section, GradeLevel, Site, Staff,
    SectionLevelRosterPerYear
)
from reports.models import Report, Worksheet, WorksheetMembership
from mimesis import Person
from utils import get_academic_year
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
            'is_enrolled': student.is_enrolled()
        }
    user = request.user
    staff_level = user.staff.get_max_role_level()
    if staff_level < 700:
        request_teacher = Staff.objects.filter(user=user)
        teacher_student_ids = (SectionLevelRosterPerYear.objects
            .filter(user=request_teacher.first())
            .filter(academic_year=get_academic_year())
            .values_list('student_id')
        )
        staff_students = Student.objects.filter(id__in=teacher_student_ids)
    else:
        current_site_id = user.staff.get_current_site_id()
        site_student_ids = (SectionLevelRosterPerYear.objects
            .filter(site_id=current_site_id)
            .filter(academic_year=get_academic_year())
            .values_list('student_id')
        )
        staff_students = Student.objects.filter(id__in=site_student_ids)
    return JsonResponse({
        'data': [_shape(s) for s in staff_students]
    })


@login_required
def SectionView(request):
    # TODO
    def _shape(section):
        tags = [str(section.get_timeblock())]
        course = section.get_course()
        if course:
            tags.append(str(course))
        return {
            'id': section.id,
            'section_name': str(section),
            'tags': tags
        }
    # Decided somewhat arbitrarily to return all sections associated with a
    # staff member. We'll want to come up with more specific rules for that soon,
    # aka all sections at a staff member's site, that accounts for multi-site
    # staff, etc.
    user = request.user
    staff_level = user.staff.get_max_role_level()
    if staff_level < 700:
        request_teacher = Staff.objects.filter(user=user)
        teacher_section_ids = (SectionLevelRosterPerYear.objects
            .filter(user=request_teacher.first())
            .filter(academic_year=get_academic_year())
            .filter(section__section_name__isnull=False)
            .exclude(section__section_name__exact="")
            .values_list('section_id')
        )
        staff_sections = Section.objects.filter(id__in=teacher_section_ids)
    else:
        current_site_id = user.staff.get_current_site_id()
        site_section_ids = (SectionLevelRosterPerYear.objects
            .filter(site_id=current_site_id)
            .filter(academic_year=get_academic_year())
            .values_list('section_id')
        )
        staff_sections = Section.objects.filter(id__in=site_section_ids)
    return JsonResponse({
        'data': [_shape(s) for s in staff_sections]
    })


@login_required
def GradeLevelView(request):
    # TODO
    def _shape(grade_level):
        return {
            'id': grade_level.id,
            'short_name': grade_level.short_name,
            'long_name': grade_level.long_name,
        }
    user = request.user
    staff_level = user.staff.get_max_role_level()
    if staff_level < 700:
        request_teacher = Staff.objects.filter(user=user)
        teacher_grade_level_ids = (SectionLevelRosterPerYear.objects
            .filter(user=request_teacher.first())
            .filter(academic_year=get_academic_year())
            .values_list('grade_level_id')
        )
        staff_grade_levels = GradeLevel.objects.filter(
            id__in=teacher_grade_level_ids
        )
    else:
        current_site_id = user.staff.get_current_site_id()
        site_grade_level_ids = (SectionLevelRosterPerYear.objects
            .filter(site_id=current_site_id)
            .filter(academic_year=get_academic_year())
            .values_list('grade_level_id')
        )
        staff_grade_levels = GradeLevel.objects.filter(
            id__in=site_grade_level_ids
        )
    return JsonResponse({
        'data': [_shape(g) for g in staff_grade_levels]
    })


@login_required
def CourseView(request):
    # TODO
    def _shape(row):
        return {
            'id': row.course.id,
            'short_name': row.course.short_name,
            'long_name': row.course.long_name,
        }

    user = request.user
    request_staff = Staff.objects.get(user=user)
    filter_kwargs = {}

    if request_staff.get_max_role_level() < 700:
        grade_levels = GradeLevel.get_users_current_grade_levels(request_staff)
        filter_kwargs["grade_level_id__in"] = grade_levels
        filter_kwargs["user"] = request_staff
    else:
        filter_kwargs["site_id"] = request_staff.get_current_site_id()

    return JsonResponse({
        'data': [_shape(row) for row in SectionLevelRosterPerYear.objects
                 .filter(**filter_kwargs)\
                 .distinct('course_id')
                 ]
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
        .filter(user=request_teacher.first())
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
        }, status_code=405)
    user = request.user
    if request.method == 'GET':
        if user.is_authenticated():
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }, status=200)
        else:
            return JsonResponse(
                {'error': 'No session for user'},
                status=404
            )
    elif request.method == 'POST':
        if user.is_authenticated():
            return JsonResponse({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }, status=200)
        else:
            parseable_post = request.body.decode('utf8').replace("'", '"')
            parsed_post = loads(parseable_post)
            request_username = parsed_post.get('username')
            request_password = parsed_post.get('password', '')
            user = authenticate(username=request_username, password=request_password)
            if user:
                login(request, user)
                return JsonResponse({
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }, status=201)
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


@login_required
@csrf_exempt
def ReportView(request, report_id=None):
    if request.method not in ['GET', 'POST', 'DELETE']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)
    def _shape(report):
        return {
            'id': report.id,
            'staff': report.staff.id,
            'title': report.title,
            'query': report.query,
            'created_on': report.created_on,
            'updated_on': report.updated_on,
            'source_report': report.source_report,
        }
    requesting_staff = Staff.objects.get(user=request.user)
    if request.method == 'GET':
        if report_id:
            requested_report = get_object_or_404(Report, pk=report_id)
            return JsonResponse(_shape(requested_report), status=200)
        else:
            requested_reports = Report.objects.filter(staff=requesting_staff)
            return JsonResponse(
                {'data': [_shape(requested_reports) for r in requested_reports]}
            )

    if request.method == 'POST':
        parseable_post = request.body.decode('utf8').replace("'", '"')
        parsed_post = loads(parseable_post)
        if parsed_post.get('report_id'):
            reportForUpdate = Report.objects.get(id=parsed_post.get('report_id'))
            reportForUpdate.title = parsed_post.get('title')
            reportForUpdate.query = parsed_post.get('query')
            reportForUpdate.save()
            return JsonResponse({'data': 'success'}, status=200)
        else:
            if Report.objects.filter(staff=requesting_staff, query=parsed_post.get('query')).exists():
                return JsonResponse({
                    'error': 'Report already exists.'
                }, status=400)
            new_report = Report(
                staff=requesting_staff,
                title=parsed_post.get('title'),
                query=parsed_post.get('query')
            )
            new_report.save()
            return JsonResponse({'data': _shape(new_report)}, status=201)
    if request.method == 'DELETE':
        if not report_id:
            return JsonResponse({'error': 'report_id is required'}, status=400)
        requested_report = get_object_or_404(Report, pk=report_id, staff=requesting_staff)
        requested_report.delete()
        return HttpResponse(status=200)


@login_required
@csrf_exempt
def WorksheetView(request):
    if request.method not in ['GET']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)

    def _shape(worksheet):
        return {
            'id': worksheet.id,
            'title': worksheet.title,
            'reports': [
                {
                    'id': r.id,
                } for r in worksheet.reports.all()
            ],
        }
    requesting_staff = Staff.objects.get(user=request.user)
    user_worksheets = Worksheet.objects.filter(staff=requesting_staff)
    return JsonResponse({'data': [_shape(w) for w in user_worksheets]}, status=200)


@login_required
@csrf_exempt
def WorksheetMembershipView(request):
    def _shape(worksheet_membership):
        return {
            'report_id': worksheet_membership.report.id,
            'worksheet_id': worksheet_membership.worksheet.id,
            'created_on': worksheet_membership.created_on,
            'updated_on': worksheet_membership.updated_on,
        }
    if request.method not in ['POST']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)
    requesting_staff = Staff.objects.get(user=request.user)
    parseable_post = request.body.decode('utf8').replace("'", '"')
    parsed_post = loads(parseable_post)
    report_id = parsed_post.get('report_id')
    if not report_id:
        return JsonResponse({
            'error': 'Missing required parameters'
        }, status=400)
    report = get_object_or_404(Report, pk=report_id)

    target_worksheet_id = parsed_post.get('target_worksheet')
    target_worksheet = None
    if target_worksheet_id:
        target_worksheet = get_object_or_404(Worksheet, pk=target_worksheet_id)
    else:
        # If the client didn't specify a worksheet, try to grab the user's default
        target_worksheet = Worksheet.objects.filter(staff=requesting_staff).first()
        if not target_worksheet:
            # The user doesn't have a worksheet yet! That means it's their first
            # time saving a report. So let's create a worksheet for them to save
            target_worksheet = Worksheet(
                staff=requesting_staff,
                title="{}'s first worksheet".format(requesting_staff)
            )
            target_worksheet.save()
    if WorksheetMembership.objects.filter(report=report, worksheet=target_worksheet).exists():
        return JsonResponse({
            'error': 'Worksheet membership already exists'
        }, status=400)

    new_worksheet_membership = WorksheetMembership(
        report=report,
        worksheet=target_worksheet
    )
    new_worksheet_membership.save()
    return JsonResponse({
        'data': _shape(new_worksheet_membership),
    }, status=201)
