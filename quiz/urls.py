# quiz/urls.py
from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('create/lecture/<int:lecture_id>/', views.create_quiz, name='create_quiz'),  # Pass lecture_id directly
    path('<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/results/', views.manage_quiz_results, name='manage_results'),
    path('<int:quiz_id>/delete/', views.delete_quiz, name="delete_quiz"),
]
