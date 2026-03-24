# quiz/urls.py
from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    # Teacher: Quiz Management
    path('create/lecture/<int:lecture_id>/', views.create_quiz, name='create_quiz'),  # Pass lecture_id directly
    path('<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('<int:quiz_id>/delete/', views.delete_quiz, name="delete_quiz"),

   # Student: Taking Quiz & Viewing Result
    path('<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('result/<int:submission_id>/', views.quiz_result, name='quiz_result'),

    # Teacher: Grading & Results List
    path('<int:quiz_id>/results/', views.manage_quiz_results, name='manage_results'),
    path('grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),

]

