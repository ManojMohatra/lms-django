from django.urls import path
from . import views

app_name = "discussion"

urlpatterns = [
    path("course/<int:course_id>/", views.course_discussion, name="course_discussion"),
    path("delete/<int:comment_id>/",views.delete_comment,name="delete_comment"),
    path("edit/<int:comment_id>/",views.edit_comment,name="edit_comment"),
]
