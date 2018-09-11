from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

from experiment.experiment_utils import get_all_users_for_set_dates, \
    get_date_filter_for_gradebooks
from sis_mirror.models import Users, Gradebooks, Assignments, Scores, \
    Categories, Students

from .models import StudentWeekCategoryScore, Standout


class UserSelectionView(ListView):
    queryset = Users.objects.filter(
        user_id__in=get_all_users_for_set_dates()
    )

    template_name = "user_select.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    model = Users
    template_name = "user_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["standouts"] = Standout.objects.filter(
            user_id=self.get_object().pk
        ).order_by('-date','student_id').all()
        return context


class UserGradebookSelect(ListView):
    context_object_name = "gradebooks"
    template_name = "user_gb_list.html"

    def get_queryset(self):
        filters = get_date_filter_for_gradebooks()
        filters["created_by_id"] = self.kwargs["user_id"]
        return Gradebooks.objects.filter(
            **filters
        ).distinct('gradebook_id').all()


def gradebook_view(request, gradebook_id):
    gb = Gradebooks.objects.get(gradebook_id=gradebook_id)
    context_dict = {
        "gradebook_name": gb.gradebook_name,
        "user": gb.created_by
    }

    context_dict["data"] = StudentWeekCategoryScore\
        .get_all_scores_for_all_timespans(gradebook_id)

    return render(
        request, context=context_dict, template_name="gradebook_view.html"
    )

@csrf_exempt
def create_standout(request):
    if not request.POST:
        return JsonResponse({}, status=200)

    user_id = request.POST.get('user_id')
    student_id = request.POST.get('studentId')
    date = request.POST.get('date')
    text = request.POST.get('text')
    standout_type = request.POST.get('type')

    try:
        s = Standout.objects.create(
            user_id=user_id, student_id=student_id,
            date=date, text=text, standout_type=standout_type
        )
        return JsonResponse({
            "standout_id": s.pk
        }, status=201, safe=False)

    except IntegrityError as e:
        print(e)
        return JsonResponse({}, status=201)


def student_view(request, student_id):
    student = get_object_or_404(Students, pk=student_id)

    return JsonResponse(
        {'student_id': student_id,
         'first_name': student.first_name,
         'last_name': student.last_name,
         }, status=200
    )


def assignments_view(request, student_id, gradebook_id,
                     start_date, end_date, category_id=None):

    context_dict = {
        "student_id": student_id, "gradebook_id": gradebook_id,
        "start_date": start_date, "end_date": end_date
    }
    scores = Scores.objects.filter(
        student_id=student_id,
        gradebook_id=gradebook_id,
        created__gte=start_date,
        created__lte=end_date,
    )

    if category_id:
        scores = scores.filter(assignment__category_id=category_id)
        context_dict["category_name"] = Categories.objects\
            .get(category_id=category_id).category_name

    context_dict["data"] = scores.values(
        'student_id', 'gradebook_id', 'assignment__category_id', 'created',
        'assignment__short_name', 'assignment__possible_points', 'value'
    )

    return render(
        request, context=context_dict, template_name="assignments_view.html"
    )