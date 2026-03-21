from django import forms
from .models import Course,Assignment,Submission,Review

class CourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=["title","description","thumbnail"]

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control' 
            }),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]