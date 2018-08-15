from django.conf.urls import url

from .views import UserSelectionView, UserDetailView, UserGradebookSelect
urlpatterns = [
    url('^$', UserSelectionView.as_view(), name="user_select"),
    url('user/(?P<pk>\d+)/$', UserDetailView.as_view(), name="user_detail"),
    url('user/(?P<user_id>\d+)/gradebooks/$', UserGradebookSelect.as_view(),
        name="user_gb_select")
]