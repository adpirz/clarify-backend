from django.shortcuts import render
from django.views.generic import ListView, DetailView

from experiment.experiment_utils import get_all_users_for_set_dates, \
    get_date_filter_for_gradebooks
from sis_mirror.models import Users, Gradebooks

from .models import StudentWeekCategoryScore


class UserSelectionView(ListView):
    queryset = Users.objects.filter(
        user_id__in=get_all_users_for_set_dates()
    )

    template_name = "user_select.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    model = Users
    template_name = "user_detail.html"


class UserGradebookSelect(ListView):
    context_object_name = "gradebooks"
    template_name = "user_gb_list.html"

    def get_queryset(self):
        filters = get_date_filter_for_gradebooks()
        filters["created_by_id"] = self.kwargs["user_id"]
        return Gradebooks.objects.filter(
            **filters
        ).all()


def gradebook_view(request, gradebook_id):
    return render(
        request, context=data, template_name="gradebook_view.html"
    )