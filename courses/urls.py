from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("",views.course_list, name="course_list"),
    path("create/",views.create_course,name="create_course"),
    path("enroll/<int:course_id>/",views.enroll_course,name="enroll_course"),
    path("unenroll/<int:course_id>/",views.unenroll_course,name="unenroll_course"),
]


