import requests
import json
import base64
import urllib
from pprint import pprint
from requests import HTTPError

from django.contrib.auth import login
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from clarify.models import CleverAuth, GoogleAuth, UserProfile, Student, \
    Section, EnrollmentRecord, SectionGradeLevels
from clarify.sync import CleverSync, GoogleClassroomSync
from decorators import require_methods, requires_user_profile
from django import forms
from clarify_backend.utils import manually_roster_with_file

CLEVER_CLIENT_ID = settings.CLEVER_CLIENT_ID
CLEVER_CLIENT_SECRET = settings.CLEVER_CLIENT_SECRET
CLEVER_REDIRECT_URL = settings.CLEVER_REDIRECT_URL


GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly'
]


class UploadFileForm(forms.Form):
    file = forms.FileField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.EmailField()
    temporary_password = forms.CharField()
    prefix = forms.CharField()
    school_name = forms.CharField()


@login_required
@require_methods("GET", "POST")
def handleManualRosterUpload(request):
    if not request.user.is_superuser:
        return HttpResponse(status=400)

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            manually_roster_with_file(request.FILES['file'], **form.cleaned_data)
            return HttpResponse("Success", status=200)
        else:
            return HttpResponse("FAILURE", status=400)
    else:
        return render(request, 'manual_upload.html', {'form': UploadFileForm})


@csrf_exempt
@require_methods('POST')
def CleverTokenView(request):
    data = json.loads(request.body)
    code = data["code"]
    clever_code = CleverAuth.objects.filter(code=code)

    if clever_code.exists():
        user = clever_code.first().user.user
        login(request, user)
        return JsonResponse({
            "data": "login success"
        }, status=201)

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

    user_profile = UserProfile.objects.filter(clever_id=clever_id).first()
    login(request, user_profile.user)

    try:
        CleverAuth.objects.create(
            code=code,
            user_profile=user_profile,
            clever_token=bearer_token
        )
    except IntegrityError:
        clever_code = CleverAuth.objects.get(
            code=code
        )
        clever_code.user = u
        clever_code.save()

    return JsonResponse({
        "data": "success"
    }, status=201)


@csrf_exempt
@require_methods('POST')
def GoogleTokenView(request):
    data = json.loads(request.body)
    google_access_token = data["google_access_token"]
    google_id_token = data["google_id_token"]

    google_sync = GoogleClassroomSync(google_access_token)
    new_user_profile = google_sync.create_all_for_staff_from_source()
    # For some reason that boggles my mind looking up this user a-new allows the login/session state
    # to persist when the client subsequently calls for user info. Just using the new_user_profile
    # that's returned above does not 🤷🏻‍.
    new_user = UserProfile.objects.filter(google_id=new_user_profile.google_id).first().user

    login(request, new_user)

    try:
        GoogleAuth.objects.create(
            user_profile=new_user_profile,
            google_token=google_access_token,
            id_token=google_id_token,
        )
    except:
        # Probs already created
        pass

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