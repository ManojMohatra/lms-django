from django import forms
from .models import Course, Assignment, Submission, Tag, Review
from django.utils.translation import gettext_lazy as _

class CourseForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Topics"),
        help_text=_("Select all topics that apply.")
    )

    class Meta:
        model = Course
        fields = ["title", "description", "thumbnail", "difficulty", "tags", "language", "is_free", "price"]
        labels = {
            "title": _("Course Title"),
            "description": _("Description"),
            "thumbnail": _("Thumbnail Image"),
            "difficulty": _("Difficulty Level"),
            "language": _("Language"),
            "is_free": _("Is this course free?"),
            "price": _("Price"),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "difficulty": forms.Select(attrs={"class": "form-select"}),
            "language": forms.TextInput(attrs={"placeholder": _("e.g. English"), "class": "form-control"}),
            "price": forms.NumberInput(attrs={"placeholder": "0.00", "min": "0", "step": "0.01", "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        is_free = cleaned.get("is_free")
        price = cleaned.get("price")

        # Logical validation for pricing
        if is_free and price and price > 0:
            self.add_error('price', _("A free course should not have a price."))
        
        if not is_free and (price is None or price <= 0):
            self.add_error('price', _("A paid course must have a price greater than zero."))
            
        return cleaned


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date"]
        labels = {
            "title": _("Assignment Title"),
            "description": _("Instructions"),
            "due_date": _("Deadline"),
        }
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["file"]
        labels = {
            "file": _("Upload File"),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        labels = {
            "rating": _("Your Rating"),
            "comment": _("Share your thoughts"),
        }
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": _("Write your review here..."), "class": "form-control"}),
        }