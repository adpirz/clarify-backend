from django.utils import timezone
from json import loads

from google.oauth2 import id_token
from google.auth.transport import requests

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Case, When, Value, BooleanField
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from sis_pull.models import (
    Student, Section, GradeLevel, Site, Staff,
    SectionLevelRosterPerYear,
    StaffTermRoleAffinity)
from reports.models import Report, ReportShare
from mimesis import Person
from utils import get_academic_year


@login_required
def UserView(request):
    if request.method == 'GET':
        user = request.user
        return JsonResponse({
            'data': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
        })


@login_required
def StudentView(request):
    def _shape(student):
        return {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'is_enrolled': student.is_enrolled,
            'is_searchable': student.is_searchable,
        }

    try:
        request_staff = request.user.staff
    except:
        return JsonResponse(
            {'error': 'No staff for that user'},
            status=401
        )

    staff_level = request_staff.get_max_role_level()
    staff_site_id = request_staff.get_most_recent_primary_site_id()

    if not staff_level:
        return JsonResponse(
            {'error': 'Could not determine staff level'},
            status=400
        )

    if not staff_site_id:
        return JsonResponse(
            {'error': 'Could not determine site for that staff'},
            status=400
        )

    site_student_ids = (SectionLevelRosterPerYear.objects
        .filter(site_id=staff_site_id)
        .filter(academic_year=get_academic_year())
        .values_list('student_id')
    )

    if staff_level < 700:
        # Staff member isn't an admin. The client should only allow them to
        # search for students that they teach. Indicate which students those are.
        staff_student_ids = (SectionLevelRosterPerYear.objects
            .filter(staff=request_staff)
            .filter(academic_year=get_academic_year())
            .values_list('student_id')
        )
    else:
        # Staff is an admin, which means they can see all students at their site
        staff_student_ids = site_student_ids

    staff_students = (Student.objects.filter(id__in=site_student_ids)
                      .annotate(is_searchable=Case(
                        When(id__in=staff_student_ids, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                      ))
                      .annotate(is_enrolled=Case(
                        When(currentroster__isnull=False, then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                      )))

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
            .filter(staff=request_teacher.first())
            .filter(academic_year=get_academic_year())
            .filter(section__section_name__isnull=False)
            # .exclude(section__section_name__exact="")
            .values_list('section_id')
        )
        staff_sections = Section.objects.filter(id__in=teacher_section_ids)
    else:
        current_site_id = user.staff.get_most_recent_primary_site_id()
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
            .filter(staff=request_teacher.first())
            .filter(academic_year=get_academic_year())
            .values_list('grade_level_id')
        )
        staff_grade_levels = GradeLevel.objects.filter(
            id__in=teacher_grade_level_ids
        )
    else:
        current_site_id = user.staff.get_most_recent_primary_site_id()
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
        filter_kwargs["staff"] = request_staff
    else:
        filter_kwargs["site_id"] = request_staff.get_most_recent_primary_site_id()

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
        .filter(staff=request_teacher.first())
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
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }, status=200)
        else:
            return JsonResponse(
                {'error': 'No session for user'},
                status=404
            )
    elif request.method == 'POST':
        if user.is_authenticated():
            return JsonResponse({
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            }, status=200)
        else:
            parseable_post = request.body.decode('utf8').replace("'", '"')
            parsed_post = loads(parseable_post)
            request_google_token = parsed_post.get('google_token', '')
            try:
                idinfo = id_token.verify_oauth2_token(
                    request_google_token,
                    requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
            except ValueError:
                return JsonResponse(
                    {'error': 'google-auth'},
                    status=400)
            email = idinfo["email"]
            try:
                # In Illuminate, no email objects stored
                user = User.objects.get(username=email)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                return JsonResponse(
                    {'error': 'user-lookup'},
                    status=400
                )
            if user:
                if not user.is_active:
                    return JsonResponse({
                        'error': 'user-inactive'
                    }, status=403)

                login(request, user)
                return JsonResponse({
                    'data': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                    }
                }, status=201)
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
        report_shape = {
            'id': report.id,
            'staff': str(report.staff),
            'query': report.query,
            'created_on': report.created_on,
            'updated_on': report.updated_on,
        }

        report_children = ReportShare.objects.filter(parent=report)
        if len(report_children):
            report_shape['shared_with'] = [{
                'staff': str(r.child.staff),
                'note': r.note,
            } for r in report_children]

        report_parent = ReportShare.objects.filter(child=report)
        if len(report_parent):
            report_share = report_parent.first()
            report_shape['shared_by'] = {
                'staff': str(report_share.shared_by),
                'note': report_share.note,
            }

        return report_shape

    requesting_staff = Staff.objects.get(user=request.user)

    if request.method == 'GET':
        if report_id:
            requested_report = get_object_or_404(Report, pk=report_id)
            return JsonResponse({'data': _shape(requested_report)}, status=200)
        else:
            requested_reports = Report.objects.filter(staff=requesting_staff)
            return JsonResponse(
                {'data': [_shape(r) for r in requested_reports]}
            )


    if request.method == 'POST':
        parseable_post = request.body.decode('utf8').replace("'", '"')
        parsed_post = loads(parseable_post)

        query = parsed_post.get('query')
        staff_id_for_report = parsed_post.get('staff_id_for_report', requesting_staff.id)
        if not query:
            return JsonResponse({
                'error': 'Missing required parameters'
            }, status=400)

        staff_for_report = Staff.objects.filter(id=staff_id_for_report)

        if not len(staff_for_report):
            return JsonResponse({
                'error': 'That staff member does not exist'
            }, status=400)

        existing_report = Report.objects.filter(query=query, staff=staff_for_report)
        if existing_report.exists():
            return JsonResponse(
                       {'data': _shape(existing_report.first())},
                       status=200,
                   )

        new_report = Report(
            staff=staff_for_report.first(),
            query=query,
        )
        new_report.save()

        return JsonResponse(
                   {'data': _shape(new_report)},
                   status=201,
               )
    if request.method == 'DELETE':
        if not report_id:
            return JsonResponse({'error': 'report_id is required'}, status=400)
        requested_report = get_object_or_404(Report, pk=report_id, staff=requesting_staff)
        requested_report.delete()
        return HttpResponse(status=200)


