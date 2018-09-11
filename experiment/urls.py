from django.conf.urls import url

from .views import UserSelectionView, \
    UserDetailView, UserGradebookSelect, gradebook_view, \
    assignments_view, student_view, create_standout

DATE_RE = '\d{4}\-\d{2}\-\d{2}'
gross_url_re = 'assignments/(?P<student_id>\d+)/(?P<gradebook_id>\d+)/' + \
        f'(?P<start_date>{DATE_RE})/(?P<end_date>{DATE_RE})/' + \
        '(?P<category_id>\d+)/'

urlpatterns = [
    url('^$', UserSelectionView.as_view(), name="user_select"),
    url('standout/$', create_standout, name="create_standout"),
    url('student/(?P<student_id>\d+)/$', student_view, name="student_view"),
    url('user/(?P<pk>\d+)/$', UserDetailView.as_view(), name="user_detail"),
    url('user/(?P<user_id>\d+)/gradebooks/$',
        UserGradebookSelect.as_view(),
        name="user_gb_select"),
    url('gradebook/(?P<gradebook_id>\d+)/$', gradebook_view, name="gradebook_detail"),
    url(gross_url_re, assignments_view, name="assignments_detail")
]