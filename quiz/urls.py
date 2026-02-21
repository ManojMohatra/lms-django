from django.urls import path
from . import views

app_name = "quiz"

urlpatterns = [
    # Teacher Routes: Creating and building quizzes
    path('course/<int:course_id>/create/', views.create_quiz, name='create_quiz'),
    path('<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    
    # Student Routes: Taking the quiz and viewing results
    path('<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<int:quiz_id>/results/', views.manage_quiz_results, name='manage_results'),
]