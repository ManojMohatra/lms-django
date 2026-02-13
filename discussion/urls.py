from django.urls import path
from . import views

app_name = "discussion"

urlpatterns = [
    path("course/<int:course_id>/", views.course_discussion, name="course_discussion"),
]