@login_required
@csrf_exempt
def ReportShareView(request):
    def _shape(report_share):
        shape_object = {
            'child_report': {
                'id': report_share.child.id,
                'staff': str(report_share.child.staff),
                'created_on': report_share.child.created_on,
                'updated_on': report_share.child.updated_on,
            },
            'shared_by': str(report_share.shared_by),
            'created_on': report_share.created_on,
            'updated_on': report_share.updated_on,
            'note': report_share.note,
        }

        if report_share.parent:
            shape_object['parent_report'] = {
                'id': report_share.parent.id,
                'created_on': report_share.parent.created_on,
                'updated_on': report_share.parent.updated_on,
            }

        return shape_object

    if request.method not in ['POST', 'GET']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)

    requesting_staff = Staff.objects.get(user=request.user)

    if request.method == 'GET':
        requesting_staff_shares = (ReportShare.objects
                                       .filter(
                                           Q(parent__staff=requesting_staff)
                                           | Q(child__staff=requesting_staff)
                                       )
                                   )
        return JsonResponse({
            'data': [_shape(r) for r in requesting_staff_shares]
        }, status=405)
    elif request.method == 'POST':
        parseable_post = request.body.decode('utf8').replace("'", '"')
        parsed_post = loads(parseable_post)
        parent_report_id = parsed_post.get('parent_report_id')
        child_report_id = parsed_post.get('child_report_id')
        note = parsed_post.get('note')

        if not child_report_id:
            return JsonResponse({
                'error': 'Missing required parameters'
            }, status=400)

        parent_report = Report.objects.filter(id=parent_report_id)
        child_report = Report.objects.filter(id=child_report_id)

        if (parent_report_id and not len(parent_report)) or not len(child_report):
            return JsonResponse({
                'error': 'Either parent or child report do not exist anymore'
            }, status=400)

        new_report_share = ReportShare(
                              parent=parent_report.first(),
                              child=child_report.first(),
                              shared_by=requesting_staff,
                              note=note)
        new_report_share.save()
        return JsonResponse({
            'data': _shape(new_report_share),
        }, status=201)


@login_required
@csrf_exempt
def StaffView(request):
    def _shape(staff):
        return {
            'id': staff.id,
            'name': str(staff),
        }

    if request.method not in ['GET']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)

    requesting_staff = request.user.staff
    requesting_user_site_id = requesting_staff.get_most_recent_primary_site_id()

    # most recent active term for a user
    term = (StaffTermRoleAffinity.objects
            .filter(term__session__site_id=requesting_user_site_id)
            .filter(term__start_date__lte=timezone.now())
            .order_by('-term__end_date', '-role__role_level')
            .first()
            )

    if term:
        # get all staff for current term who are "teacher" or "principal" roles
        staff_for_term_and_site = (
            StaffTermRoleAffinity.objects
            .filter(term=term.term_id)
            # Filter for teacher, site admin, learning coach
            .filter(role_id__in=(4, 5, 8))
            .exclude(staff=requesting_staff)
            .exclude(staff__user__is_active=False)
            .distinct('staff_id')
            .values_list('staff_id', flat=True)
        )

        staff_records = Staff.objects.filter(id__in=staff_for_term_and_site)
        data = [_shape(staff) for staff in staff_records]
    else:
        data = []

    return JsonResponse({
        'data': data,
    }, status=200)
