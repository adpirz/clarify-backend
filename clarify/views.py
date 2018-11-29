import requests
import json
import base64
import urllib
from django.contrib.auth import login
from django.db import IntegrityError

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
    clever_code = CleverCode.objects.filter(code=code)

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

    u = UserProfile.objects.filter(clever_id=clever_id).first()

    u.clever_token = bearer_token
    u.save()

    login(request, u.user)

    try:
        CleverCode.objects.create(
            code=code,
            user=u
        )
    except IntegrityError:
        clever_code = CleverCode.objects.get(
            code=code
        )
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
