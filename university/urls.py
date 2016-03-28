from django.conf.urls import url

from . import views

app_name = 'university'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<university_id>[0-9]+)/$', views.FacultiesView.as_view(), name='faculties'),
    url(r'^(?P<university_id>[0-9]+)/(?P<faculty_id_chose>[0-9]+)/$', views.FacultyIndicatorsView.as_view(), name='facultyIndicators'),

]

