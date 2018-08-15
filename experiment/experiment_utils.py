from sis_mirror.models import Gradebooks


def get_date_filter_for_gradebooks():
    base_through_string = "__".join([
        "gradebooksectioncourseaff",
        "section",
        "sectiongradingperiodaff",
        "grading_period",
        "grading_period_start_date"
    ])

    return {f"{base_through_string}__gte": "2017-07-31",
               f"{base_through_string}__lte": "2017-09-01"}


def get_all_users_for_set_dates():
    return Gradebooks.objects.filter(
        **get_date_filter_for_gradebooks()
    ).distinct('created_by_id').values_list('created_by_id', flat=True)