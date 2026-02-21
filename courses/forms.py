from django import forms
from .models import Course,Assignment,Submission

class CourseForm(forms.ModelForm):
    class Meta:
        model=Course
        fields=["title","description"]


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

