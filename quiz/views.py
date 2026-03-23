from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from courses.models import Course, Enrollment, Lecture
from .models import Quiz, Question, QuizSubmission,StudentAnswer
from django.db.models import Sum
from django.contrib import messages
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
        max_pts = int(request.POST.get('max_points', 1))
        Question.objects.create(
            quiz=quiz,
            text=request.POST.get('text'),
            question_type=q_type,
            max_points=int(max_pts),
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
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.lecture.module.course
    is_teacher = (request.user == quiz.lecture.module.course.teacher)
    if request.user == course.teacher:
        if request.method == "POST":
            return HttpResponseForbidden("Teachers cannot submit attempts for their own quizzes.")
        
        return render(request, "quiz/take_quiz.html", {
            "quiz": quiz,
            "is_teacher": True 
        })
    existing_submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
    if existing_submission:
        # If they already submitted, send them straight to their result
        return redirect('quiz:quiz_result', submission_id=existing_submission.id)
    
    if request.method == "POST":
        submission = QuizSubmission.objects.create(
            student=request.user,
            quiz=quiz,
            score=0,
            is_graded=False

        )

        total_mcq_score = 0
        for q in quiz.questions.all():
            ans_text = request.POST.get(f"q_{q.id}", "").strip()
            points = 0
            if q.question_type == "MCQ":
                # Auto-grade MCQ
                if str(ans_text).strip() == str(q.correct_answer).strip():
                    points = q.max_points  
                total_mcq_score += points

            # Save the student's answer
            StudentAnswer.objects.create(
                submission=submission,
                question=q,
                answer_text=ans_text,
                points_earned=points
            )

        submission.score = total_mcq_score
        if not quiz.questions.filter(question_type="PARA").exists():
            submission.is_graded = True
        submission.save()

        return redirect("quiz:quiz_result", submission_id=submission.id)

    return render(request, "quiz/take_quiz.html", {"quiz": quiz,"is_teacher":is_teacher})

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
def grade_submission(request, submission_id):
    submission = get_object_or_404(QuizSubmission, id=submission_id)
    quiz = submission.quiz
    course = quiz.lecture.module.course

    if request.user.profile.role != "teacher" or course.teacher != request.user:
        return HttpResponseForbidden("Access Denied.")

    para_answers = submission.answers.filter(question__question_type="PARA")

    if request.method == "POST":
        for ans in para_answers:       
          points_str = request.POST.get(f"points_{ans.id}")
          if points_str is not None and points_str.strip() != "":
                try:
                    ans.points_earned = int(points_str)
                    ans.save()
                except ValueError:
                    # Ignore invalid inputs (like if the teacher typed "five" instead of 5)
                    pass

        # Update total score
        total = submission.answers.aggregate(total=Sum('points_earned'))['total'] or 0
        
        submission.score = total
        submission.is_graded = True
        submission.save()

        messages.success(request, f"Grades for {submission.student.username} have been updated successfully!")
        return redirect("quiz:manage_results", quiz_id=quiz.id)

    return render(request, "quiz/grade_submission.html", {
        "submission": submission,
        "para_answers": para_answers
    })

@login_required
def quiz_result(request, submission_id):
    submission = get_object_or_404(QuizSubmission, id=submission_id,student=request.user)
    quiz = submission.quiz
    answers = submission.answers.select_related('question').all()
    total_possible_score =quiz.questions.aggregate(total=Sum('max_points'))['total'] or 0
    return render(request, "quiz/result.html", {
        "submission": submission,
        "answers": answers,
        "total": total_possible_score
    })
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
