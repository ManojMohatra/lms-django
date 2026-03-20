from django import forms
from .models import Course, Assignment, Submission, Tag


class CourseForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select all topics that apply."
    )

    class Meta:
        model  = Course
        fields = ["title", "description", "thumbnail", "difficulty", "tags", "language", "is_free", "price"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
            "language": forms.TextInput(attrs={"placeholder": "e.g. English"}),
            "price": forms.NumberInput(attrs={"placeholder": "0.00", "min": "0", "step": "0.01"}),
        }

    def clean(self):
        cleaned = super().clean()
        is_free = cleaned.get("is_free")
        price   = cleaned.get("price")

        if is_free and price:
            raise forms.ValidationError("A free course should not have a price.")
        if not is_free and not price:
            raise forms.ValidationError("A paid course must have a price.")
        return cleaned


class AssignmentForm(forms.ModelForm):
    class Meta:
        model  = Assignment
        fields = ["title", "description", "due_date"]
        widgets = {
            "due_date":    forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model  = Submission
        fields = ["file"]
