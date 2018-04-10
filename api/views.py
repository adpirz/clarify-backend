from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt

from mimesis import Person

# Create your views here.

def TestView(request):
    return JsonResponse({
        'data': 'Hello world'
    })

def StudentView(request):
    person = Person('en')
    return JsonResponse({
        'data': [{"id": i, "name": person.full_name()} for i in range(0,25)]
    })

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
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Method not allowed.'
        })
    requestUsername = request.POST.get('username')
    requestPassword = request.POST.get('password')
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
