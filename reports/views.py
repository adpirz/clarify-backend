import random
from json import loads
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from sis_pull.models import Student, AttendanceDailyRecord

from mimesis import Person
# Create your views here.


@login_required
def ReportView(request):
    def _get_mock_attendance_data(student):
        generator_ceiling = 100
        data = {}
        for (code, label) in AttendanceDailyRecord.ATTENDANCE_FLAG_CHOICES:
            percentage_times_one_hundred = random.randint(0, generator_ceiling)
            data[code] = {
                'label': label,
                'value': percentage_times_one_hundred/100,
            }
            generator_ceiling = generator_ceiling - percentage_times_one_hundred
        return data

    data = []
    person = Person('en')
    students = [{"id": i, "name": person.full_name()} for i in range(0,25)]

    if Student.objects.first():
        students = Student.objects.all()
    response_rows = [
        {'student_id': s.get('id'), 'data': _get_mock_attendance_data(s)} for s in students
    ]
    return JsonResponse({'data': response_rows})
