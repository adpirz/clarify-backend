import requests
import json
import base64
import urllib
from django.contrib.auth import login

from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint
from requests import HTTPError

from clarify.models import CleverCode, UserProfile, Student, Section, \
    EnrollmentRecord, SectionGradeLevels
from clarify.sync import CleverSync
from decorators import require_methods


CLEVER_CLIENT_ID = settings.CLEVER_CLIENT_ID
CLEVER_CLIENT_SECRET = settings.CLEVER_CLIENT_SECRET
CLEVER_REDIRECT_URL = settings.CLEVER_REDIRECT_URL

@csrf_exempt
@require_methods('POST')
def CleverTokenView(request):
    data = json.loads(request.body)
    code = data["code"]
    clever_code, created = CleverCode.objects.get_or_create(code=code)

    if not created and clever_code.user_id is not None:
        login(request, user=clever_code.user)
        return JsonResponse({
            "data": "login success"
        }, status=201)

    if not created:

        return JsonResponse({

        }, status=401)

    auth = base64.b64encode(f"{CLEVER_CLIENT_ID}:{CLEVER_CLIENT_SECRET}"
                            .encode("ascii")).decode('utf-8')

    auth_string = f"Basic {auth}"
    resp = requests.post("https://clever.com/oauth/tokens",
                          headers={
                              "Authorization": auth_string
                          },
                          json={
                              "code": code,
                              "grant_type": "authorization_code",
                              "redirect_uri": CLEVER_REDIRECT_URL
                          })

    try:
        resp.raise_for_status()
    except HTTPError as e:
        return JsonResponse({}, status=400)

    data = resp.json()

    bearer_token = data["access_token"]

    clever_id = get_clever_user_id_from_token(bearer_token)


    #  --- DELETE THIS , TESTING ONLY ----

    sync = CleverSync(bearer_token)
    sync.create_all_for_staff_from_source(clever_id)


    # ---- END DELETE -------


    u = UserProfile.objects.filter(clever_id=clever_id).first()

    if not u:
        u = first_clever_login(clever_id, bearer_token)

    u.clever_token = bearer_token
    u.save()

    login(request, u.user)

    clever_code.user = u
    clever_code.save()

    return JsonResponse({
        "data": "success"
    }, status=201)


def get_clever_user_id_from_token(bearer_token):
    req = requests.get(
        url="https://api.clever.com/v2.0/me",
        headers={
            "Authorization": f"Bearer {bearer_token}"
        }
    )

    req.raise_for_status()

    data = req.json()["data"]

    return data["id"]


def first_clever_login(clever_id, bearer_token):
    sync = CleverSync(bearer_token)
    profile, created = sync.get_or_create_staff(clever_id)

    if not created:
        return profile

    students = sync.get_source_related_students_for_staff_id(profile.id)

    # { clever_id: <StudentInstance> }
    # We use this first to create students, then associate
    # them with enrollment records and grade_levels

    student_map = {}

    for student in students:
        student_clever_id = student["id"]
        student_map[student_clever_id] = Student(
            first_name=student["name"]["first"],
            last_name=student["name"]["last"],
            clever_id=student_clever_id
        )

    sections = sync.get_source_related_sections_for_staff_id(profile.id)

    # { clever_id: (<SectionInstance>, [student_clever_ids], grade_level) }
    section_map = {}

    for section in sections:
        section_clever_id = section["id"]
        name = section["name"]
        course_name = name.split(" - ")[0]
        section_map[section_clever_id] = (Section(
            name=name,
            course_name=course_name,
            clever_id=section_clever_id
        ), section["students"], section["grade"])

    Student.objects.bulk_create(student_map.values())
    Section.objects.bulk_create([s[0] for s in section_map.values()])

    enrollment_list = []

    for clever_section_id, info in section_map.items():
        section, student_list, grade = info

        SectionGradeLevels.objects.get_or_create(
            section=section,
            grade_level=grade
        )

        for clever_student_id in student_list:
            student = student_map[clever_student_id]
            enrollment_list.append(EnrollmentRecord(
                student=student,
                section=section
            ))

    EnrollmentRecord.objects.bulk_create(enrollment_list)

    return profile
