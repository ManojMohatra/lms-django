from django.urls import path
from . import views

app_name= "materials"
urlpatterns = [
    path('lecture/<int:lecture_id>/materials/', views.lecture_materials, name='lecture_materials'),
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'),
]
