from django.urls import path
from .import views

app_name = "materials"

urlpatterns = [
    path("<int:course_id>/", views.material_list, name="material_list"),
    path("<int:course_id>/add/", views.add_material, name="add_material"),
]
