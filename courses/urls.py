from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("",views.course_list, name="course_list"),
    path("create/",views.create_course,name="create_course"),
    path("enroll/<int:course_id>/",views.enroll_course,name="enroll_course"),
    path("unenroll/<int:course_id>/",views.unenroll_course,name="unenroll_course"),
    path("<int:course_id>",views.course_detail,name="course_detail"),
    path("edit/<int:course_id>",views.edit_course,name="edit_course"),
    path("lecture/<int:lecture_id>",views.lecture_detail,name="lecture_detail"),
    path("<int:course_id>/add-module/",views.add_module, name="add_module"),
    path("module/<int:module_id>/add-lecture/",views.add_lecture,name="add_lecture"),
    path("module/<int:module_id>/edit/",views.edit_module,name="edit_module"),
    path("module/<int:module_id>/delete",views.delete_module,name="delete_module"),
    path("lecture/<int:lecture_id>/edit/",views.edit_lecture,name="edit_lecture"),
    path("lecture/<int:lecture_id>/delete/",views.delete_lecture,name="delete_lecture"),
    path("course/<int:course_id>/delete/",views.delete_course,name="delete_course"),
    path('lecture/<int:lecture_id>/assignment/create/',  views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path("assignment/<int:assignment_id>/review/", views.review_assignment, name="review_assignment"),
    path("submission/<int:submission_id>/grade/", views.grade_submission, name="grade_submission"),
    path('<int:course_id>/analytics/', views.course_analytics, name='course_analytics'),
]


