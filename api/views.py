from django.utils import timezone
from json import loads
from datetime import timedelta, datetime
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
    StaffTermRoleAffinity, Assignment, GradebookSectionCourseAffinity,
    Gradebook, Score,)
from deltas.models import Action
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
    def _shape(student, student_section_pairs):
        return {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'is_enrolled': student.is_enrolled,
            'is_searchable': student.is_searchable,
            'enrolled_section_ids': list(set([s[1] for s in student_section_pairs if s[0] == student.id]))
        }

    try:
        requesting_staff = request.user.staff
    except:
        return JsonResponse(
            {'error': 'No staff for that user'},
            status=401
        )

    staff_level = requesting_staff.get_max_role_level()
    staff_site_id = requesting_staff.get_most_recent_primary_site_id()

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

    student_section_pairs = (SectionLevelRosterPerYear.objects
        .filter(site_id=staff_site_id)
        .filter(academic_year=get_academic_year())
        .filter(staff=requesting_staff)
        .values_list('student_id', 'section_id').distinct()
    )
    site_student_ids = [s[0] for s in student_section_pairs]

    if staff_level < 700:
        # Staff member isn't an admin. The client should only allow them to
        # search for students that they teach. Indicate which students those are.
        staff_student_ids = (SectionLevelRosterPerYear.objects
            .filter(staff=requesting_staff)
            .filter(academic_year=get_academic_year())
            .values_list('student_id').distinct()
        )
    else:
        # Staff is an admin, which means they can see all students at their site
        staff_student_ids = site_student_ids


    staff_students = (Student.objects.filter(id__in=staff_student_ids)
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
        'data': [_shape(s, student_section_pairs) for s in staff_students]
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
            .values_list('section_id')
        )
        staff_sections = Section.objects.filter(id__in=teacher_section_ids)
    else:
        # Admins can see all sections at the site.
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
def CourseView(request):
    def _shape(row):
        return {
            'id': row.course.id,
            'short_name': row.course.short_name,
            'long_name': row.course.long_name,
        }

    user = request.user
    requesting_staff = Staff.objects.get(user=user)
    filter_kwargs = {}

    if requesting_staff.get_max_role_level() < 700:
        grade_levels = GradeLevel.get_users_current_grade_levels(requesting_staff)
        filter_kwargs["grade_level_id__in"] = grade_levels
        filter_kwargs["staff"] = requesting_staff
    else:
        filter_kwargs["site_id"] = requesting_staff.get_most_recent_primary_site_id()

    return JsonResponse({
        'data': [_shape(row) for row in SectionLevelRosterPerYear.objects
                 .filter(**filter_kwargs)\
                 .distinct('course_id')
                 ]
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
                user = User.objects.get(email=email)
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
def MissingAssignmentDeltaView(request):
    if request.method not in ['GET']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status_code=405)

    try:
        requesting_staff = request.user.staff
    except:
        return JsonResponse(
            {'error': 'No staff for that user'},
            status=401
        )

    def get_missing_assignments_for_student(student_id, sections, section_gradebook_pairs):
        student_deltas = []
        scores = list(Scores.objects.filter(student_id=student_id))
        for section_id in sections:
            section_deltas = []
            section_gradebooks = list(set([pair[1] for pair in section_gradebook_pairs if pair[0] == section_id]))
            section_assignments = (Assignment.objects
                                  .filter(gradebook__in=section_gradebooks)
                                  .order_by('due_date'))
            missing_assignments = []
            for assignment in section_assignments:
                ontime_scores = [score for score in scores if score.assignment_id == assignment.id and score.created.date() < assignment.due_date]
                for missing_assignment in missing_assignments:
                    ontime_scores = [score for score in scores if score.assignment_id == assignment.id and score.created.date() < assignment.due_date]
                if len(ontime_scores) < 1:
                    # No Score node was created prior to the assignment due_date, it was missing
                    section_deltas.append({
                        'timestamp': assignment.due_date,
                        'assignment': {'name': assignment, 'due_date': assignment.due_date, 'new': True},
                    })
                    missing_assignments.append(assignment)
            student_deltas.append({'section_id': section_id, 'deltas': section_deltas})

        return student_deltas

    student_section_pairs = (SectionLevelRosterPerYear.objects
                            .filter(staff=requesting_staff)
                            .filter(academic_year=get_academic_year())
                            .values_list('student_id', 'section_id')
                            .distinct())

    staff_student_set = list(set([s[0] for s in student_section_pairs]))
    staff_section_set = list(set([s[1] for s in student_section_pairs]))
    section_gradebook_pairs = (GradebookSectionCourseAffinity.objects
                               .filter(staff=requesting_staff)
                               .filter(gradebook__active=True)
                               .filter(gradebook__is_deleted=False)
                               .values_list('section_id', 'gradebook_id'))
    delta_data = []

    for student_id in staff_student_set:
        student_sections = list(set([pair[1] for pair in student_section_pairs if pair[0] == student_id]))
        deltas = get_missing_assignments_for_student(student_id, student_sections, section_gradebook_pairs)

        delta_data.append({
            'student_id': student_id,
            'missing_assignments': deltas
        })

    return JsonResponse({"data": delta_data})


@login_required
def ActionView(request):
    def _shape(action):
        return {
            'completed_on': action.completed_on,
            'created_by': action.created_by.id,
            'due_on': action.due_on,
            'type': action.type,
            'student_id': action.student.id,
            'delta_ids': [d.id for d in action.deltas.all()],
            'created_on': action.created_on,
            'updated_on': action.updated_on,
            'note': action.note,
        }

    if request.method not in ['GET', 'POST']:
        return JsonResponse({
            'error': 'Method not allowed.'
        }, status=405)

    try:
        requesting_staff = request.user.staff
    except:
        return JsonResponse(
            {'error': 'No staff for that user'},
            status=401
        )

    if request.method == 'GET':
        staff_students = (SectionLevelRosterPerYear.objects
                         .filter(staff=requesting_staff)
                         .filter(academic_year=get_academic_year())
                         .values_list('student_id')
                         .distinct())

        student_actions = Action.objects.filter(student__in=staff_students)

        return JsonResponse({'data': [_shape(action) for action in student_actions]})

    if request.method == 'POST':
        parseable_post = request.body.decode('utf8')
        if not parseable_post:
            return JsonResponse(
                {'error': 'Request body must be present'},
                status=400)

        parsed_post = loads(parseable_post)
        student_id = parsed_post.get('student_id')

        if not student_id:
            return JsonResponse(
                {'error': 'Target student is required parameter'},
                status=400)

        try:
            target_student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse(
                {'error': 'Target student could not be found'},
                status=404)

        new_action = (Action.objects.create(
                        student=target_student,
                        note=parsed_post.get('note'),
                        created_by=requesting_staff))

        due_on = parsed_post.get('due_on')
        completed_on = parsed_post.get('completed_on')

        if due_on:
            try:
                due_on = datetime.strptime(due_on, '%m/%d/%Y')
                new_action.due_on = due_on
            except:
                return JsonResponse(
                    {'error': 'Due date must be in the format mm/dd/yyyy'},
                    status=400)

        if completed_on:
            try:
                completed_on = datetime.strptime(completed_on, '%m/%d/%Y')
                new_action.completed_on = completed_on
            except:
                return JsonResponse(
                    {'error': 'Completed date must be in the format mm/dd/yyyy'},
                    status=400)

        if parsed_post.get('type'):
            new_action.type = parsed_post.get('type')


        new_action.save()

        deltas = parsed_post.get('deltas')
        if deltas:
            if isinstance(deltas, list):
                new_action.deltas = deltas
                new_action.save()
            else:
                new_action.delete()
                return JsonResponse(
                    {'error': 'Deltas must be a list. Action was not created.'},
                    status=400)

        return JsonResponse(
            {'data': _shape(new_action)},
            status=201)
