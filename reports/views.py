import random
from json import loads
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from sis_pull.models import Student, AttendanceDailyRecord

from mimesis import Person

from .report_builder import query_to_data
# Create your views here.


@login_required
def ReportView(request):
    return JsonResponse(query_to_data(request.GET))

@login_required
def _ReportView(request):
    def _get_mock_attendance_data(student):
        generator_ceiling = 100
        report_data = {}
        for (code, label) in AttendanceDailyRecord.ATTENDANCE_FLAG_CHOICES:
            percentage_times_one_hundred = random.randint(0, generator_ceiling)
            report_data[code] = {
                'label': label,
                'value': percentage_times_one_hundred/100,
            }
            generator_ceiling = generator_ceiling - percentage_times_one_hundred
        return report_data

    def _get_mock_grades_data(student):
        possible_points = random.randint(1, 500)
        points_earned = random.randint(0, possible_points)
        report_data = {
            'possible_points': possible_points,
            'points_earned': points_earned,
            'percentage': points_earned / possible_points,
        }
        remaining_points = possible_points - points_earned
        for property in ['missing_count', 'zero_count']:
            random_point_share = random.randint(0,remaining_points)
            report_data[property] = random_point_share
            remaining_points -= random_point_share
        report_data['excused_count'] = remaining_points
        return report_data

    reportGroup = request.GET.get('group')
    reportGroupIds = [int(id) for id in request.GET.get(reportGroup + '_ids', []).split(',')]
    reportCategory = request.GET.get('category')
    # reportStartDate = request.GET.get('from')
    # reportEndDate = request.GET.get('to')
    response_rows = []
    person = Person('en')
    students = [{"id": i, "name": person.full_name()} for i in range(0,25)]

    if Student.objects.first():
        students = Student.objects.all()

    if len(reportGroupIds):
        students = filter(lambda s: s.get('id') in reportGroupIds, students)
    if reportCategory == 'attendance':
        response_rows = [
            {'student_id': s.get('id'), 'data': _get_mock_attendance_data(s)} for s in students
        ]
    if reportCategory == 'grades':
        response_rows = [
            {'student_id': s.get('id'), 'data': _get_mock_grades_data(s)} for s in students
        ]
    return JsonResponse({'data': response_rows})
