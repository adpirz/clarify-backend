from django.utils import timezone
from json import loads
from datetime import datetime

from google.oauth2 import id_token
from google.auth.transport import requests

from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Case, When, Value, BooleanField, Q, F
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from clarify.models import Student, Section, EnrollmentRecord, StaffSectionRecord
from deltas.models import Action, Delta
from clarify_backend.utils import get_academic_year

from decorators import requires_user_profile, require_methods


@login_required(login_url="/")
@require_methods("GET")
def UserView(request):
    user = request.user
    response = {
        'data': {
            'id': user.id,
            'user_profile_id': user.userprofile.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'sis_enabled': not bool(user.userprofile.clever_token),
        }
    }
    if user.userprofile:
        response["data"]["prefix"] = user.userprofile.get_prefix_display()
    return JsonResponse(response)


@login_required
@require_methods("GET")
@requires_user_profile
def StudentView(request, requesting_user_profile):
    # TODO: Make this work for an admin account

    def _shape(student, student_section_pairs):
        return {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name if not settings.ANONYMIZE_STUDENTS else student.last_name[0],
            'is_enrolled': True,
            'enrolled_section_ids': [ssp.section_id for ssp in student_section_pairs if ssp.id == student.id]
        }

    student_section_pairs = requesting_user_profile.get_enrolled_students()

    unique_students = student_section_pairs.distinct('id')


    return JsonResponse({
        'data': [_shape(s, student_section_pairs) for s in unique_students]
    })


@login_required
@require_methods("GET")
@requires_user_profile
def SectionView(request, requesting_user_profile):
    # TODO: make work for admins:

    def _shape(section):
        return {
            'id': section["id"],
            'section_name': section["name"],
        }

    sections = Section.objects.filter(
        staffsectionrecord__active=True,
        staffsectionrecord__user_profile_id=requesting_user_profile.id
    ).values('id', 'name')

    return JsonResponse({
        'data': [_shape(s) for s in sections]
    })


@csrf_exempt
@require_methods("GET", "POST", "DELETE")
def SessionView(request):
    def _user_response_shape(user):
        response = {
            'data': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
        }
        if user.userprofile:
            response["data"]["prefix"] = user.userprofile.get_prefix_display()

        return response

    if settings.IMPERSONATION and request.method == 'GET'\
            and request.GET.get('user_id', None):

        if request.user and request.user.is_authenticated:
            return JsonResponse(_user_response_shape(request.user), status=200)

        user_id = request.GET.get('user_id')
        user = get_object_or_404(User, id=user_id)
        login(request, user)

        return JsonResponse(_user_response_shape(user), status=201)

    user = request.user
    if request.method == 'GET':
        if user.is_authenticated():
            return JsonResponse(_user_response_shape(user), status=200)
        else:
            return JsonResponse(
                {'error': 'No session for user'},
                status=404
            )
    elif request.method == 'POST':
        parseable_post = request.body.decode('utf8').replace("'", '"')
        parsed_post = loads(parseable_post)
        request_google_token = parsed_post.get('google_token', '')
        user = None
        if request_google_token:
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
        else:
            username = parsed_post.get('username')
            password = parsed_post.get('password')
            user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                return JsonResponse({
                    'error': 'user-inactive'
                }, status=403)

            login(request, user)
            return JsonResponse(_user_response_shape(user), status=201)
        else:
            return JsonResponse({
                'error': 'invalid-credentials'
            }, status=401)
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
@require_methods("GET")
@requires_user_profile
def DeltaView(request, requesting_user_profile, student_id=None):
    delta_type = request.GET.get('type', None)

    deltas = Delta.return_response_query(
        requesting_user_profile.id,
        student_id,
        delta_type
    )

    def _shape_context_record(record):
        return {
            "category_id": record.category_id,
            "category_name": record.category.name,
            "date": record.date,
            "total_points_possible": record.total_points_possible,
            "average_points_earned": record.average_points_earned
        }

    def _shape_missing_record(record):
        return {
            "assignment_name": record.assignment.name,
            "assignment_id": record.assignment_id,
            "due_date": record.assignment.due_date,
            "missing_on": record.missing_on
        }

    def _shape_delta(delta):

        resp = {
            "delta_id": delta.id,
            "student_id": delta.student_id,
            "created_on": delta.created_on,
            "updated_on": delta.updated_on,
            "type": delta.type,
            "gradebook_name": delta.gradebook.name,
            "gradebook_id": delta.gradebook_id
        }

        if delta.type == "missing":
            resp["missing_assignments"] = [
                _shape_missing_record(a) for a in
                delta.missingassignmentrecord_set.all()
            ]
            resp["sort_date"] = delta.created_on

        if delta.type == "category":
            score = {
                "assignment_id": delta.score.assignment_id,
                "score_id": delta.score.id,
                "assignment_name": delta.score.assignment.name,
                "score": delta.score.score,
                "possible_points": delta.score.assignment.possible_points,
                "due_date": delta.score.assignment.due_date,
                "last_updated": delta.score.last_updated
            }
            resp["score"] = score
            resp["context_record"] = _shape_context_record(delta.context_record)
            resp["category_average_before"] = delta.category_average_before
            resp["category_average_after"] = delta.category_average_after
            resp["sort_date"] = delta.score.assignment.due_date

        return resp

    return JsonResponse({
        'data': [_shape_delta(d) for d in deltas]
    })


