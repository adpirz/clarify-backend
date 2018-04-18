from json import loads
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

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
    person = Person('en')
    return JsonResponse({
        'data': [{"id": i, "name": person.full_name()} for i in range(0,25)]
    })

@login_required
def SectionView(request):
    return JsonResponse({
        'data': [
            {
                'name': 'Community 101',
                'id': '2341',
            },
            {
                'name': 'Back to the Future 102',
                'id': '236',
            },
            {
                'name': 'Harry Potter 101',
                'id': '4685',
            },
            {
                'name': 'Game of Thrones 101',
                'id': '1508',
            },
        ]
    })

@login_required
def GradeLevelView(request):
    return JsonResponse({
        'data': [
            {
                'name': 'Community Course',
                'id': '2341',
            },
            {
                'name': 'Back to the Future',
                'id': '236',
            },
            {
                'name': 'Harry Potter',
                'id': '4685',
            },
            {
                'name': 'Game of Thrones',
                'id': '1508',
            },
        ]
    })

@login_required
def SchoolView(request):
    return JsonResponse({
        'data': [
            {
                'name': 'Central High School',
                'id': '2341',
            },
            {
                'name': 'Saint Paul Academy',
                'id': '236',
            },
            {
                'name': 'Archbishop Mitty',
                'id': '4685',
            },
            {
                'name': 'Richard Montgomery High School',
                'id': '1508',
            },
        ]
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
            requestPassword = parsedPost.get('password')
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
