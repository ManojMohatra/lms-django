from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("",views.course_list, name="course_list"),
    path("create/",views.create_course,name="create_course"),
    path("enroll/<int:course_id>/",views.enroll_course,name="enroll_course"),
    path("unenroll/<int:course_id>/",views.unenroll_course,name="unenroll_course"),
    path("my-courses/",views.my_courses,name="my_courses"),
    path("<int:course_id>",views.course_detail,name="course_detail"),
    path("edit/<int:course_id>",views.edit_course,name="edit_course"),
    path("lecture/<int:lecture_id>",views.lecture_detail,name="lecture_detail"),
    path("<int:course_id>/add-module/",views.add_module, name="add_module"),
    path("module/<int:module_id>/add-lecture/",views.add_lecture,name="add_lecture"),
]


