from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("course/<int:course_id>/", views.course_chat, name="course_chat"),
]
