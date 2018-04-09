from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def TestView(request):
    return JsonResponse({'data': "Hello World"})
