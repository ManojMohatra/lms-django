from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from courses.models import Course, Enrollment, Lecture
from .models import Quiz, Question, QuizSubmission

@login_required
def create_quiz(request, lecture_id):  # ← Make sure this says lecture_id, not course_id
    """Allows teachers to initiate a new quiz for a specific lecture."""
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.module.course
    
    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("Only the course teacher can create quizzes.")
    
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        # Link the quiz to the lecture
        quiz = Quiz.objects.create(lecture=lecture, title=title, description=description)
        return redirect('quiz:add_question', quiz_id=quiz.id)
    
    return render(request, 'quiz/create_quiz.html', {'lecture': lecture, 'course': course})
@login_required
def add_question(request, quiz_id):
    """Allows teachers to add MCQ or Paragraph questions to a quiz."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.lecture.module.course
    
    if course.teacher != request.user:
        return HttpResponseForbidden("Permission denied.")
    
    if request.method == "POST":
        q_type = request.POST.get('type')
        Question.objects.create(
            quiz=quiz,
            text=request.POST.get('text'),
            question_type=q_type,
            option_1=request.POST.get('opt1') if q_type == 'MCQ' else None,
            option_2=request.POST.get('opt2') if q_type == 'MCQ' else None,
            option_3=request.POST.get('opt3') if q_type == 'MCQ' else None,
            option_4=request.POST.get('opt4') if q_type == 'MCQ' else None,
            correct_answer=request.POST.get('correct')
        )
        
        if "another" in request.POST:
            return redirect('quiz:add_question', quiz_id=quiz.id)
        # Redirect back to the lecture detail view
        return redirect('courses:lecture_detail', lecture_id=quiz.lecture.id)
    
    return render(request, 'quiz/add_question.html', {'quiz': quiz})

@login_required
def take_quiz(request, quiz_id):
    """Handles student quiz attempts with debug logging for score issues."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.lecture.module.course
    
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not is_enrolled and course.teacher != request.user:
        return HttpResponseForbidden("You must be enrolled to take this quiz.")
    
    if request.method == "POST":
        score = 0
        questions = quiz.questions.all()
        
        print("\n" + "="*30)
        print(f"GRADING QUIZ: {quiz.title}")
        
        for q in questions:
            user_ans = request.POST.get(f'q_{q.id}')
            db_ans = str(q.correct_answer).strip()
            submitted_ans = str(user_ans).strip() if user_ans else "NONE"
            print(f"DEBUG: Question ID {q.id}")
            print(f"DEBUG: Student picked: '{submitted_ans}'")
            print(f"DEBUG: Correct Answer in DB: '{db_ans}'")
            
            if q.question_type == 'MCQ':
                if submitted_ans == db_ans:
                    print("DEBUG: Result -> MATCH!")
                    score += 1
                else:
                    print("DEBUG: Result -> NO MATCH")
        
        print(f"FINAL SCORE: {score}")
        print("="*30 + "\n")
        
        QuizSubmission.objects.create(student=request.user, quiz=quiz, score=score)
        return render(request, 'quiz/result.html', {'score': score, 'total': questions.count(), 'quiz': quiz})
    
    return render(request, 'quiz/take_quiz.html', {'quiz': quiz})

@login_required
def manage_quiz_results(request, quiz_id):
    """Allows teachers to view all student submissions."""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.lecture.module.course
    
    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("Access Denied.")
    
    submissions = QuizSubmission.objects.filter(quiz=quiz).order_by('-submitted_at')
    return render(request, 'quiz/manage_results.html', {'quiz': quiz, 'submissions': submissions})

@login_required
# REMOVE @require_POST here
def delete_quiz(request, quiz_id):
    # Ensure the ID in the URL matches the variable name 'quiz_id'
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Permission check
    if quiz.lecture.module.course.teacher != request.user:
        return HttpResponseForbidden("You are not allowed to delete this quiz")
    
    if request.method == "POST":
        lecture_id = quiz.lecture.id
        quiz.delete()
        # Redirect back to the lecture detail page
        return redirect("courses:lecture_detail", lecture_id=lecture_id)
    
    # If GET, show the confirmation page
    return render(request, "quiz/delete_quiz.html", {"quiz": quiz})
