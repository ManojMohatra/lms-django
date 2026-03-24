from django.db import models
from django.contrib.auth.models import User
from courses.models import Lecture
from django.db.models import Sum

class Quiz(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="quizzes",null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return f"{self.title} - {self.lecture.title}"
    @property
    def total_points(self):
        return self.questions.aggregate(total=Sum('max_points'))['total'] or 0

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('PARA', 'Paragraph'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    max_points = models.IntegerField(default=1)
    question_type = models.CharField(max_length=4, choices=QUESTION_TYPES)
    
    # MCQ Fields: Nullable to accommodate Paragraph questions
    option_1 = models.CharField(max_length=255, blank=True, null=True)
    option_2 = models.CharField(max_length=255, blank=True, null=True)
    option_3 = models.CharField(max_length=255, blank=True, null=True)
    option_4 = models.CharField(max_length=255, blank=True, null=True)
    
    # Logic: Stores '1'-'4' for MCQs or the answer key for Paragraphs
    correct_answer = models.TextField()

    def __str__(self):
        return f"{self.question_type}: {self.text[:50]}"

class QuizSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    is_graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score})"
    

class StudentAnswer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    points_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer by {self.submission.student.username} to {self.question.text[:20]}"
    