@login_required
@require_methods("GET", "PUT", "POST", "DELETE")
@requires_user_profile
def ActionView(request, requesting_user_profile, action_id=None):
    def _shape(action):
        return {
            'id': action.id,
            'completed_on': action.completed_on,
            'created_by': {
                'user_profile_id': action.created_by_id,
                'first_name': action.user_first_name,
                'last_name': action.user_last_name,
            },
            'due_on': action.due_on,
            'type': action.type,
            'student_id': action.student_id,
            'delta_ids': [d.id for d in action.deltas.all()],
            'created_on': action.created_on,
            'updated_on': action.updated_on,
            'note': action.note,
            'public': action.public,
        }
    if request.method == 'GET':
        staff_students = (requesting_user_profile
                          .get_enrolled_students()
                          .values())

        student_actions = (
            Action.objects
                .filter(student__in=[s["id"] for s in staff_students])
                .prefetch_related('deltas__id')
                .annotate(user_first_name=F('created_by__user__first_name'),
                          user_last_name=F('created_by__user__last_name'))
                .filter(Q(created_by=requesting_user_profile) | Q(public=True))
        )

        return JsonResponse({'data': [_shape(action) for action in student_actions]})

    elif request.method == 'DELETE':
        action = get_object_or_404(Action, id=action_id)
        if requesting_user_profile != action.created_by:
            return JsonResponse(
                {'error': 'You cannot delete an action you do not own.'},
                status=403)
        else:
            action.delete()
            return HttpResponse(status=204)

    parseable_post = request.body.decode('utf8')
    if not parseable_post:
        return JsonResponse(
            {'error': 'Request body must be present'},
            status=400)

    parsed_post = loads(parseable_post)

    if request.method == 'POST':
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

        new_action = (Action(
                        student=target_student,
                        note=parsed_post.get('note'),
                        created_by=requesting_user_profile,
                        public=bool(parsed_post.get('public'))))

        due_on = parsed_post.get('due_on')
        completed_on = parsed_post.get('completed_on')

        if due_on:
            try:
                due_on = datetime.strptime(due_on, '%m/%d/%Y %H:%M')
                new_action.due_on = due_on
            except:
                return JsonResponse(
                    {'error': 'Due date must be in the format mm/dd/yyyy HH:MM'},
                    status=400)

        if completed_on:
            try:
                completed_on = datetime.strptime(completed_on, '%m/%d/%Y %H:%M')
                new_action.completed_on = completed_on
            except:
                return JsonResponse(
                    {'error': 'Completed date must be in the format mm/dd/yyyy HH:MM'},
                    status=400)

        if parsed_post.get('type'):
            new_action.type = parsed_post.get('type')


        new_action.save()

        delta_ids = parsed_post.get('delta_ids')
        if delta_ids:
            if isinstance(delta_ids, list):
                new_action.deltas = delta_ids
                new_action.save()
            else:
                new_action.delete()
                return JsonResponse(
                    {'error': 'Deltas must be a list. Action was not created.'},
                    status=400)

        return JsonResponse(
            {'data': _shape(new_action)},
            status=201)
    else:
        # Method is PUT
        action_id = parsed_post.get('action_id')
        action = get_object_or_404(Action, id=action_id)

        if requesting_user_profile != action.created_by:
            return JsonResponse(
                {'error': 'You cannot update an action you do not own.'},
                status=403)

        student_id = parsed_post.get('student_id')

        if student_id:
            try:
                target_student = Student.objects.get(id=student_id)
                action.student = target_student
            except Student.DoesNotExist:
                return JsonResponse(
                    {'error': 'Target student could not be found'},
                    status=404)

        new_note = parsed_post.get('note')
        if new_note:
            action.note = new_note

        due_on = parsed_post.get('due_on')
        completed_on = parsed_post.get('completed_on')

        if due_on:
            try:
                due_on = datetime.strptime(due_on, '%m/%d/%Y %H:%M')
                action.due_on = due_on
            except:
                return JsonResponse(
                    {'error': 'Due date must be in the format mm/dd/yyyy HH:MM'},
                    status=400)

        if completed_on:
            try:
                completed_on = datetime.strptime(completed_on, '%m/%d/%Y %H:%M')
                action.completed_on = completed_on
            except:
                return JsonResponse(
                    {'error': 'Completed date must be in the format mm/dd/yyyy HH:MM'},
                    status=400)

        if parsed_post.get('type'):
            action.type = parsed_post.get('type')

        action.save()

        deltas = parsed_post.get('deltas')
        if deltas:
            if isinstance(deltas, list):
                action.deltas = deltas
                action.save()
            else:
                return JsonResponse(
                    {'error': 'Deltas must be a list. This update to action deltas was ignored.'},
                    status=400)

        return JsonResponse(
            {'data': _shape(action)},
            status=200)
