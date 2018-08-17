from django.conf.urls import url

from .views import UserSelectionView, UserDetailView, UserGradebookSelect, gradebook_view, assignments_view

DATE_RE = '\d{4}\-\d{2}\-\d{2}'
urlpatterns = [
    url('^$', UserSelectionView.as_view(), name="user_select"),
    url('user/(?P<pk>\d+)/$', UserDetailView.as_view(), name="user_detail"),
    url('user/(?P<user_id>\d+)/gradebooks/$', UserGradebookSelect.as_view(),
        name="user_gb_select"),
    url('gradebook/(?P<gradebook_id>\d+)/$', gradebook_view, name="gradebook_detail"),
    url('assignments/(?P<student_id>\d+)/(?P<gradebook_id>\d+)/' +
        f'(?P<start_date>{DATE_RE})/(?P<end_date>{DATE_RE})/' +
        '(?P<category_id>\d+)/', assignments_view, name="assignments_detail")
]